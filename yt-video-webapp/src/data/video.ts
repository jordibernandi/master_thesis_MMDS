import { db } from "@/lib/db";
import { Sort, VideoWithChannel, VideoWithDetails, VideoWithDetailsNoDiarization } from "@/lib/types";
import { Ideology, LR } from "@prisma/client";

const buildWhereClause = (
    query: string,
    ideologies: Ideology[],
    lrs: LR[],
    relevance: number[],
    start: string,
    end: string,
    hasTranscript: boolean
): object => {
    const hasQuery = query.trim().length > 0;
    const hasIdeologies = ideologies.length > 0;
    const hasLrs = lrs.length > 0;
    const hasRelevance = relevance.length > 0;
    const hasStart = start.length > 0;
    const hasEnd = end.length > 0;

    const conditions: any[] = [];

    if (hasQuery) {
        conditions.push({
            OR: [
                { title: { startsWith: query, mode: 'insensitive' } },
                { description: { startsWith: query, mode: 'insensitive' } },
                { keywords: { has: query } }
            ]
        });
    }

    if (hasIdeologies) {
        conditions.push({
            channel: {
                ideology: {
                    in: ideologies
                }
            }
        });
    }

    if (hasLrs) {
        conditions.push({
            channel: {
                lr: {
                    in: lrs
                }
            }
        });
    }

    if (hasRelevance) {
        conditions.push({
            channel: {
                relevance: {
                    gte: relevance[0],
                    lte: relevance[1]
                }
            }
        });
    }

    const startDate = new Date(start);
    const endDate = new Date(end);
    const isValidStartDate = !isNaN(startDate.getTime());
    const isValidEndDate = !isNaN(endDate.getTime());

    if (isValidEndDate) {
        endDate.setHours(23, 59, 59, 999);
    }

    if (hasStart && hasEnd && isValidStartDate && isValidEndDate) {
        conditions.push({
            publish_date: {
                gte: startDate.toISOString(),
                lte: endDate.toISOString()
            }
        });
    } else if (hasStart && isValidStartDate) {
        conditions.push({
            publish_date: {
                gte: startDate.toISOString()
            }
        });
    } else if (hasEnd && isValidEndDate) {
        conditions.push({
            publish_date: {
                lte: endDate.toISOString()
            }
        });
    }

    if (hasTranscript) {
        conditions.push({
            transcripts: {
                some: {}
            }
        });
    }

    return {
        AND: conditions
    };
};

const buildOrderByClause = (sort: Sort): object => {
    let orderBy = {}

    switch (sort) {
        case "OLD":
            orderBy = [
                { publish_date: 'asc' },
                { yt_video_id: 'asc' }
            ]
            break;
        case "NEW":
            orderBy = [
                { publish_date: 'desc' },
                { yt_video_id: 'asc' }
            ]
            break;
        case "LOW":
            orderBy = [
                {
                    channel: {
                        relevance: 'asc'
                    }
                },
                { yt_video_id: 'asc' }
            ]
            break;
        case "HIGH":
            orderBy = [
                {
                    channel: {
                        relevance: 'desc'
                    }
                },
                { yt_video_id: 'asc' }
            ]
            break;
        default:
            orderBy = { yt_video_id: 'asc' }
            break;
    }
    return orderBy;
}

export const getAllVideos = async (
    query: string,
    ideologies: Ideology[],
    lrs: LR[],
    relevance: number[],
    start: string,
    end: string,
    hasTranscript: boolean,
    page: number,
    pageSize: number,
    sort: Sort
): Promise<{ videos: VideoWithChannel[]; totalVideos: number } | null> => {
    try {
        const whereClause = buildWhereClause(query, ideologies, lrs, relevance, start, end, hasTranscript);

        const skip = (page - 1) * pageSize;
        const take = pageSize;

        const orderByClause = buildOrderByClause(sort);

        const videos = await db.video.findMany({
            where: whereClause,
            include: {
                channel: true,
            },
            skip,
            take,
            orderBy: orderByClause
        });

        const totalVideos = await db.video.count({
            where: whereClause
        });

        return { videos, totalVideos };
    } catch (error) {
        console.log("ERROR", error);
        return null;
    }
};

export const getAllVideosExport = async (
    query: string,
    ideologies: Ideology[],
    lrs: LR[],
    relevance: number[],
    start: string,
    end: string,
    hasTranscript: boolean,
    cursor: string | undefined,
    pageSize: number,
    sort: Sort,
    diarization: boolean
): Promise<(VideoWithDetails | VideoWithDetailsNoDiarization)[] | null> => {
    try {
        const whereClause = buildWhereClause(query, ideologies, lrs, relevance, start, end, hasTranscript);

        const orderByClause = buildOrderByClause(sort);

        const videos = await db.video.findMany({
            where: whereClause,
            include: {
                channel: true,
                transcripts: true
            },
            take: pageSize,
            cursor: cursor ? { yt_video_id: cursor } : undefined,
            skip: cursor ? 1 : 0,
            orderBy: orderByClause
        });

        if (!diarization) {
            const noDiarizationVideos = videos.map(video => {
                let transcriptText = '';

                (video.transcripts as any[]).forEach((transcript) => {
                    transcriptText += transcript.text + ' ';
                });
                transcriptText = transcriptText.trim();

                return {
                    ...video,
                    transcripts: transcriptText
                } as VideoWithDetailsNoDiarization;
            });

            return noDiarizationVideos;
        } else {
            return videos;
        }

    } catch (error) {
        console.log("ERROR", error);
        return null;
    }
};

export const getVideoWithDetails = async (yt_video_id: string) => {
    try {
        const video = await db.video.findUnique({
            where: {
                yt_video_id: yt_video_id,
            },
            include: {
                transcripts: {
                    orderBy: {
                        order: 'asc',
                    },
                }, channel: true,
            },
        });

        return video;
    } catch (error) {
        return null;
    }
}

// db.$on('query' as never, (e: any) => {
//     console.log('Query: ' + e.query)
//     console.log('Params: ' + e.params)
//     console.log('Duration: ' + e.duration + 'ms')
// })