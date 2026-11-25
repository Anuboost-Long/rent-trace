import clsx from "clsx";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

import type { SidebarTone } from "./nav-link";

type SidebarToggleProp = Readonly<{
  collapsed: boolean;
  tone: SidebarTone;
  onToggle: () => void;
}>;

export default function SidebarToggle({
  collapsed,
  tone,
  onToggle,
}: SidebarToggleProp) {
  const label = collapsed ? "Expand sidebar" : "Collapse sidebar";
  const Icon = collapsed ? PanelLeftOpen : PanelLeftClose;

  return (
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
        "text-body-sm focus-visible:outline-2 focus-visible:outline-offset-2",
        tone === "admin"
          ? "text-on-brand/85 hover:bg-admin-active/60 focus-visible:outline-on-brand"
          : "text-fg-secondary hover:bg-subtle focus-visible:outline-brand-border",
      )}
    >
      <Icon aria-hidden className="size-5 shrink-0" />
      <span aria-hidden className="ml-3 group-data-collapsed:hidden">
        Collapse
      </span>
    </button>
  );
}
