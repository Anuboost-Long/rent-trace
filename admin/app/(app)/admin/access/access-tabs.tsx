"use client";
import { Route } from "@/constants/web-routes";
import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { label: "Admins", href: Route.admin.access, exact: true },
  { label: "Roles", href: Route.admin.roles },
  { label: "Permissions", href: Route.admin.permissions },
  { label: "Grants", href: Route.admin.grants },
];

const isActive = (tab: (typeof TABS)[number], pathname: string) =>
  tab.exact
    ? pathname === tab.href || pathname.startsWith(`${tab.href}/admins`)
    : pathname.startsWith(tab.href);

export default function AccessTabs() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Team and permissions sections"
      className="mb-6 flex gap-1 overflow-x-auto border-b border-default"
    >
      {TABS.map((tab) => {
        const active = isActive(tab, pathname);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            aria-current={active ? "page" : undefined}
            className={clsx(
              "-mb-px border-b-2 px-4 py-2.5 text-body-sm whitespace-nowrap",
              "focus-visible:outline-2 focus-visible:outline-brand-border",
              active
                ? "border-brand-border font-semibold text-fg-brand"
                : "border-transparent text-fg-secondary hover:text-foreground",
            )}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
