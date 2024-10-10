"use server"

import InfoWrapper from "@/components/singleVideo/InfoWrapper";
import TranscriptWrapper from "@/components/singleVideo/TranscriptWrapper";
import { getVideoWithDetails } from "@/data/video";
import HeaderWrapper from "@/components/singleVideo/HeaderWrapper";
import { VideoWithDetails } from "@/lib/types";
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"

const SingleVideoPage = async ({ params }: any) => {
    const { slug } = params;

    const video: VideoWithDetails | null = await getVideoWithDetails(slug);

    return (
        <div className="grow relative">
            <div className="absolute inset-0 flex">
                <div className="min-h-0 grow">
                    <div className="h-full">
                        <ResizablePanelGroup direction="horizontal">
                            <ResizablePanel defaultSize={25} className="pr-4 !overflow-y-auto">
                                <InfoWrapper video={video} />
                            </ResizablePanel>
                            <ResizableHandle withHandle />
                            <ResizablePanel defaultSize={75} className="pl-4 !overflow-y-auto">
                                <div className="flex flex-col gap-4">
                                    <HeaderWrapper video={video} />
                                    <TranscriptWrapper transcripts={video?.transcripts ?? []} />
                                </div>
                            </ResizablePanel>
                        </ResizablePanelGroup>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default SingleVideoPage;
