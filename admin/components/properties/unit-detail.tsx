import { handleGetProperty } from "@/api/services/properties/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import ContentSkeleton from "@/components/layout/content-skeleton";
import { PropertyAccess, PropertyRoutes } from "@/constants/properties";
import type { PropertyAudience } from "@/types/properties/models";
import { propertyTitle } from "@/utils/property-address";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import PropertyFilesSection from "./property-files-section";
import UnitPanel from "./unit-panel";

type UnitDetailProp = Readonly<{
  audience: PropertyAudience;
  params: Promise<{ id: string; unitId: string }>;
}>;

export default function UnitDetailPage(props: UnitDetailProp) {
  return (
    <Suspense fallback={<ContentSkeleton />}>
      <UnitDetail {...props} />
    </Suspense>
  );
}

async function UnitDetail({ audience, params }: UnitDetailProp) {
  const { id, unitId } = await params;
  const { data: property, error } = await handleGetProperty(id, audience);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }
  const unit = property.units.find(
    (candidate) => String(candidate.id) === unitId,
  );
  if (!unit) notFound();

  const unitFiles = property.files.filter((file) => file.unit_id === unit.id);
  const showsPropertyPhotos =
    !unitFiles.some((file) => file.kind === "PHOTO") &&
    property.files.some(
      (file) => file.unit_id === null && file.kind === "PHOTO",
    );

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Properties", href: PropertyRoutes[audience].list },
          {
            label: propertyTitle(property),
            href: PropertyRoutes[audience].detail(property.id),
          },
          { label: unit.name },
        ]}
      />
      <UnitPanel audience={audience} propertyId={property.id} unit={unit} />
      {showsPropertyPhotos && (
        <p className="mt-6 text-sm text-foreground/70">
          This unit has no photos yet, so the property&apos;s photos are shown
          for it.
        </p>
      )}
      <PropertyFilesSection
        audience={audience}
        propertyId={property.id}
        unitId={unit.id}
        files={unitFiles}
        managePermission={PropertyAccess[audience].update}
      />
    </>
  );
}
