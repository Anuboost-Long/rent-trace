"use client";
import type { NavItem } from "@/constants/navigation";
import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";

export type SidebarTone = "admin" | "default";

type NavLinkProp = Readonly<{
  item: NavItem;
  tone: SidebarTone;
  onNavigate?: () => void;
}>;

export const isNavItemActive = (item: NavItem, pathname: string) =>
  item.exact
    ? pathname === item.href
    : pathname === item.href || pathname.startsWith(`${item.href}/`);

export default function NavLink({ item, tone, onNavigate }: NavLinkProp) {
  const isActive = isNavItemActive(item, usePathname());
  const isAdmin = tone === "admin";

  return (
    <Link
      href={item.href}
      title={item.label}
      onClick={onNavigate}
      aria-current={isActive ? "page" : undefined}
      className={clsx(
        "flex h-10 items-center rounded-lg text-body-sm",
        "px-3 group-data-collapsed:justify-center group-data-collapsed:px-0",
        "focus-visible:outline-2 focus-visible:outline-offset-2",
        isAdmin
          ? [
              "focus-visible:outline-on-brand",
              isActive
                ? "bg-admin-active font-medium text-on-brand"
                : "text-on-brand/85 hover:bg-admin-active/60",
            ]
          : [
              "focus-visible:outline-brand-border",
              isActive
                ? "bg-brand-subtle font-medium text-admin-text"
                : "text-fg-secondary hover:bg-subtle",
            ],
      )}
    >
      <item.icon aria-hidden className="size-5 shrink-0" />
      <span className="ml-3 truncate group-data-collapsed:sr-only">
        {item.label}
      </span>
    </Link>
  );
}
