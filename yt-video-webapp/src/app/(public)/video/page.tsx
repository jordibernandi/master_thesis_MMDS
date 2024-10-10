import FilterWrapper from "@/components/video/FilterWrapper";
import ContentWrapper from "@/components/video/ContentWrapper";
import { Suspense } from "react";
import BadgeWrapper from "@/components/video/BadgeWrapper";
import ContentWrapperLoading from "@/components/video/ContentWrapperLoading";

const VideoPage = async ({ searchParams }: { searchParams: { [key: string]: string | string[] | undefined } }) => {
    const searchParamsKey = JSON.stringify(searchParams);

    return (
        <div className="flex flex-grow">
            <div className="grid grid-cols-6 gap-8 w-full">
                <div className="col-span-2">
                    <FilterWrapper />
                </div>
                <div className="col-span-4 flex flex-col gap-4">
                    <BadgeWrapper />
                    <Suspense key={searchParamsKey} fallback={<ContentWrapperLoading />}>
                        <ContentWrapper searchParams={searchParams} />
                    </Suspense>
                </div>
            </div>
        </div>

    )
}

export default VideoPage;
