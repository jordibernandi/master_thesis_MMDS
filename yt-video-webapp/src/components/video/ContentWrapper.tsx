import HeaderWrapper from "@/components/video/HeaderWrapper";
import ListWrapper from "@/components/video/ListWrapper";
import PaginationControl from "@/components/video/PaginationControl";
import { getAllVideos } from "@/data/video";
import { Sort, VideoWithChannel } from "@/lib/types";
import { Ideology, LR } from "@prisma/client";


const ContentWrapper = async ({ searchParams }: { searchParams: { [key: string]: string | string[] | undefined } }) => {

    const paramPage = searchParams["page"] ?? "1";
    const paramQuery = searchParams["query"] ?? "";
    const paramIdeologies = searchParams["ideologies"] ? (searchParams["ideologies"] as string).split(',') : [];
    const paramLrs = searchParams["lrs"] ? (searchParams["lrs"] as string).split(',') : [];
    const paramRelevance = searchParams["relevance"] ? (searchParams["relevance"] as string).split(',').map(Number) : [];
    const paramStart = searchParams["start"] ?? "";
    const paramEnd = searchParams["end"] ?? "";
    const paramHasTranscript = searchParams["hasTranscript"] ?? "";
    const paramSort = searchParams["sort"] ?? "";

    const perPage = 20;

    const data: {
        videos: VideoWithChannel[];
        totalVideos: number;
    } | null = await getAllVideos(
        paramQuery as string,
        paramIdeologies as Ideology[],
        paramLrs as LR[],
        paramRelevance as number[],
        paramStart as string,
        paramEnd as string,
        paramHasTranscript ? true : false as boolean,
        Number(paramPage),
        perPage,
        paramSort as Sort
    );

    const start = (Number(paramPage) - 1) * Number(perPage);
    const end = start + Number(perPage);

    const totalVideos: number | null = data ? data.totalVideos : 0;

    return (
        <>
            <HeaderWrapper totalVideos={totalVideos} />
            <ListWrapper videos={data?.videos ?? []} />
            {data && data.totalVideos > 0 && (
                <PaginationControl
                    hasNextPage={end < totalVideos}
                    hasPrevPage={start > 0}
                    numberOfPages={Math.ceil(totalVideos / Number(perPage))}
                />
            )}
        </>
    )
}

export default ContentWrapper;
