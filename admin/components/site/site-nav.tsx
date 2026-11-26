"use client";
import TabBar from "@/components/common/tab-bar";
import { Route } from "@/constants/web-routes";
import { usePathname } from "next/navigation";

export type RoleLink = Readonly<{
  href: string;
  label: string;
  activePrefix: string;
}>;

export default function SiteNav({
  roleLink,
}: Readonly<{ roleLink: RoleLink | null }>) {
  const pathname = usePathname();

  const tabs = [
    {
      href: Route.listings,
      label: "Browse rentals",
      active: pathname.startsWith(Route.listings),
    },
    ...(roleLink
      ? [
          {
            href: roleLink.href,
            label: roleLink.label,
            active: pathname.startsWith(roleLink.activePrefix),
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
