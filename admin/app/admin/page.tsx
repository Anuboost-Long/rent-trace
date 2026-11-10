import PageHeader from "@/components/layout/page-header";

import MenuGrid from "./menu-grid";
import MockDashboard from "./mock-dashboard";
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
        dashboard={<MockDashboard />}
      />
    </>
  );
}
