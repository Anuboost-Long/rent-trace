"use client";
import { handleUpdateProperty } from "@/api/services/properties/serve-action";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import SelectInput from "@/components/common/inputs/select-input";
import {
  labelOptions,
  PropertyRoutes,
  PropertyStatusLabel,
} from "@/constants/properties";
import useSaveProperty from "@/hooks/form/useSaveProperty";
import type {
  PropertyAudience,
  PropertyDetail,
  PropertyStatus,
  UpdatePropertyBody,
} from "@/types/properties/models";

import PropertyFields, { readPropertyFields } from "./property-fields";

type EditPropertyFormProp = Readonly<{
  audience: PropertyAudience;
  property: PropertyDetail;
}>;

export default function EditPropertyForm({
  audience,
  property,
}: EditPropertyFormProp) {
  const { pending, error, save } = useSaveProperty(
    (body: UpdatePropertyBody) =>
      handleUpdateProperty(property.id, body, audience),
    audience,
  );

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        save({
          ...readPropertyFields(form),
          property_status: String(
            form.get("property_status"),
          ) as PropertyStatus,
        });
      }}
      className="flex flex-col gap-4"
    >
      <SelectInput
        label="Status"
        name="property_status"
        options={labelOptions(PropertyStatusLabel)}
        defaultValue={property.property_status}
        error={error?.fields.property_status}
      />
      <PropertyFields defaults={property} error={error} />
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
      <div className="flex gap-3">
        <Button type="submit" pending={pending}>
          {pending ? "Saving…" : "Save changes"}
        </Button>
        <ButtonLink
          href={PropertyRoutes[audience].detail(property.id)}
          variant="quiet"
        >
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
