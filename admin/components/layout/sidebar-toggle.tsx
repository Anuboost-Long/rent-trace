import clsx from "clsx";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

type SidebarToggleProp = Readonly<{
  collapsed: boolean;
  onToggle: () => void;
}>;

export default function SidebarToggle({
  collapsed,
  onToggle,
}: SidebarToggleProp) {
  const label = collapsed ? "Expand sidebar" : "Collapse sidebar";
  const Icon = collapsed ? PanelLeftOpen : PanelLeftClose;

  return (
    <div className="p-4 group-data-collapsed:p-3">
      <button
        type="button"
        onClick={onToggle}
        title={label}
        aria-label={label}
        aria-controls="sidebar"
        aria-expanded={!collapsed}
        className={clsx(
          "flex h-10 w-full items-center rounded-lg",
          "px-2.5 group-data-collapsed:justify-center group-data-collapsed:px-0",
          "text-sm text-foreground/70",
          "hover:bg-foreground/5 hover:text-foreground focus-visible:outline-2 focus-visible:outline-foreground",
        )}
      >
        <Icon aria-hidden className="size-5 shrink-0" />
        <span aria-hidden className="ml-3 group-data-collapsed:hidden">
          Collapse
        </span>
      </button>
    </div>
  );
}
