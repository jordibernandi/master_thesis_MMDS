"use client"

import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useRouter, useSearchParams } from "next/navigation";
import { useDebounce } from 'use-debounce';
import { CalendarIcon } from "@radix-ui/react-icons";
import { format } from "date-fns";
import { cn, configureFilter } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { DualRangeSlider } from '@/components/ui/dual-range-slider';
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"
import { ideologies, lrs, mapEnumIdeologyToDisplayValue, mapEnumLRToDisplayValue } from "@/lib/utils";
import { Ideology, LR } from "@prisma/client";
import { FiAlertCircle } from "react-icons/fi";

const FilterWrapper = () => {
    const router = useRouter();
    const searchParams = useSearchParams();

    const paramQuery = useMemo(() => {
        return searchParams.get("query") ? searchParams.get("query") : "";
    }, [searchParams]);
    const paramIdeologies = searchParams.get("ideologies") ?? "";
    const paramLrs = searchParams.get("lrs") ?? "";
    const paramRelevance = useMemo(() => {
        return searchParams.get("relevance") ? searchParams.get("relevance")?.split(',').map(Number) : [];
    }, [searchParams]);
    const paramStart = searchParams.get("start") ?? "";
    const paramEnd = searchParams.get("end") ?? "";
    const paramHasTranscript = searchParams.get("hasTranscript") ?? "";

    const [queryTerm, setQueryTerm] = useState(paramQuery);
    const [debouncedQueryTerm] = useDebounce(queryTerm, 1000);

    const [relevanceTerm, setRelevanceTerm] = useState(paramRelevance);
    const [debouncedRelevanceTerm] = useDebounce(relevanceTerm, 1000);

    useEffect(() => {
        setQueryTerm(paramQuery);
    }, [paramQuery]);

    useEffect(() => {
        setRelevanceTerm(paramRelevance);
    }, [paramRelevance]);

    useEffect(() => {
        if (debouncedQueryTerm !== undefined && debouncedQueryTerm !== null && debouncedQueryTerm !== paramQuery) {
            configureFilter(router, searchParams, debouncedQueryTerm, "QUERY")();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [debouncedQueryTerm]);

    useEffect(() => {
        if (debouncedRelevanceTerm !== undefined && debouncedRelevanceTerm !== null && debouncedRelevanceTerm !== paramRelevance) {
            configureFilter(router, searchParams, debouncedRelevanceTerm.join(','), "RELEVANCE")();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [debouncedRelevanceTerm]);

    return (
        <div className="flex flex-col gap-4">
            <Input
                className="w-full"
                placeholder="Search"
                value={queryTerm ?? ""}
                onChange={(e) => setQueryTerm(e.target.value)}
            />
            <Badge
                className="w-fit cursor-pointer"
                variant={paramQuery?.length == 0 && paramIdeologies.length == 0 && paramLrs.length == 0 && paramRelevance?.length == 0 && paramStart.length == 0 && paramEnd.length == 0 && paramHasTranscript.length == 0 ? "default" : "outline"}
                onClick={configureFilter(router, searchParams, "", "CLEAR_ALL")}
            >
                All Dataset
            </Badge>
            <div className="flex flex-col gap-2">
                <span className="tracking-wide uppercase text-xs">Ideology</span>
                <div className="flex flex-wrap gap-2">
                    {ideologies.map((ideology: Ideology) => (
                        <Badge
                            key={ideology}
                            className="w-fit cursor-pointer"
                            variant={paramIdeologies.includes(ideology) ? "default" : "outline"}
                            onClick={paramIdeologies.includes(ideology) ? configureFilter(router, searchParams, ideology, "IDEOLOGY_REMOVE") : configureFilter(router, searchParams, ideology, "IDEOLOGY_ADD")}
                        >
                            {mapEnumIdeologyToDisplayValue(ideology)}
                        </Badge>
                    ))}
                </div>
            </div>
            <div className="flex flex-col gap-2">
                <span className="tracking-wide uppercase text-xs">LR</span>
                <div className="flex flex-wrap gap-2">
                    {lrs.map((lr: LR) => (
                        <Badge
                            key={lr}
                            className="w-fit cursor-pointer"
                            variant={paramLrs.includes(lr) ? "default" : "outline"}
                            onClick={paramLrs.includes(lr) ? configureFilter(router, searchParams, lr, "LR_REMOVE") : configureFilter(router, searchParams, lr, "LR_ADD")}
                        >
                            {mapEnumLRToDisplayValue(lr)}
                        </Badge>
                    ))}
                </div>
            </div>
            <div className="flex flex-col gap-2">
                <div className="flex flex-row gap-2">
                    <span className="tracking-wide uppercase text-xs">Relevance</span>

                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger><FiAlertCircle /></TooltipTrigger>
                            <TooltipContent>
                                <p>Representing the portion of channel content relevant to US politics & cultural commentary</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>

                </div>
                <div className="flex flex-wrap gap-2 pt-6">
                    <DualRangeSlider
                        label={(value) => <span>{value && value / 100}</span>}
                        value={relevanceTerm && relevanceTerm.length > 0 ? relevanceTerm.map(value => value * 100) : [1, 100]}
                        onValueChange={(value) => setRelevanceTerm(JSON.stringify([1, 100]) != JSON.stringify(value) ? value.map(value => value / 100) : [])}
                        min={1}
                        max={100}
                        step={1}
                    />
                </div>
            </div>
            <div className="flex flex-col gap-2">
                <span className="tracking-wide uppercase text-xs">Start Date</span>
                <div className="flex flex-wrap gap-2">
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button
                                variant={"outline"}
                                className={cn(
                                    "w-[240px] justify-start text-left font-normal",
                                    !paramStart && "text-muted-foreground"
                                )}
                            >
                                <CalendarIcon className="mr-2 h-4 w-4" />
                                {paramStart ? format(paramStart, "PPP") : <span>Pick a date</span>}
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                                mode="single"
                                selected={new Date(paramStart)}
                                onSelect={(dateString) => {
                                    const formattedDate = dateString ? new Date(dateString).toLocaleDateString('en-US') : "";
                                    configureFilter(router, searchParams, formattedDate, "START")();
                                }}
                                initialFocus
                            />
                        </PopoverContent>
                    </Popover>
                </div>
            </div>
            <div className="flex flex-col gap-2">
                <span className="tracking-wide uppercase text-xs">End Date</span>
                <div className="flex flex-wrap gap-2">
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button
                                variant={"outline"}
                                className={cn(
                                    "w-[240px] justify-start text-left font-normal",
                                    !paramEnd && "text-muted-foreground"
                                )}
                            >
                                <CalendarIcon className="mr-2 h-4 w-4" />
                                {paramEnd ? format(paramEnd, "PPP") : <span>Pick a date</span>}
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                                mode="single"
                                selected={new Date(paramEnd)}
                                onSelect={(dateString) => {
                                    const formattedDate = dateString ? new Date(dateString).toLocaleDateString('en-US') : "";
                                    configureFilter(router, searchParams, formattedDate, "END")();
                                }}
                                initialFocus
                            />
                        </PopoverContent>
                    </Popover>
                </div>
            </div>
            <div className="flex flex-col gap-2">
                <span className="tracking-wide uppercase text-xs">Transcript</span>
                <div className="flex items-center space-x-2">
                    <Switch id="has-transcript" checked={paramHasTranscript ? true : false} onCheckedChange={() => {
                        configureFilter(router, searchParams, !paramHasTranscript == true ? "true" : "", "HAS_TRANSCRIPT")();
                    }} />
                    <Label htmlFor="has-transcript">Has Transcript</Label>
                </div>
            </div>
        </div>
    );
}

export default FilterWrapper;