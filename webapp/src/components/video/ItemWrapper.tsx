import { Video } from "@prisma/client";
import Image from "next/image";
import Link from "next/link";
import { Separator } from "../ui/separator";
import { formatDate, mapEnumIdeologyToDisplayValue, mapEnumLRToDisplayValue } from "@/lib/utils";
import { VideoWithChannel } from "@/lib/types";

interface ItemWrapperProps {
    video: VideoWithChannel;
}

const ItemWrapper = ({ video }: ItemWrapperProps) => {

    return (
        <Link key={video.id} href={`/video/${video.yt_video_id}`}>
            <div className="flex flex-row gap-4 p-2.5 hover:bg-gray-100 transition duration-300 ease-in-out">
                <div className="w-[120px] h-[90px] flex items-center justify-center overflow-hidden bg-gray-200">
                    <Image
                        src={video.thumbnail_url ? video.thumbnail_url : "/no-thumbnail.jpg"}
                        alt=""
                        width={120}
                        height={90}
                        className="object-cover"
                        unoptimized
                    />
                </div>
                <div className="flex flex-col gap-2 w-full">
                    <span className="font-bold text-xl">{video.title}</span>
                    <div className="flex flex-row justify-between items-center">
                        <div className="text-xs text-gray-500 flex flex-col">
                            <span>{video.channel.name + " · " + mapEnumIdeologyToDisplayValue(video.channel.ideology)}</span>
                            <span>{video?.publish_date ? formatDate(video?.publish_date) : "No Date"}</span>
                        </div>
                        <div className="text-xs text-gray-500 text-right flex flex-col">
                            <span>{mapEnumLRToDisplayValue(video.channel.lr)}</span>
                            <span>{`Relevance: ${video.channel.relevance}`}</span>
                        </div>
                    </div>
                </div>
            </div>
            <Separator />
        </Link>
    );
}

export default ItemWrapper;