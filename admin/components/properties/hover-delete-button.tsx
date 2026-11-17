import clsx from "clsx";
import { Trash2 } from "lucide-react";

type HoverDeleteButtonProp = Readonly<{
  label: string;
  onClick: () => void;
}>;

export default function HoverDeleteButton({
  label,
  onClick,
}: HoverDeleteButtonProp) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      className={clsx(
        "absolute top-2 right-2 flex size-7 items-center justify-center rounded-full",
        "border border-foreground/15 bg-background text-foreground",
        "opacity-0 transition-opacity group-focus-within:opacity-100 group-hover:opacity-100 pointer-coarse:opacity-100 motion-reduce:transition-none",
        "hover:bg-foreground hover:text-background focus-visible:opacity-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-foreground",
      )}
    >
      <Trash2 aria-hidden className="size-3.5" />
    </button>
  );
}
