"use client";
import TabContent from "@/components/common/tab-content";
import { Navigation } from "@/constants/navigation";
import { usePathname } from "next/navigation";

export default function Template({ children }: LayoutProps<"/tenant">) {
  const pathname = usePathname();
  const activeIndex = Navigation.tenant.items.findIndex((item) =>
    item.exact
      ? pathname === item.href
      : pathname === item.href || pathname.startsWith(`${item.href}/`),
  );

  return (
    <TabContent group="tenant" activeIndex={activeIndex}>
      {children}
    </TabContent>
  );
}
