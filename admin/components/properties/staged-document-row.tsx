import Button from "@/components/common/button";
import type { PendingFile } from "@/hooks/form/useStagedFiles";
import { formatBytes } from "@/utils/property-files";
import { FileText, X } from "lucide-react";

type StagedDocumentRowProp = Readonly<{
  item: PendingFile;
  onRemove: () => void;
}>;

export default function StagedDocumentRow({
  item,
  onRemove,
}: StagedDocumentRowProp) {
  return (
    <li className="flex items-center gap-3 p-4">
      <FileText aria-hidden className="size-5 shrink-0" strokeWidth={1.5} />
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{item.file.name}</p>
        <p className="text-sm text-foreground/70">
          New, {formatBytes(item.file.size)}
        </p>
      </div>
      <Button
        variant="quiet"
        size="icon"
        aria-label={`Remove ${item.file.name}`}
        title="Remove"
        onClick={onRemove}
      >
        <X aria-hidden className="size-4" />
      </Button>
    </li>
  );
}
