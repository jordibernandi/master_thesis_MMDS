// Seed file for Prisma schema

const { PrismaClient } = require('@prisma/client');

const pc = new PrismaClient();

async function main() {
    // Create two channels
    const channel1 = await pc.channel.create({
        data: {
            yt_channel_id: 'channel_id_1',
            name: 'Channel 1',
            ideology: 'ANTI_SJW', // or any other ideology
            lr: 'LEFT',
        },
    });

    const channel2 = await pc.channel.create({
        data: {
            yt_channel_id: 'channel_id_2',
            name: 'Channel 2',
            ideology: 'LGBT', // or any other ideology
            lr: 'RIGHT',
        },
    });

    // Create 3500000 videos
    for (let i = 0; i < 3500000; i++) {
        const video = await pc.video.create({
            data: {
                yt_video_id: `video_id_${i}`,
                title: `Video ${i}`,
                description: `Description for video ${i}`,
                publish_date: new Date(),
                channel_id: (i % 2) == 0 ? channel1.id : channel2.id, // Assign videos to channels alternatively
            },
        });

        // Create 5 transcripts and 2 speakers for each video
        for (let j = 0; j < 5; j++) {
            const speaker1 = await pc.speaker.create({
                data: {
                    name: `Speaker ${j + 1}`,
                    video_id: video.id,
                },
            });

            const speaker2 = await pc.speaker.create({
                data: {
                    name: `Speaker ${j + 6}`, // To ensure two different speakers
                    video_id: video.id,
                },
            });

            await pc.transcript.createMany({
                data: [
                    {
                        start_time: '00:00:00',
                        end_time: '00:00:10',
                        text: `Transcript ${j + 1} for video ${i}`,
                        video_id: video.id,
                        speaker_id: speaker1.id,
                        last_updated: new Date(),
                    },
                    {
                        start_time: '00:00:10',
                        end_time: '00:00:20',
                        text: `Transcript ${j + 6} for video ${i}`, // To ensure two different speakers
                        video_id: video.id,
                        speaker_id: speaker2.id,
                        last_updated: new Date(),
                    },
                ],
            });
        }
    }
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await pc.$disconnect();
    });
