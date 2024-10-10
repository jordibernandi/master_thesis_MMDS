"use client"

import Link from "next/link";
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import type { Video } from '@prisma/client'
import ItemWrapper from "./ItemWrapper";
import { VideoWithChannel } from "@/lib/types";

interface ListWrapperProps {
    videos: VideoWithChannel[]
}

const ListWrapper = ({ videos }: ListWrapperProps) => {
    return (
        <ScrollArea className="h-[1px] flex-grow w-full rounded-md border p-4 overflow-y-auto">
            {videos && videos.map((entry: VideoWithChannel) => (
                <ItemWrapper key={entry.id} video={entry} />
            ))}
        </ScrollArea>
    );
}

export default ListWrapper;