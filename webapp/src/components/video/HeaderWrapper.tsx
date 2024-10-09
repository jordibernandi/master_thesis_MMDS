"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useRef, useEffect } from 'react';
import { FiDownload } from "react-icons/fi";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { ProgressWithValue } from '@/components/ui/progress-with-value';
import exportFromJSON, { ExportType } from 'export-from-json';
import { Ideology, LR } from "@prisma/client";
import { exportVideosAction } from "@/actions/exportVideos";
import { configureFilter } from "@/lib/utils";
import { Sort } from "@/lib/types";

interface HeaderWrapperProps {
    totalVideos: number | null;
}

const HeaderWrapper = ({ totalVideos }: HeaderWrapperProps) => {
    const router = useRouter();
    const searchParams = useSearchParams();

    const [progress, setProgress] = useState(0);
    const [isExporting, setIsExporting] = useState(false);
    const [startTime, setStartTime] = useState<number | null>(null);
    const [estimatedTime, setEstimatedTime] = useState<string | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    const paramQuery = searchParams.get("query") ?? "";
    const paramIdeologies = searchParams.get("ideologies") ? (searchParams.get("ideologies") as String).split(',') : [];
    const paramLrs = searchParams.get("lrs") ? (searchParams.get("lrs") as String).split(',') : [];
    const paramRelevance = searchParams.get("relevance") ? searchParams.get("relevance")?.split(',').map(Number) : [];
    const paramStart = searchParams.get("start") ?? "";
    const paramEnd = searchParams.get("end") ?? "";
    const paramHasTranscript = searchParams.get("hasTranscript") ?? "";
    const paramSort = searchParams.get("sort") ?? "";

    useEffect(() => {
        return () => {
            // Cleanup function to abort the ongoing fetch when the component unmounts
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
                setIsExporting(false);
                setProgress(0);
                setEstimatedTime(null);
            }
        };
    }, []);

    const cancelExport = () => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setIsExporting(false);
            setProgress(0);
            setEstimatedTime(null);
        }
    };

    const exportVideos = (exportType: ExportType, diarization: boolean) => async () => {
        console.log("Export started");
        setIsExporting(true);
        setProgress(0);
        setStartTime(Date.now());
        setEstimatedTime(null);

        const pageSize = 1000;
        const total = totalVideos ?? 0;
        let cursor: string | undefined = undefined;
        let allVideos: any[] = [];

        abortControllerRef.current = new AbortController();
        const signal = abortControllerRef.current.signal;

        const fetchVideos = async () => {
            try {
                while (true) {
                    if (signal.aborted) {
                        console.log("Export cancelled");
                        break;
                    }

                    const videos = await exportVideosAction(
                        paramQuery as string,
                        paramIdeologies as Ideology[],
                        paramLrs as LR[],
                        paramRelevance as number[],
                        paramStart as string,
                        paramEnd as string,
                        paramHasTranscript ? true : false as boolean,
                        cursor,
                        pageSize,
                        paramSort as Sort,
                        diarization
                    );

                    if (videos && videos.length > 0) {
                        allVideos = allVideos.concat(videos);
                        cursor = videos[videos.length - 1].yt_video_id;
                        setProgress((prevProgress) => {
                            const newProgress = prevProgress + (videos.length / total) * 100;
                            updateEstimatedTime(newProgress);
                            return newProgress;
                        });
                    } else {
                        break;
                    }
                }
            } catch (error) {
                if (signal.aborted) {
                    console.log("Export cancelled");
                } else {
                    console.error("Export error", error);
                }
            } finally {
                abortControllerRef.current = null;
                setIsExporting(false);
            }
        };

        await fetchVideos();

        if (!signal.aborted) {
            const data = allVideos;
            const fileName = "videos";
            exportFromJSON({ data, fileName, exportType });
        }
    };

    const updateEstimatedTime = (newProgress: number) => {
        setStartTime((prevStartTime) => {
            if (prevStartTime !== null && newProgress > 0) {
                const elapsedTime = (Date.now() - prevStartTime) / 1000; // elapsed time in seconds
                const estimatedTotalTime = (elapsedTime / newProgress) * 100; // estimated total time in seconds
                const remainingTime = estimatedTotalTime - elapsedTime; // remaining time in seconds

                if (remainingTime > 0) {
                    setEstimatedTime(formatTime(remainingTime));
                } else {
                    setEstimatedTime(null);
                }
            }
            return prevStartTime;
        });
    };

    const formatTime = (seconds: number) => {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}m ${remainingSeconds}s`;
    };

    const formatNumber = (number: number | null) => {
        return new Intl.NumberFormat().format(number ?? 0);
    };

    return (
        <div className="flex flex-row justify-between items-center h-8">
            <span className="text-xl font-bold leading-9">{`${formatNumber(totalVideos)} Results`}</span>
            <div className="flex flex-row items-center gap-4">
                {isExporting && (
                    <div className="flex flex-row items-center gap-2">
                        <span className="text-xs">{estimatedTime ? `Fetching - Estimated time: ${estimatedTime}` : "Building..."}</span>
                        <ProgressWithValue value={Math.round(progress)} position="start-outside" className="w-40" />
                        <button
                            type="button"
                            className="text-xs font-medium text-gray-500 hover:text-red-600 focus:outline-none"
                            onClick={cancelExport}
                        >
                            &#10006; {/* This is the "X" character */}
                        </button>
                    </div>
                )}
                <Select value={paramSort} onValueChange={(value) => {
                    configureFilter(router, searchParams, value != "NONE" ? value : "", "SORT")()
                }}>
                    <SelectTrigger className="w-[120px]">
                        <SelectValue placeholder="Sort" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="NONE">None</SelectItem>
                        <SelectItem value="OLD">Old</SelectItem>
                        <SelectItem value="NEW">New</SelectItem>
                        <SelectItem value="LOW">Low</SelectItem>
                        <SelectItem value="HIGH">High</SelectItem>
                    </SelectContent>
                </Select>
                <DropdownMenu>
                    <DropdownMenuTrigger>
                        <FiDownload className="cursor-pointer" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-40" align="end">
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.json, false)} disabled={isExporting}>
                            JSON
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.xml, false)} disabled={isExporting}>
                            XML
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.csv, false)} disabled={isExporting}>
                            CSV
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.json, true)} disabled={isExporting}>
                            JSON - Diarization
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.xml, true)} disabled={isExporting}>
                            XML - Diarization
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.csv, true)} disabled={isExporting}>
                            CSV - Diarization
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </div >
    );
};

export default HeaderWrapper;
