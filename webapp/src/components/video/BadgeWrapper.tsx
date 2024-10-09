"use client"

import { useRouter, useSearchParams } from "next/navigation";
import { Badge } from "../ui/badge";
import { Ideology, LR } from "@prisma/client";
import { configureFilter, mapEnumIdeologyToDisplayValue, mapEnumLRToDisplayValue } from "@/lib/utils";

const BadgeWrapper = () => {
    const router = useRouter();
    const searchParams = useSearchParams();

    const paramQuery = searchParams.get("query") ?? "";
    const paramIdeologies = searchParams.get("ideologies") ?? "";
    const paramLrs = searchParams.get("lrs") ?? "";
    const paramRelevance = searchParams.get("relevance") ?? "";
    const paramStart = searchParams.get("start") ?? "";
    const paramEnd = searchParams.get("end") ?? "";
    const paramHasTranscript = searchParams.get("hasTranscript") ?? "";

    return (
        <div className="flex flex-wrap gap-2">
            {paramQuery.length == 0 && paramIdeologies.length == 0 && paramLrs.length == 0 && paramRelevance.length == 0 && paramStart.length == 0 && paramEnd.length == 0 && paramHasTranscript.length == 0 && (
                <Badge variant="default">
                    All Dataset
                </Badge>
            )}
            {paramQuery.length > 0 && (
                <Badge
                    key={paramQuery}
                    variant="default"
                    closable
                    onClose={configureFilter(router, searchParams, "", "QUERY")}
                >
                    {`Query: ${paramQuery}`}
                </Badge>
            )}
            {paramIdeologies.length > 0 && (paramIdeologies?.split(',') as Ideology[]).map(ideology => (
                <Badge
                    key={ideology}
                    variant="default"
                    closable
                    onClose={configureFilter(router, searchParams, ideology, "IDEOLOGY_REMOVE")}
                >
                    {mapEnumIdeologyToDisplayValue(ideology)}
                </Badge>
            ))}
            {paramLrs.length > 0 && (paramLrs?.split(',') as LR[]).map(lr => (
                <Badge
                    key={lr}
                    variant="default"
                    closable
                    onClose={configureFilter(router, searchParams, lr, "LR_REMOVE")}
                >
                    {mapEnumLRToDisplayValue(lr)}
                </Badge>
            ))}
            {paramRelevance.length > 0 && (
                <Badge
                    key={paramRelevance}
                    variant="default"
                    closable
                    onClose={configureFilter(router, searchParams, "", "RELEVANCE")}
                >
                    {`Relevance Score between: ${paramRelevance?.split(',').map(Number)[0]} and ${paramRelevance?.split(',').map(Number)[1]}`}
                </Badge>
            )}
            {paramStart.length > 0 && (
                <Badge
                    key={paramStart}
                    variant="default"
                    closable
                    onClose={configureFilter(router, searchParams, "", "START")}
                >
                    {`Start: ${paramStart}`}
                </Badge>
            )}
            {paramEnd.length > 0 && (
                <Badge
                    key={paramEnd}
                    variant="default"
                    closable
                    onClose={configureFilter(router, searchParams, "", "END")}
                >
                    {`End: ${paramEnd}`}
                </Badge>
            )}
            {paramHasTranscript.length > 0 && (
                <Badge
                    key={paramHasTranscript}
                    variant="default"
                    closable
                    onClose={configureFilter(router, searchParams, "", "HAS_TRANSCRIPT")}
                >
                    {"Has Transcript"}
                </Badge>
            )}
        </div>
    );
}

export default BadgeWrapper;