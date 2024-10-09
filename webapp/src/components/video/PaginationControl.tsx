"use client"

import { useRouter, useSearchParams } from "next/navigation";
import {
    Pagination,
    PaginationContent,
    PaginationItem,
    PaginationLink,
    PaginationNext,
    PaginationPrevious,
} from "@/components/ui/pagination"
import { useMemo } from "react";
import { configureFilter } from "@/lib/utils";

interface PaginationControlProps {
    hasNextPage: boolean
    hasPrevPage: boolean
    numberOfPages: number
}

const PaginationControl = ({ hasNextPage, hasPrevPage, numberOfPages }: PaginationControlProps) => {
    const router = useRouter();
    const searchParams = useSearchParams();

    const pagesToShow = 9;

    const paramPage = searchParams.get("page") ?? "1";

    const totalPages = numberOfPages;
    const currentPage = Number(paramPage);

    let startIndex, endIndex;

    if (totalPages <= pagesToShow) {
        startIndex = 0;
        endIndex = totalPages;
    } else {
        const halfPagesToShow = Math.floor(pagesToShow / 2);

        if (currentPage <= halfPagesToShow + 1) {
            startIndex = 0;
            endIndex = pagesToShow;
        } else if (currentPage >= totalPages - halfPagesToShow) {
            startIndex = totalPages - pagesToShow;
            endIndex = totalPages;
        } else {
            startIndex = currentPage - halfPagesToShow - 1;
            endIndex = currentPage + halfPagesToShow;
        }
    }

    return (
        <Pagination>
            <PaginationContent>
                <PaginationItem>
                    <PaginationPrevious
                        isActive={hasPrevPage}
                        onClick={() => {
                            hasPrevPage && configureFilter(router, searchParams, `${currentPage - 1}`, "PAGE")()
                        }} />
                </PaginationItem>
                {[...Array(endIndex - startIndex)].map((_, index) => (
                    <PaginationItem key={startIndex + index}>
                        <PaginationLink
                            isActive={startIndex + index + 1 !== currentPage}
                            onClick={() => {
                                configureFilter(router, searchParams, `${startIndex + index + 1}`, "PAGE")()
                            }}>
                            {startIndex + index + 1}
                        </PaginationLink>
                    </PaginationItem>
                ))}
                <PaginationItem>
                    <PaginationNext
                        isActive={hasNextPage}
                        onClick={() => {
                            hasNextPage && configureFilter(router, searchParams, `${currentPage + 1}`, "PAGE")()
                        }} />
                </PaginationItem>
            </PaginationContent>
        </Pagination>
    );
}

export default PaginationControl;