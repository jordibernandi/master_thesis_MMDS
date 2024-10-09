import { Prisma } from "@prisma/client";

export type VideoWithChannel = Prisma.VideoGetPayload<{
    include: {
        channel: true,
    },
}>

export type VideoWithDetails = Prisma.VideoGetPayload<{
    include: {
        transcripts: true,
        channel: true,
    },
}>

export type VideoWithDetailsNoDiarization = Omit<VideoWithDetails, 'transcripts'> & {
    transcripts: string; // Replacing transcripts array with concatenatedTranscripts string
};

export type TranscriptWithDetails = Prisma.TranscriptGetPayload<{}>

export type Sort = null | 'OLD' | 'NEW' | 'LOW' | 'HIGH';
