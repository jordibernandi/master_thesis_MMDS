import { FiCalendar } from "react-icons/fi";
import { FiClock } from "react-icons/fi";
import {
    Avatar,
    AvatarFallback,
    AvatarImage,
} from "@/components/ui/avatar"
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion"
import { VideoWithChannel } from "@/lib/types";
import { formatDate, formatVideoDuration, mapEnumIdeologyToDisplayValue, mapEnumLRToDisplayValue } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Ideology } from "@prisma/client";

interface InfoWrapperProps {
    video: VideoWithChannel | null
}

const InfoWrapper = ({ video }: InfoWrapperProps) => {
    return (
        <div className="flex flex-col gap-2 ">
            <span className="text-lg font-bold">{video?.title}</span>
            <div className="flex flex-row gap-2 items-center">
                <FiCalendar className="mr-2 h-4 w-4 opacity-70" />
                <span className="text-xs text-muted-foreground">Published on {formatDate(video?.publish_date ?? undefined)}</span>
            </div>
            <div className="flex flex-row gap-2 items-center">
                <FiClock className="mr-2 h-4 w-4 opacity-70" />
                <span className="text-xs text-muted-foreground">Duration: {formatVideoDuration(video?.length ?? 0)}</span>
            </div>
            <Accordion defaultValue={["item-channel", "item-desc"]} type="multiple">
                <AccordionItem value="item-channel">
                    <AccordionTrigger>@{video?.channel.name.replace(/\s+/g, '')}</AccordionTrigger>
                    <AccordionContent>
                        <div className="flex flex-col gap-4">
                            <div className="flex flex-row gap-4 items-center">
                                <Avatar>
                                    <AvatarImage src={video?.channel.logo_url} />
                                    <AvatarFallback>Logo</AvatarFallback>
                                </Avatar>
                                <div className="space-y-1">
                                    <h4 className="text-sm font-semibold">{video?.channel.name}</h4>
                                    <p className="text-sm">
                                        {mapEnumLRToDisplayValue(video?.channel.lr) + " · " + mapEnumIdeologyToDisplayValue(video?.channel.ideology)}
                                    </p>
                                </div>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {video?.channel.tags.map((tag: Ideology) => (
                                    <Badge
                                        key={tag}
                                        className="w-fit"
                                        variant="default"
                                    >
                                        {mapEnumIdeologyToDisplayValue(tag)}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                    </AccordionContent>
                </AccordionItem>
                <AccordionItem value="item-desc">
                    <AccordionTrigger>Video Description</AccordionTrigger>
                    <AccordionContent>
                        <span className="whitespace-pre-wrap">
                            {video?.description}
                        </span>
                    </AccordionContent>
                </AccordionItem>
                <AccordionItem value="item-key">
                    <AccordionTrigger>Video Keywords</AccordionTrigger>
                    <AccordionContent>
                        <div className="flex flex-wrap gap-2">
                            {video?.keywords.map((keyword: string) => (
                                <Badge
                                    key={keyword}
                                    className="w-fit"
                                    variant="default"
                                >
                                    {keyword}
                                </Badge>
                            ))}
                        </div>
                    </AccordionContent>
                </AccordionItem>
            </Accordion>
        </div>
    );
}

export default InfoWrapper;