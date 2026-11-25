"use client";
import type { NavItem } from "@/constants/navigation";
import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";

type NavLinkProp = Readonly<{ item: NavItem; onNavigate?: () => void }>;

export default function NavLink({ item, onNavigate }: NavLinkProp) {
  const pathname = usePathname();
  const isActive = item.exact
    ? pathname === item.href
    : pathname === item.href || pathname.startsWith(`${item.href}/`);

  return (
    <Link
      href={item.href}
      title={item.label}
      onClick={onNavigate}
      aria-current={isActive ? "page" : undefined}
      className={clsx(
        "flex h-10 items-center rounded-lg",
        isActive && "bg-muted",
        "px-2.5 group-data-collapsed:justify-center group-data-collapsed:px-0",
        "text-sm",
        isActive ? "font-semibold" : "text-fg-secondary",
        "hover:bg-subtle focus-visible:outline-2 focus-visible:outline-brand-border",
      )}
    >
      <item.icon aria-hidden className="size-5 shrink-0" />
      <span className="ml-3 truncate group-data-collapsed:sr-only">
        {item.label}
      </span>
    </Link>
  );
}
