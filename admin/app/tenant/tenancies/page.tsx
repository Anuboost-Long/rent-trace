import PageHeader from "@/components/layout/page-header";
import MyInvitations from "@/components/tenancies/my-invitations";
import { Suspense } from "react";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Tenancies"
        description="Your current and past tenancies."
      />
      <Suspense>
        <MyInvitations />
      </Suspense>
    </>
  );
}
