"use client";
import TabBar from "@/components/common/tab-bar";
import { Route } from "@/constants/web-routes";
import { usePathname } from "next/navigation";

export default function AccessTabs() {
  const pathname = usePathname();
  const onRoles =
    pathname === Route.admin.access ||
    pathname.startsWith(`${Route.admin.access}/roles`);

  const tabs = [
    { label: "Roles", href: Route.admin.access, active: onRoles },
    {
      label: "Permissions",
      href: Route.admin.permissions,
      active: pathname.startsWith(Route.admin.permissions),
    },
    {
      label: "Grants",
      href: Route.admin.grants,
      active: pathname.startsWith(Route.admin.grants),
    },
  ];

  return (
    <TabBar
      label="Access sections"
      tabs={tabs}
      className="mb-6 border-b border-foreground/15"
    />
  );
}
