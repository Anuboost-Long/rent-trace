import { HomePanelSkeleton } from "@/components/layout/page-skeletons";
import MyInvitations from "@/components/tenancies/my-invitations";
import TenantHome from "@/components/tenancies/tenant-home";
import { getViewer } from "@/utils/viewer";
import { Suspense } from "react";

export default function Page() {
  return (
    <div className="max-w-4xl">
      <Suspense
        fallback={<h1 className="mb-8 text-3xl font-semibold">Welcome back</h1>}
      >
        <Greeting />
      </Suspense>
      <Suspense>
        <MyInvitations />
      </Suspense>
      <Suspense fallback={<HomePanelSkeleton />}>
        <TenantHome />
      </Suspense>
    </div>
  );
}

async function Greeting() {
  const user = await getViewer();
  return (
    <div className="mb-8">
      <h1 className="text-3xl font-semibold tracking-tight">
        Welcome back{user ? `, ${user.first_name}` : ""}
      </h1>
      <p className="mt-1 text-fg-secondary">
        Your home, your rent and your landlord, in one place.
      </p>
    </div>
  );
}
