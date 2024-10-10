const fs = require('fs');
const path = require('path');
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
            { id: 'YT_VIDEO_ID', title: 'YT_VIDEO_ID' },
            { id: 'ERROR', title: 'ERROR' }
        ],
        append: true
    });

    if (!fileExists) {
        await csvWriter.writeRecords([error]);
    } else {
        const data = fs.readFileSync(filePath, 'utf8');
        const rows = data.split('\n').filter(row => row).map(row => row.split(','));
        const ids = rows.map(row => row[1]);

        if (!ids.includes(error.YT_VIDEO_ID)) {
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
    const folderPath = '../../../thesis_data/result_audio_files_AFTER_COVID_large-v3'; // Replace with your folder path
    const processedFilesLogPath = './processed_files_import_transcripts_log.csv';

    const processedFiles = await getProcessedFiles(processedFilesLogPath);

    const files = fs.readdirSync(folderPath).filter(file => file.endsWith('.json') && !processedFiles.includes(file));

    const fileBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
    fileBar.start(files.length, 0);

    for (const file of files) {
        const filePath = path.join(folderPath, file);
        const transcripts = [];

        try {
            let data = fs.readFileSync(filePath, 'utf8');

            // Remove any BOM or unexpected characters at the beginning of the file
            if (data.charCodeAt(0) === 0xFEFF) {
                data = data.slice(1);
            }

            try {
                const jsonContent = JSON.parse(data);

                const { yt_video_id, transcripts: transcriptArray } = jsonContent;

                // Delete existing transcripts for the yt_video_id
                await prisma.transcript.deleteMany({
                    where: { yt_video_id }
                });

                transcriptArray.forEach((transcript, index) => {
                    const { start_time, end_time, text, speaker } = transcript;
                    const speaker_name = speaker?.name || 'Unknown';

                    transcripts.push({
                        yt_video_id,
                        order: index + 1,
                        start_time,
                        end_time,
                        text: text.trim(),
                        speaker_name
                    });
                });

                const transcriptBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
                transcriptBar.start(transcripts.length, 0);

                for (const transcript of transcripts) {
                    try {
                        await prisma.transcript.create({
                            data: transcript,
                        });
                    } catch (error) {
                        await appendErrorLog("./error_import_transcripts_log.csv", { FILE_NAME: file, YT_VIDEO_ID: transcript.yt_video_id, ERROR: error.message });
                        console.error(`Failed to insert transcript for video ID: ${transcript.yt_video_id}`);
                        console.error(error);
                    }
                    transcriptBar.increment();
                }

                transcriptBar.stop();
                console.log(`Inserted ${transcripts.length} transcripts from ${file}`);
                fileBar.increment();
                await appendProcessedFileLog(processedFilesLogPath, file); // Log processed file

            } catch (jsonError) {
                console.error(`Invalid JSON in file ${filePath}:`, jsonError);
                await appendErrorLog("./error_import_transcripts_log.csv", { FILE_NAME: file, YT_VIDEO_ID: '', ERROR: jsonError.message });
            }
        } catch (error) {
            console.error(`Error reading file ${filePath}: `, error);
            await appendErrorLog("./error_import_transcripts_log.csv", { FILE_NAME: file, YT_VIDEO_ID: '', ERROR: error.message });
        }
    }

    fileBar.stop();
}

main()
    .catch(e => console.error(e))
    .finally(async () => {
        await prisma.$disconnect();
    });
