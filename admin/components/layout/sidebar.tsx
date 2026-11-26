"use client";
import BrandLogo from "@/components/common/brand-logo";
import { groupNavItems, type NavItem } from "@/constants/navigation";
import type { Me } from "@/types/auth/models";
import clsx from "clsx";
import { ChevronLeft } from "lucide-react";
import { memo } from "react";

import NavLink, { type SidebarTone } from "./nav-link";

type SidebarProp = Readonly<{
  label: string;
  tone: SidebarTone;
  user: Me;
  items: NavItem[];
  onNavigate?: () => void;
  onSignOut: () => void;
  headerAction?: React.ReactNode;
  profileAction?: React.ReactNode;
}>;

function SidebarContent({
  label,
  tone,
  user,
  items,
  onNavigate,
  onSignOut,
  headerAction,
  profileAction,
}: SidebarProp) {
  const isAdmin = tone === "admin";

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col gap-6 p-4 group-data-collapsed:p-3">
      <div className="flex shrink-0 items-center gap-2 overflow-hidden whitespace-nowrap group-data-collapsed:justify-center">
        <BrandLogo
          variant="emblem"
          tone={isAdmin ? "white" : "blue"}
          alt=""
          className="size-8 shrink-0"
        />
        <p className="min-w-0 truncate text-section group-data-collapsed:sr-only">
          RentTrace
        </p>
        <span
          className={clsx(
            "rounded px-1.5 py-0.5 text-caption uppercase",
            headerAction ? "hidden" : "group-data-collapsed:hidden",
            isAdmin
              ? "bg-admin-active text-on-brand"
              : "bg-brand-subtle text-admin-text",
          )}
        >
          {label}
        </span>
        {headerAction && (
          <div className="ml-auto shrink-0 group-data-collapsed:hidden">
            {headerAction}
          </div>
        )}
      </div>
      <nav
        aria-label={`${label} navigation`}
        className="min-h-0 flex-1 overflow-y-auto overscroll-contain"
      >
        <ul className="flex flex-col gap-4">
          {groupNavItems(items).map(([group, groupItems]) => (
            <li
              key={group}
              className={
                group
                  ? clsx(
                      "border-t pt-3 group-data-collapsed:pt-4",
                      isAdmin ? "border-on-brand/20" : "border-default",
                    )
                  : undefined
              }
            >
              {group && (
                <p
                  className={clsx(
                    "mb-1 px-3 text-caption group-data-collapsed:sr-only",
                    isAdmin ? "text-on-brand/70" : "text-fg-tertiary",
                  )}
                >
                  {group}
                </p>
              )}
              <ul className="flex flex-col gap-1">
                {groupItems.map((item) => (
                  <li key={item.href}>
                    <NavLink item={item} tone={tone} onNavigate={onNavigate} />
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </nav>
      <div className="flex shrink-0 flex-col gap-3">
        <div className="flex items-start justify-between gap-2 group-data-collapsed:justify-center">
          <div className="min-w-0 overflow-hidden group-data-collapsed:sr-only">
            <p className="truncate text-body-sm font-medium">
              {user.first_name} {user.last_name}
            </p>
            <p
              className={clsx(
                "truncate text-caption font-normal",
                isAdmin ? "text-on-brand/75" : "text-fg-tertiary",
              )}
            >
              {label} · {user.email}
            </p>
          </div>
          {profileAction}
        </div>
        <button
          type="button"
          title="Log out"
          onClick={onSignOut}
          className={clsx(
            "flex h-10 w-full items-center gap-3 rounded-lg border px-3 text-body-sm",
            "group-data-collapsed:justify-center group-data-collapsed:px-0",
            "focus-visible:outline-2 focus-visible:outline-offset-2",
            isAdmin
              ? "border-on-brand/30 text-on-brand hover:bg-admin-active focus-visible:outline-on-brand"
              : "border-strong text-fg-brand hover:bg-brand-subtle focus-visible:outline-brand-border",
          )}
        >
          <ChevronLeft aria-hidden className="size-5 shrink-0" />
          <span className="group-data-collapsed:sr-only">Log out</span>
        </button>
      </div>
    </div>
  );
}

const Sidebar = memo(SidebarContent);
export default Sidebar;
