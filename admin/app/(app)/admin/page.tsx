import { DashboardSkeleton } from "@/components/layout/page-skeletons";
import Dashboard from "@/components/overview/dashboard";
import Greeting from "@/components/overview/greeting";
import { Suspense } from "react";

export default function Page() {
  return (
    <>
      <Greeting />
      <Suspense fallback={<DashboardSkeleton />}>
        <Dashboard audience="admin" />
      </Suspense>
    </>
  );
}
