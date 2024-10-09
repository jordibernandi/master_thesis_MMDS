"use client"

import { Separator } from "@/components/ui/separator"
import { TranscriptWithDetails } from "@/lib/types";
import { useSearchParams } from "next/navigation";

interface TranscriptWrapperProps {
    transcripts: TranscriptWithDetails[] | []
}

const TranscriptWrapper = ({ transcripts }: TranscriptWrapperProps) => {
    const searchParams = useSearchParams();

    const paramShowDiarization = searchParams.get("showDiarization") ?? "";

    let transcriptText = "";

    if (!paramShowDiarization) {
        transcripts.forEach((transcript => {
            transcriptText += transcript.text + ' ';
        }))
        transcriptText = transcriptText.trim();
    }

    return (
        <div className="flex flex-col gap-4">
            <Separator />

            {paramShowDiarization && transcripts.map(transcript => (
                <div key={transcript.id} className="flex flex-col gap-2">
                    <div className="flex flex-row justify-between items-center">
                        <span className="font-bold">{transcript.speaker_name}</span>
                        <span className="text-xs">{`[${transcript.start_time} - ${transcript.end_time}]`}</span>
                    </div>
                    <span>{transcript.text}</span>
                    <Separator />
                </div>
            ))}

            {!paramShowDiarization && transcriptText &&
                <div className="flex flex-col gap-2">
                    <span>{transcriptText}</span>
                    <Separator />
                </div>
            }

            {!transcripts && !transcriptText && (
                <div>No Data</div>
            )}
        </div>
    )
};

export default TranscriptWrapper;