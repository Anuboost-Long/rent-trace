import PageHeader from "@/components/layout/page-header";
import { CardsSkeleton } from "@/components/layout/page-skeletons";
import MyInvitations from "@/components/tenancies/my-invitations";
import MyTenancies from "@/components/tenancies/my-tenancies";
import { Suspense } from "react";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Tenancies"
        description="Where you live now and where you have lived."
      />
      <Suspense>
        <MyInvitations />
      </Suspense>
      <Suspense fallback={<CardsSkeleton />}>
        <MyTenancies showHistory />
      </Suspense>
    </>
  );
}
