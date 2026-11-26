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
        "flex size-8 shrink-0 items-center justify-center rounded-lg",
        "focus-visible:outline-2 focus-visible:outline-offset-2",
        tone === "admin"
          ? "text-on-brand/85 hover:bg-admin-active/60 focus-visible:outline-on-brand"
          : "text-fg-secondary hover:bg-subtle focus-visible:outline-brand-border",
      )}
    >
      <Icon aria-hidden className="size-4" />
    </button>
  );
}
