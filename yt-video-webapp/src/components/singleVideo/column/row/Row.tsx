import styles from "./row.module.css";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Separator } from "@/components/ui/separator";
import { TranscriptWithDetails } from "@/lib/types";

interface RowProps {
    transcript: TranscriptWithDetails;
}

const Row = ({ transcript }: RowProps) => {
    const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: transcript.id })

    const style = {
        transition,
        transform: CSS.Transform.toString(transform)
    }

    return (
        <div ref={setNodeRef} {...attributes} {...listeners} className="flex flex-col gap-2 mb-4" style={style}>
            <span className="font-bold">{transcript.speaker_name}</span>
            <span>{transcript.text}</span>
            <Separator />
        </div>
    )
};

export default Row;