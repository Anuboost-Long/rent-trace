"use client";
import TabContent from "@/components/common/tab-content";
import { Route } from "@/constants/web-routes";
import { usePathname } from "next/navigation";

const SECTIONS = [
  Route.admin.access,
  Route.admin.permissions,
  Route.admin.grants,
];

export default function Template({ children }: LayoutProps<"/admin/access">) {
  const pathname = usePathname();
  const activeIndex = Math.max(
    SECTIONS.findIndex((href, index) => index > 0 && pathname.startsWith(href)),
    0,
  );

  return (
    <TabContent group="access" activeIndex={activeIndex}>
      {children}
    </TabContent>
  );
}
