const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function dropTable() {
    try {
        // Drop the table using SQL command
        await prisma.$executeRaw('DROP TABLE "Video"');
        console.log('Table "Video" dropped successfully.');
    } catch (error) {
        console.error('Error dropping table:', error);
    } finally {
        await prisma.$disconnect();
    }
}

dropTable();