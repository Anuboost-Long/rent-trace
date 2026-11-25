import { handleGetProperty } from "@/api/services/properties/serve-action";
import ButtonLink from "@/components/common/button-link";
import Can from "@/components/common/can";
import LocalTime from "@/components/common/local-time";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { DetailSkeleton } from "@/components/layout/page-skeletons";
import PropertyProvidersSection from "@/components/providers/property-providers-section";
import {
  PropertyAccess,
  PropertyRoutes,
  PropertyStatusLabel,
  PropertyTypeLabel,
} from "@/constants/properties";
import { TenancyAccess, TenancyRoutes } from "@/constants/tenancies";
import type { PropertyAudience } from "@/types/properties/models";
import {
  formatAddress,
  ownerName,
  propertyTitle,
} from "@/utils/property-address";
import { FilePlus2, Pencil } from "lucide-react";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import DeletePropertyButton from "./delete-property-button";
import ListingSection from "./listing-section";
import PropertyFilesSection from "./property-files-section";
import UnitsSection from "./units-section";

type PropertyDetailProp = Readonly<{
  audience: PropertyAudience;
  params: Promise<{ id: string }>;
}>;

export default function PropertyDetailPage(props: PropertyDetailProp) {
  return (
    <Suspense fallback={<DetailSkeleton />}>
      <PropertyDetail {...props} />
    </Suspense>
  );
}

async function PropertyDetail({ audience, params }: PropertyDetailProp) {
  const { id } = await params;
  const { data: property, error } = await handleGetProperty(id, audience);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-error">
        {error.message}
      </p>
    );
  }

  const title = propertyTitle(property);
  const access = PropertyAccess[audience];
  const details: [string, React.ReactNode][] = [
    ["Address", formatAddress(property)],
    ["Type", PropertyTypeLabel[property.property_type]],
    ["Status", PropertyStatusLabel[property.property_status]],
    [
      property.owners.length > 1 ? "Owners" : "Owner",
      property.owners.length === 0
        ? "—"
        : property.owners.map((entry) => (
            <p key={entry.owner.id}>
              {ownerName(entry.owner)}{" "}
              <span className="text-fg-tertiary">({entry.owner.email})</span>
            </p>
          )),
    ],
    ["Public description", property.public_description ?? "—"],
    ["Private notes", property.private_notes ?? "—"],
    ["Created", <LocalTime key="Created" iso={property.created_at} />],
    [
      "Last changed",
      <LocalTime key="Last changed" iso={property.updated_at} />,
    ],
  ];

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Properties", href: PropertyRoutes[audience].list },
          { label: title },
        ]}
      />
      <div className="mt-4 mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <Can permission={access.update}>
          <div className="flex gap-2">
            <Can permission={TenancyAccess[audience].create}>
              <ButtonLink
                href={`${TenancyRoutes[audience].create}?property=${property.id}`}
                variant="quiet"
                className="gap-2"
              >
                <FilePlus2 aria-hidden className="size-4" />
                New tenancy
              </ButtonLink>
            </Can>
            <ButtonLink
              href={PropertyRoutes[audience].edit(property.id)}
              variant="quiet"
              className="gap-2"
            >
              <Pencil aria-hidden className="size-4" />
              Edit
            </ButtonLink>
            {audience === "admin" && (
              <DeletePropertyButton id={property.id} title={title} />
            )}
          </div>
        </Can>
      </div>
      <dl className="divide-y divide-default rounded-xl border border-default">
        {details.map(([label, value]) => (
          <div key={label} className="grid gap-1 p-4 sm:grid-cols-[12rem_1fr]">
            <dt className="text-sm text-fg-secondary">{label}</dt>
            <dd className="whitespace-pre-line">{value}</dd>
          </div>
        ))}
      </dl>
      <ListingSection
        audience={audience}
        propertyId={property.id}
        status={property.listing_status}
      />
      <PropertyFilesSection
        audience={audience}
        propertyId={property.id}
        files={property.files.filter((file) => file.unit_id === null)}
        managePermission={access.update}
      />
      {audience === "landlord" && (
        <PropertyProvidersSection propertyId={property.id} />
      )}
      <UnitsSection
        audience={audience}
        propertyId={property.id}
        units={property.units}
        files={property.files}
      />
    </>
  );
}
