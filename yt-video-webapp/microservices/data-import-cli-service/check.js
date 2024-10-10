const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse');
const { PrismaClient } = require('@prisma/client');
const { createObjectCsvWriter } = require('csv-writer');
const cliProgress = require('cli-progress');

const prisma = new PrismaClient();

async function main() {
    try {
        // Query the database for the record with yt_video_id = 'fa1ArJopESk'
        const video = await prisma.video.findUnique({
            where: {
                yt_video_id: 'a74Zav1Z6z4',
            },
        });

        if (video) {
            console.log('Video found:', video);
        } else {
            console.log('No video found with yt_video_id = fa1ArJopESk');
        }
    } catch (error) {
        console.error('Error querying the database:', error);
    } finally {
        // Disconnect Prisma Client
        await prisma.$disconnect();
    }
}

main();
