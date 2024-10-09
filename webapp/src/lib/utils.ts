import { Ideology, LR, UserRole } from "@prisma/client";
import { type ClassValue, clsx } from "clsx"
import { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";
import { ReadonlyURLSearchParams, useRouter, useSearchParams } from "next/navigation";
import { twMerge } from "tailwind-merge"

export const ideologies: Ideology[] = [
  Ideology.ANTI_SJW,
  Ideology.ANTI_THEIST,
  Ideology.BLACK,
  Ideology.CONSPIRACY,
  Ideology.LGBT,
  Ideology.LIBERTARIAN,
  Ideology.MRA,
  Ideology.PARTISAN_LEFT,
  Ideology.PARTISAN_RIGHT,
  Ideology.QANON,
  Ideology.RELIGIOUS_CONSERVATIVE,
  Ideology.SOCIALIST,
  Ideology.SOCIAL_JUSTICE,
  Ideology.WHITE_IDENTITARIAN
]

export const lrs: LR[] = [
  LR.LEFT,
  LR.RIGHT,
  LR.CENTER
]

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function mapEnumUserRoleToDisplayValue(userRole: UserRole) {
  switch (userRole) {
    case UserRole.ADMIN:
      return 'Admin';
    case UserRole.CONTRIBUTOR:
      return 'Contributor';
    case UserRole.GUEST:
      return 'Guest';
    default:
      return '';
  }
}

export function mapEnumIdeologyToDisplayValue(ideology: Ideology | undefined) {
  switch (ideology) {
    case Ideology.ANTI_SJW:
      return 'Anti-SJW';
    case Ideology.CONSPIRACY:
      return 'Conspiracy';
    case Ideology.RELIGIOUS_CONSERVATIVE:
      return 'Religious Conservative';
    case Ideology.PARTISAN_RIGHT:
      return 'Partisan Right';
    case Ideology.BLACK:
      return 'Black';
    case Ideology.QANON:
      return 'QAnon';
    case Ideology.LGBT:
      return 'LGBT';
    case Ideology.LIBERTARIAN:
      return 'Libertarian';
    case Ideology.SOCIAL_JUSTICE:
      return 'Social Justice';
    case Ideology.SOCIALIST:
      return 'Socialist';
    case Ideology.PARTISAN_LEFT:
      return 'Partisan Left';
    case Ideology.MRA:
      return 'MRA';
    case Ideology.ANTI_THEIST:
      return 'Anti-theist';
    case Ideology.WHITE_IDENTITARIAN:
      return 'White Identitarian';
    default:
      return 'Unknown';
  }
}

export function mapEnumLRToDisplayValue(lr: LR | undefined) {
  switch (lr) {
    case LR.LEFT:
      return 'Left';
    case LR.RIGHT:
      return 'Right';
    case LR.CENTER:
      return 'Center';
    default:
      return 'Unknown';
  }
}

export function formatDate(date?: Date) {
  if (!date) return "";

  const uploadDate = new Date(date);

  const formattedDate = uploadDate.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  return formattedDate
}

export function formatVideoDuration(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;

  // Format the duration as hh:mm:ss
  const formattedHours = hours < 10 ? `0${hours}` : `${hours}`;
  const formattedMinutes = minutes < 10 ? `0${minutes}` : `${minutes}`;
  const formattedSeconds = remainingSeconds < 10 ? `0${remainingSeconds}` : `${remainingSeconds}`;

  if (hours > 0) {
    return `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
  } else {
    return `${formattedMinutes}:${formattedSeconds}`;
  }
}

export const configureFilter = (router: AppRouterInstance, searchParams: ReadonlyURLSearchParams, filterVal: Ideology | LR | string, type: string) => () => {
  const paramPage = searchParams.get("page") ?? "1";
  const paramQuery = searchParams.get("query") ?? "";
  const paramIdeologies = searchParams.get("ideologies") ?? "";
  const paramLrs = searchParams.get("lrs") ?? "";
  const paramRelevance = searchParams.get("relevance") ?? "";
  const paramStart = searchParams.get("start") ?? "";
  const paramEnd = searchParams.get("end") ?? "";
  const paramHasTranscript = searchParams.get("hasTranscript") ?? "";

  const paramSort = searchParams.get("sort") ?? "";

  let tempPage = paramPage;
  let tempQuery = paramQuery;
  let tempParamIdeologies = paramIdeologies;
  let tempParamLrs = paramLrs;
  let tempParamRelevance = paramRelevance;
  let tempParamStart = paramStart;
  let tempParamEnd = paramEnd;
  let tempParamHasTranscript = paramHasTranscript;

  let tempParamSort = paramSort;

  switch (type) {
    case "CLEAR_ALL":
      tempPage = "1";
      tempParamIdeologies = "";
      tempParamLrs = "";
      tempParamRelevance = "";
      tempParamStart = "";
      tempParamEnd = "";
      tempParamHasTranscript = "";
      break;
    case "PAGE":
      tempPage = filterVal;
      break;
    case "QUERY":
      tempQuery = filterVal;
      tempPage = "1";
      break;
    case "IDEOLOGY_ADD":
      tempParamIdeologies = paramIdeologies.length > 0 ? paramIdeologies + "," + filterVal : filterVal;
      tempPage = "1";
      break;
    case "IDEOLOGY_REMOVE":
      tempParamIdeologies = paramIdeologies.split(',').filter((part: string) => part !== filterVal).join(',');
      tempPage = "1";
      break;
    case "LR_ADD":
      tempParamLrs = paramLrs.length > 0 ? paramLrs + "," + filterVal : filterVal;
      tempPage = "1";
      break;
    case "LR_REMOVE":
      tempParamLrs = paramLrs.split(',').filter((part: string) => part !== filterVal).join(',');
      tempPage = "1";
      break;
    case "RELEVANCE":
      tempParamRelevance = filterVal;
      tempPage = "1";
      break;
    case "START":
      tempParamStart = filterVal;
      tempPage = "1";
      break;
    case "END":
      tempParamEnd = filterVal;
      tempPage = "1";
      break;
    case "HAS_TRANSCRIPT":
      tempParamHasTranscript = filterVal;
      tempPage = "1";
      break;
    case "SORT":
      tempParamSort = filterVal;
      tempPage = "1";
      break;
    default:
  }

  if (tempParamStart.length > 0 && tempParamEnd.length > 0) {
    if (new Date(tempParamStart) > new Date(tempParamEnd)) {
      tempParamEnd = "";
    }
  }

  let pageParam = "1"
  let queryParam = "";
  let ideologiesParam = "";
  let lrsParam = "";
  let relevanceParam = "";
  let startParam = "";
  let endParam = "";
  let hasTranscriptParam = "";

  let sortParam = "";

  if (tempPage.length > 0) {
    pageParam = `page=${tempPage}`
  }
  if (tempQuery.length > 0) {
    queryParam = `&query=${tempQuery}`
  }
  if (tempParamIdeologies.length > 0) {
    ideologiesParam = `&ideologies=${tempParamIdeologies}`
  }
  if (tempParamLrs.length > 0) {
    lrsParam = `&lrs=${tempParamLrs}`
  }
  if (tempParamRelevance.length > 0) {
    relevanceParam = `&relevance=${tempParamRelevance}`
  }
  if (tempParamStart.length > 0) {
    startParam = `&start=${tempParamStart}`
  }
  if (tempParamEnd.length > 0) {
    endParam = `&end=${tempParamEnd}`
  }
  if (tempParamHasTranscript.length > 0) {
    hasTranscriptParam = `&hasTranscript=${tempParamHasTranscript}`
  }

  if (tempParamSort.length > 0) {
    sortParam = `&sort=${tempParamSort}`
  }
  router.push(`/video?${pageParam}${queryParam}${ideologiesParam}${lrsParam}${relevanceParam}${startParam}${endParam}${hasTranscriptParam}${sortParam}`);
}
