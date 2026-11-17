import PageHeader from "@/components/layout/page-header";
import { DashboardSkeleton } from "@/components/layout/page-skeletons";
import Dashboard from "@/components/overview/dashboard";
import { Suspense } from "react";

export default function Page() {
  return (
    <>
      <PageHeader title="Overview" description="Your portfolio at a glance." />
      <Suspense fallback={<DashboardSkeleton />}>
        <Dashboard audience="landlord" />
      </Suspense>
    </>
  );
}
