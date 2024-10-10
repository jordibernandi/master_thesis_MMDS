import { ScrollArea } from "../ui/scroll-area";
import { Separator } from "../ui/separator";
import { Skeleton } from "../ui/skeleton";

const ContentWrapperLoading = () => {
    return (
        <>
            <div className="flex flex-row justify-between items-center h-8">
                <Skeleton className="h-6 w-[150px]" />
                <div className="flex flex-row items-center gap-4">
                    <Skeleton className="h-6 w-[120px]" />
                    <Skeleton className="h-6 w-[25px]" />
                </div>
            </div>
            <ScrollArea className="h-[1px] flex-grow w-full rounded-md border p-4 overflow-y-auto">
                {[...Array(10)].map((_, i) => (
                    <>
                        <div key={i} className="flex flex-row gap-2 p-2.5 hover:bg-gray-100 transition duration-300 ease-in-out">
                            <Skeleton className="h-[90px] w-[120px]" />
                            <div className="flex flex-col gap-4 w-full">
                                <Skeleton className="h-6 w-100" />
                                <div className="flex flex-row justify-between items-center">
                                    <div className="flex flex-col gap-1">
                                        <Skeleton className="h-3 w-[150px]" />
                                        <Skeleton className="h-3 w-[150px]" />
                                    </div>
                                    <div className="flex flex-col gap-1">
                                        <Skeleton className="h-3 w-[150px]" />
                                        <Skeleton className="h-3 w-[150px]" />
                                    </div>
                                </div>
                            </div>
                        </div >
                        <Separator />
                    </>
                ))}
            </ScrollArea >
            <Skeleton className="h-9 w-[500px] mx-auto" />
        </>
    )
}

export default ContentWrapperLoading;
