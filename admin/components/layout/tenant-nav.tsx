"use client";
import TabBar from "@/components/common/tab-bar";
import { Navigation } from "@/constants/navigation";
import { usePathname } from "next/navigation";

export default function TenantNav() {
  const pathname = usePathname();

  const tabs = Navigation.tenant.items.map((item) => ({
    href: item.href,
    label: item.label,
    active: item.exact
      ? pathname === item.href
      : pathname === item.href || pathname.startsWith(`${item.href}/`),
  }));

  return (
    <TabBar
      label="Your rentals"
      tabs={tabs}
      className="border-b border-foreground/10"
      listClassName="mx-auto w-full max-w-7xl px-4 sm:px-6"
    />
  );
}
