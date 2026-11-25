"use client";
import { Navigation } from "@/constants/navigation";
import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function TenantNav() {
  const pathname = usePathname();

  return (
    <nav aria-label="Your rentals" className="border-b border-default">
      <ul className="mx-auto flex w-full max-w-7xl gap-1 overflow-x-auto px-4 sm:px-6">
        {Navigation.tenant.items.map((item) => {
          const isActive = item.exact
            ? pathname === item.href
            : pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={clsx(
                  "flex h-12 items-center border-b-2 px-3 text-sm whitespace-nowrap",
                  "focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-brand-border",
                  isActive
                    ? "border-brand-border font-semibold"
                    : "border-transparent text-fg-secondary hover:text-foreground",
                )}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
