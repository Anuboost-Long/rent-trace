"use client";
import TabBar from "@/components/common/tab-bar";
import { Route } from "@/constants/web-routes";
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
    <TabBar
      label="Team and permissions sections"
      tabs={TABS.map((tab) => ({
        label: tab.label,
        href: tab.href,
        active: isActive(tab, pathname),
      }))}
      className="mb-6 border-b border-default"
    />
  );
}
