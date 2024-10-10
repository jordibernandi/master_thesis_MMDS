"use client"

import { FiDownload } from "react-icons/fi";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import exportFromJSON, { ExportType } from 'export-from-json'
import { Button } from "@/components/ui/button";
import { VideoWithDetails, VideoWithDetailsNoDiarization } from "@/lib/types";
import { useRouter, useSearchParams } from "next/navigation";
import { Switch } from "@/components/ui/switch";
import { useState } from "react";
import { Label } from "@/components/ui/label";

interface HeaderWrapperProps {
    video: VideoWithDetails | VideoWithDetailsNoDiarization | null
}

const HeaderWrapper = ({ video }: HeaderWrapperProps) => {
    const router = useRouter();
    const searchParams = useSearchParams();

    const paramShowDiarization = searchParams.get("showDiarization") ?? "";

    const exportVideos = (exportType: ExportType, diarization: boolean) => () => {
        let transcriptText = '';

        let data = video as VideoWithDetails | VideoWithDetailsNoDiarization;

        if (!diarization) {
            (data as VideoWithDetails).transcripts.forEach((transcript) => {
                transcriptText += transcript.text + ' ';
            });
            transcriptText = transcriptText.trim();

            (data as VideoWithDetailsNoDiarization).transcripts = transcriptText;
        }

        const fileName = 'video'
        exportFromJSON({ data, fileName, exportType })
    }

    return (
        <div className="flex flex-row justify-between items-center h-8">
            <Button variant="secondary">
                <a onClick={() => {
                    router.push('/video');
                }}>
                    List Videos
                </a>
            </Button>
            <div className="flex flex-row items-center gap-4">
                <div className="flex items-center space-x-2">
                    <Switch id="show-diarization" checked={paramShowDiarization ? true : false} onCheckedChange={() => {
                        if (!paramShowDiarization) {
                            router.push(`/video/${video?.yt_video_id}?showDiarization=true`);
                        } else {
                            router.push(`/video/${video?.yt_video_id}`);
                        }
                    }} />
                    <Label htmlFor="show-diarization">Show Diarization</Label>
                </div>
                <DropdownMenu>
                    <DropdownMenuTrigger>
                        <FiDownload className="cursor-pointer" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-40" align="end">
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.json, false)}>
                            JSON
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.xml, false)}>
                            XML
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.csv, false)}>
                            CSV
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.json, true)}>
                            JSON - Diarization
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.xml, true)}>
                            XML - Diarization
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={exportVideos(exportFromJSON.types.csv, true)}>
                            CSV - Diarization
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </div>
    );
}

export default HeaderWrapper;