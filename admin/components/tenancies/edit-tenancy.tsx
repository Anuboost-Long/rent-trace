import { handleGetTenancy } from "@/api/services/tenancies/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { FormSkeleton } from "@/components/layout/page-skeletons";
import { TenancyRoutes } from "@/constants/tenancies";
import type { TenancyAudience } from "@/types/tenancies/models";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import EditTenancyForm from "./edit-tenancy-form";

type EditTenancyProp = Readonly<{
  audience: TenancyAudience;
  params: Promise<{ id: string }>;
}>;

export default function EditTenancyPage(props: EditTenancyProp) {
  return (
    <Suspense fallback={<FormSkeleton withHeader />}>
      <EditTenancy {...props} />
    </Suspense>
  );
}

async function EditTenancy({ audience, params }: EditTenancyProp) {
  const { id } = await params;
  const { data: tenancy, error } = await handleGetTenancy(id, audience);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }
  if (tenancy.status === "ENDED" || tenancy.status === "CANCELLED") {
    notFound();
  }

  return (
    <div className="max-w-xl">
      <Breadcrumbs
        trail={[
          { label: "Tenancies", href: TenancyRoutes[audience].list },
          {
            label: tenancy.reference_no,
            href: TenancyRoutes[audience].detail(tenancy.id),
          },
          { label: "Edit" },
        ]}
      />
      <h1 className="mt-4 text-2xl font-semibold">Edit tenancy</h1>
      <p className="mt-1 mb-6 text-foreground/70">
        Dates and notes apply at once. A higher rent or bond waits until every
        tenant approves it.
      </p>
      <EditTenancyForm audience={audience} tenancy={tenancy} />
    </div>
  );
}
