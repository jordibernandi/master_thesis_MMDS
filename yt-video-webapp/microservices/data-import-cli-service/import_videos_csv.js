const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse');
const { PrismaClient } = require('@prisma/client');
const { createObjectCsvWriter } = require('csv-writer');
const cliProgress = require('cli-progress');

const prisma = new PrismaClient();

async function appendErrorLog(filePath, error) {
    const fileExists = fs.existsSync(filePath);

    const csvWriter = createObjectCsvWriter({
        path: filePath,
        header: [
            { id: 'FILE_NAME', title: 'FILE_NAME' },
            { id: 'VIDEO_ID', title: 'VIDEO_ID' },
            { id: 'VIDEO_TITLE', title: 'VIDEO_TITLE' }
        ],
        append: true
    });

    if (!fileExists) {
        await csvWriter.writeRecords([error]);
    } else {
        const data = fs.readFileSync(filePath, 'utf8');
        const rows = data.split('\n').filter(row => row).map(row => row.split(','));
        const ids = rows.map(row => row[1]);

        if (!ids.includes(error.VIDEO_ID)) {
            await csvWriter.writeRecords([error]);
        }
    }
}

async function appendProcessedFileLog(filePath, fileName) {
    const fileExists = fs.existsSync(filePath);

    const csvWriter = createObjectCsvWriter({
        path: filePath,
        header: [
            { id: 'FILE_NAME', title: 'FILE_NAME' }
        ],
        append: true
    });

    if (!fileExists) {
        await csvWriter.writeRecords([{ FILE_NAME: fileName }]);
    } else {
        const data = fs.readFileSync(filePath, 'utf8');
        const rows = data.split('\n').filter(row => row);
        const filenames = rows.map(row => row.split(',')[0]);

        if (!filenames.includes(fileName)) {
            await csvWriter.writeRecords([{ FILE_NAME: fileName }]);
        }
    }
}

async function getProcessedFiles(filePath) {
    const fileExists = fs.existsSync(filePath);

    if (!fileExists) {
        return [];
    }

    const data = fs.readFileSync(filePath, 'utf8');
    const rows = data.split('\n').filter(row => row);
    return rows.map(row => row.split(',')[0]);
}

async function main() {
    const folderPath = '../../../thesis_data/results_checked_thumbnail_url_old'; // Replace with your folder path
    const processedFilesLogPath = './processed_files_import_videos_log.csv';

    const processedFiles = await getProcessedFiles(processedFilesLogPath);

    const files = fs.readdirSync(folderPath).filter(file => file.endsWith('.csv') && !processedFiles.includes(file));

    const fileBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
    fileBar.start(files.length, 0);

    for (const file of files) {
        const filePath = path.join(folderPath, file);
        const videos = [];

        await new Promise((resolve, reject) => {
            fs.createReadStream(filePath)
                .pipe(parse({
                    columns: true,               // Generate records as objects
                    relax_column_count: true,    // Allow variable column counts
                    skip_empty_lines: true,      // Skip empty lines
                    trim: true,                  // Trim whitespaces around the delimiter
                    // on_record: (record, { lines }) => { // Custom function to track lines and handle multiline description
                    //     // Recombine multiline fields into a single field
                    //     if (lines.records === 0) {
                    //         record.VIDEO_DESCRIPTION = record.VIDEO_DESCRIPTION.replace(/\n/g, ' ');
                    //     } else {
                    //         record.VIDEO_DESCRIPTION += `\n${lines.source}`;
                    //     }
                    //     return record;
                    // }
                    // delimiter: ',',              // Define the field delimiter
                    // quote: '"',                  // Define the quote character
                    // escape: '\\'                 // Define the escape character
                }))
                .on('data', (row) => {
                    const {
                        CHANNEL_ID,
                        VIDEO_ID,
                        VIDEO_TITLE,
                        VIDEO_VIEWS,
                        VIDEO_PUBLISH_DATE,
                        VIDEO_DESCRIPTION,
                        VIDEO_KEYWORDS,
                        VIDEO_LENGTH,
                        VIDEO_THUMBNAIL_URL
                    } = row;

                    let keywords;
                    try {
                        keywords = VIDEO_KEYWORDS.replace(/^\[|\]$/g, '').replace(/'/g, '').split(',').map(keyword => keyword.trim());
                    } catch (error) {
                        console.error(`Error parsing keywords for video ${VIDEO_ID}:`, error);
                        keywords = [];
                    }

                    let publishDate = VIDEO_PUBLISH_DATE ? new Date(VIDEO_PUBLISH_DATE) : null;

                    videos.push({
                        yt_video_id: VIDEO_ID,
                        title: VIDEO_TITLE,
                        description: VIDEO_DESCRIPTION,
                        publish_date: publishDate,
                        keywords: keywords,
                        length: parseInt(VIDEO_LENGTH, 10),
                        views: parseInt(VIDEO_VIEWS, 10),
                        thumbnail_url: VIDEO_THUMBNAIL_URL,
                        yt_channel_id: CHANNEL_ID
                    });
                })
                .on('end', async () => {
                    console.log(`Finished processing ${file}`);

                    const videoBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
                    videoBar.start(videos.length, 0);

                    for (const video of videos) {
                        try {
                            await prisma.video.upsert({
                                where: { yt_video_id: video.yt_video_id },
                                update: video,
                                create: video,
                            });
                        } catch (error) {
                            await appendErrorLog("./error_import_videos_log.csv", { FILE_NAME: file, VIDEO_ID: video.yt_video_id, VIDEO_TITLE: video.title });
                            console.error(`Failed to insert video with ID: ${video.yt_video_id}`);
                            console.log(error);
                        }
                        videoBar.increment();
                    }

                    videoBar.stop();
                    console.log(`Inserted/Updated ${videos.length} videos from ${file}`);
                    fileBar.increment();
                    await appendProcessedFileLog(processedFilesLogPath, file); // Log processed file
                    resolve();
                })
                .on('error', (error) => {
                    console.error(`Error processing file ${filePath}: `, error);
                    reject(error);
                });
        });
    }

    fileBar.stop();
}

main()
    .catch(e => console.error(e))
    .finally(async () => {
        await prisma.$disconnect();
    });
