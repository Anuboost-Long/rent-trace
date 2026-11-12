import PageHeader from "@/components/layout/page-header";
import MyInvitations from "@/components/tenancies/my-invitations";
import MyTenancies from "@/components/tenancies/my-tenancies";
import { Suspense } from "react";

export default function Page() {
  return (
    <>
      <PageHeader title="Overview" description="Your tenancy at a glance." />
      <Suspense>
        <MyInvitations />
      </Suspense>
      <Suspense>
        <MyTenancies showHistory={false} />
      </Suspense>
    </>
  );
}
