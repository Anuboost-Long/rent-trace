"use client";
import { groupNavItems, type NavItem } from "@/constants/navigation";
import { memo } from "react";

import NavLink from "./nav-link";

type SidebarProp = Readonly<{
  label: string;
  items: NavItem[];
  onNavigate?: () => void;
}>;

function SidebarContent({ label, items, onNavigate }: SidebarProp) {
  return (
    <div className="flex h-full flex-col gap-6 p-4 group-data-collapsed:p-3">
      <div className="overflow-hidden whitespace-nowrap">
        <p className="text-xl font-bold">
          R<span className="group-data-collapsed:hidden">entTrace</span>
        </p>
        <p className="text-sm text-fg-secondary group-data-collapsed:sr-only">
          {label}
        </p>
      </div>
      <nav aria-label={`${label} navigation`}>
        <ul className="flex flex-col gap-4">
          {groupNavItems(items).map(([group, groupItems]) => (
            <li
              key={group}
              className={
                group
                  ? "border-t border-default pt-3 group-data-collapsed:pt-4"
                  : undefined
              }
            >
              {group && (
                <p className="mb-1 px-2.5 text-xs text-fg-tertiary group-data-collapsed:sr-only">
                  {group}
                </p>
              )}
              <ul className="flex flex-col gap-1">
                {groupItems.map((item) => (
                  <li key={item.href}>
                    <NavLink item={item} onNavigate={onNavigate} />
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}

const Sidebar = memo(SidebarContent);
export default Sidebar;
