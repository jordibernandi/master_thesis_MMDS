"use server"

import { getAllVideosExport } from "@/data/video";
import { Sort } from "@/lib/types";
import { Ideology, LR } from "@prisma/client";

export const exportVideosAction = async (query: string, ideologies: Ideology[], lrs: LR[], relevance: number[], start: string, end: string, hasTranscript: boolean, cursor: string | undefined, pageSize: number, sort: Sort, diarization: boolean) => {

    return await getAllVideosExport(query, ideologies, lrs, relevance, start, end, hasTranscript, cursor, pageSize, sort, diarization);
}