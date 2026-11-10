"use client";
import { Route } from "@/constants/web-routes";
import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { label: "Roles", href: Route.admin.access, exact: true },
  { label: "Permissions", href: Route.admin.permissions },
  { label: "Grants", href: Route.admin.grants },
];

export default function AccessTabs() {
  const pathname = usePathname();
  const onRoles =
    pathname === Route.admin.access ||
    pathname.startsWith(`${Route.admin.access}/roles`);

  return (
    <nav
      aria-label="Access sections"
      className="mb-6 flex gap-1 border-b border-foreground/15"
    >
      {TABS.map((tab) => {
        const active = tab.exact ? onRoles : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            aria-current={active ? "page" : undefined}
            className={clsx(
              "-mb-px border-b-2 px-4 py-2.5 text-sm",
              active
                ? "border-foreground font-semibold"
                : "border-transparent text-foreground/70 hover:text-foreground",
            )}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
