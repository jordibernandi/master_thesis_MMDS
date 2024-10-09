const fs = require('fs');
const csv = require('fast-csv');
const path = require('path');
const { PrismaClient, Ideology, LR } = require('@prisma/client'); // Adjust the path as necessary
const { MultiBar, Presets } = require('cli-progress');

const prisma = new PrismaClient();

// Mapping for lr values
const lrMapping = {
    'l': LR.LEFT,
    'r': LR.RIGHT,
    'c': LR.CENTER,
};

// Mapping for ideology values
const ideologyMapping = {
    'Anti-SJW': Ideology.ANTI_SJW,
    'QAnon': Ideology.QANON,
    'Conspiracy': Ideology.CONSPIRACY,
    'Religious Conservative': Ideology.RELIGIOUS_CONSERVATIVE,
    'Partisan Right': Ideology.PARTISAN_RIGHT,
    'Black': Ideology.BLACK,
    'LGBT': Ideology.LGBT,
    'Libertarian': Ideology.LIBERTARIAN,
    'Social Justice': Ideology.SOCIAL_JUSTICE,
    'Socialist': Ideology.SOCIALIST,
    'Partisan Left': Ideology.PARTISAN_LEFT,
    'MRA': Ideology.MRA,
    'Anti-theist': Ideology.ANTI_THEIST,
    'White Identitarian': Ideology.WHITE_IDENTITARIAN,
};

// Mapping for tags values
const tagsMapping = {
    'AntiSJW': Ideology.ANTI_SJW,
    'QAnon': Ideology.QANON,
    'Conspiracy': Ideology.CONSPIRACY,
    'ReligiousConservative': Ideology.RELIGIOUS_CONSERVATIVE,
    'PartisanRight': Ideology.PARTISAN_RIGHT,
    'Black': Ideology.BLACK,
    'LGBT': Ideology.LGBT,
    'Libertarian': Ideology.LIBERTARIAN,
    'SocialJustice': Ideology.SOCIAL_JUSTICE,
    'Socialist': Ideology.SOCIALIST,
    'PartisanLeft': Ideology.PARTISAN_LEFT,
    'MRA': Ideology.MRA,
    'AntiTheist': Ideology.ANTI_THEIST,
    'WhiteIdentitarian': Ideology.WHITE_IDENTITARIAN,
    'Politician': Ideology.POLITICIAN,
    'Educational': Ideology.EDUCATIONAL,
    'StateFunded': Ideology.STATE_FUNDED,
    'OrganizedReligion': Ideology.ORGANIZED_RELIGION,
};

async function main() {
    const channels = [];

    fs.createReadStream('../../../thesis_data/checked_channels_V2.csv')
        .pipe(csv.parse({ headers: true }))
        .on('data', (row) => {
            let tags = [];
            if (row.CHANNEL_TAGS) {
                try {
                    // Combine and parse the tags correctly
                    const tagString = row.CHANNEL_TAGS
                        .replace(/[\n\s]/g, '') // Remove newlines and spaces
                        .replace(/(^\[)|(\]$)/g, '') // Remove the leading and trailing square brackets
                        .split(',') // Split the string into an array
                        .map(tag => tag.replace(/^"|"$/g, '')) // Remove leading and trailing quotes from each tag
                        .map(tag => tagsMapping[tag] || tag); // Map to valid tags values
                    tags = tagString.filter(tag => Object.values(tagsMapping).includes(tag)); // Filter out invalid tags
                } catch (e) {
                    console.error('Error parsing tags:', e);
                }
            }

            const lr = lrMapping[row.CHANNEL_LR.toLowerCase()];
            if (!lr) {
                console.error(`Invalid LR value: ${row.CHANNEL_LR}`);
                return;
            }

            const ideology = ideologyMapping[row.CHANNEL_IDEOLOGY];
            if (!ideology) {
                console.error(`Invalid Ideology value: ${row.CHANNEL_IDEOLOGY}`);
                return;
            }
            channels.push({
                yt_channel_id: row.CHANNEL_ID,
                name: row.CHANNEL_TITLE,
                lr: lr,
                tags: tags,
                ideology: ideology,
                relevance: parseFloat(row.CHANNEL_RELEVANCE),
                country: row.CHANNEL_COUNTRY,
                logo_url: row.CHANNEL_LOGO_URL,
                from_date: new Date(row.CHANNEL_FROM_DATE),
            });
        })
        .on('end', async () => {
            console.log('CSV file successfully processed');

            // Create a new progress bar instance
            const multiBar = new MultiBar({
                format: '{bar} | {percentage}% | ETA: {eta_formatted} | {value}/{total}',
                clearOnComplete: false,
                hideCursor: true,
            }, Presets.shades_classic);

            const upsertBar = multiBar.create(channels.length, 0);

            // Insert channels into database
            for (let i = 0; i < channels.length; i++) {
                const channel = channels[i];
                await prisma.channel.upsert({
                    where: { yt_channel_id: channel.yt_channel_id },
                    update: channel,
                    create: channel,
                });

                // Update the progress bar
                upsertBar.update(i + 1);
            }

            // Stop the progress bar
            upsertBar.stop();
            multiBar.stop();

            console.log('All channels inserted');
        });
}

main()
    .catch((e) => {
        throw e;
    })
    .finally(async () => {
        await prisma.$disconnect();
    });