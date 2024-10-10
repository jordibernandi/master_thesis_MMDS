import styles from "./column.module.css";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import Row from "./row/Row";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TranscriptWithDetails } from "@/lib/types";

interface ColumnProps {
    transcripts: TranscriptWithDetails[];
}

const Column = ({ transcripts }: ColumnProps) => {

    return (
        <ScrollArea className="h-[1px] flex-grow w-full rounded-md border p-4 overflow-y-auto">
            <SortableContext items={transcripts} strategy={verticalListSortingStrategy}>
                {transcripts.map(transcript =>
                    <Row key={transcript.id} transcript={transcript} />
                )}
            </SortableContext>
        </ScrollArea>
    )
};

export default Column;