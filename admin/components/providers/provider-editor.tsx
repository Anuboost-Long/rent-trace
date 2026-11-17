import { handleGetProperties } from "@/api/services/properties/serve-action";
import {
  handleGetProvider,
  handleGetServiceCategories,
} from "@/api/services/providers/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { FormSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import DeleteProviderButton from "./delete-provider-button";
import ProviderForm from "./provider-form";

type ProviderEditorProp = Readonly<{ params?: Promise<{ id: string }> }>;

export default function ProviderEditorPage(props: ProviderEditorProp) {
  return (
    <Suspense fallback={<FormSkeleton withHeader />}>
      <ProviderEditor {...props} />
    </Suspense>
  );
}

async function ProviderEditor({ params }: ProviderEditorProp) {
  const id = params && (await params).id;
  const [existing, categories, properties] = await Promise.all([
    id ? handleGetProvider(id) : null,
    handleGetServiceCategories(),
    handleGetProperties({ page_size: 100 }, "landlord"),
  ]);
  if (existing?.error?.status === 404) notFound();
  if (categories.error || properties.error || existing?.error) {
    const { message } = (categories.error ??
      properties.error ??
      existing?.error)!;
    return (
      <p role="alert" className="text-red-600">
        {message}
      </p>
    );
  }
  const provider = existing?.data ?? undefined;

  return (
    <>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <Breadcrumbs
          trail={[
            { label: "Tradespeople", href: Route.landlord.providers },
            { label: provider?.business_name ?? "New" },
          ]}
        />
        {provider && (
          <DeleteProviderButton
            id={provider.id}
            name={provider.business_name}
          />
        )}
      </div>
      <h1 className="mt-4 text-2xl font-semibold">
        {provider ? provider.business_name : "Add a tradesperson"}
      </h1>
      <p className="mt-1 mb-6 text-foreground/70">
        Tenants of the properties you link them to can see their contact
        details.
      </p>
      <ProviderForm
        provider={provider}
        categories={categories.data}
        properties={properties.data.results}
      />
    </>
  );
}
