"use client";
import TabBar from "@/components/common/tab-bar";
import { Route } from "@/constants/web-routes";
import { usePathname } from "next/navigation";
import { useEffect } from "react";

export type RoleLink = Readonly<{
  href: string;
  label: string;
  activePrefix: string;
}>;

let lastRoleLink: RoleLink | null = null;

export default function SiteNav({
  roleLink,
}: Readonly<{ roleLink: RoleLink | null }>) {
  const pathname = usePathname();
  const shown = roleLink ?? lastRoleLink;

  useEffect(() => {
    if (roleLink) lastRoleLink = roleLink;
  }, [roleLink]);

  const tabs = [
    {
      href: Route.listings,
      label: "Browse rentals",
      active: pathname.startsWith(Route.listings),
    },
    ...(shown
      ? [
          {
            href: shown.href,
            label: shown.label,
            active: pathname.startsWith(shown.activePrefix),
            className: "hidden md:flex",
          },
        ]
      : []),
  ];

  return (
    <TabBar
      label="Main"
      tabs={tabs}
      className="self-stretch"
      tabClassName="h-16"
    />
  );
}
