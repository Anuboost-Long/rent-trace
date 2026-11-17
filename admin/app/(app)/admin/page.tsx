import PageHeader from "@/components/layout/page-header";
import { DashboardSkeleton } from "@/components/layout/page-skeletons";
import Dashboard from "@/components/overview/dashboard";
import { Suspense } from "react";

import MenuGrid from "./menu-grid";
import OverviewViews from "./overview-views";

export default async function Page({ searchParams }: PageProps<"/admin">) {
  const { view } = await searchParams;

  return (
    <>
      <PageHeader
        title="Overview"
        description="Platform activity at a glance."
      />
      <OverviewViews
        initialView={view === "dashboard" ? "dashboard" : "menu"}
        menu={<MenuGrid />}
        dashboard={
          <Suspense fallback={<DashboardSkeleton />}>
            <Dashboard audience="admin" />
          </Suspense>
        }
      />
    </>
  );
}
