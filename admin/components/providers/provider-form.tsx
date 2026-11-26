"use client";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import CheckInput from "@/components/common/inputs/check-input";
import TextArea from "@/components/common/inputs/text-area-input";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import useSaveProvider from "@/hooks/form/useSaveProvider";
import type { PropertySummary } from "@/types/properties/models";
import type {
  ProviderBody,
  ServiceCategory,
  ServiceProvider,
} from "@/types/providers/models";

import PropertyLinkFields from "./property-link-fields";

type ProviderFormProp = Readonly<{
  provider?: ServiceProvider;
  categories: ServiceCategory[];
  properties: PropertySummary[];
}>;

const text = (form: FormData, name: string) =>
  String(form.get(name) ?? "").trim() || null;

const readProvider = (
  form: FormData,
  properties: PropertySummary[],
): ProviderBody => ({
  business_name: String(form.get("business_name") ?? "").trim(),
  contact_name: text(form, "contact_name"),
  phone_number: text(form, "phone_number"),
  email: text(form, "email"),
  website: text(form, "website"),
  address: text(form, "address"),
  description: text(form, "description"),
  category_codes: form.getAll("category").map(String),
  properties: properties
    .filter((property) => form.has(`linked_${property.id}`))
    .map((property) => ({
      property_id: property.id,
      is_recommended: form.has(`preferred_${property.id}`),
      contract_notes: text(form, `notes_${property.id}`),
    })),
});

export default function ProviderForm({
  provider,
  categories,
  properties,
}: ProviderFormProp) {
  const { pending, error, save } = useSaveProvider(provider?.id);
  const fields = error?.fields ?? {};
  const linkFor = (propertyId: number) =>
    provider?.properties.find((link) => link.property_id === propertyId);
  const hasCategory = (code: string) =>
    provider?.categories.some((category) => category.code === code);

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        void save(readProvider(new FormData(event.currentTarget), properties));
      }}
      className="flex max-w-xl flex-col gap-4"
    >
      <TextInput
        label="Business name"
        name="business_name"
        defaultValue={provider?.business_name}
        required
        error={fields.business_name}
      />
      <div className="grid gap-4 sm:grid-cols-2">
        <TextInput
          label="Contact person"
          name="contact_name"
          defaultValue={provider?.contact_name ?? ""}
          error={fields.contact_name}
        />
        <TextInput
          label="Phone"
          name="phone_number"
          type="tel"
          defaultValue={provider?.phone_number ?? ""}
          error={fields.phone_number}
        />
        <TextInput
          label="Email"
          name="email"
          type="email"
          defaultValue={provider?.email ?? ""}
          error={fields.email}
        />
        <TextInput
          label="Website"
          name="website"
          type="url"
          placeholder="https://"
          defaultValue={provider?.website ?? ""}
          error={fields.website}
        />
      </div>
      <TextArea
        label="Address (optional)"
        name="address"
        rows={2}
        defaultValue={provider?.address ?? ""}
        error={fields.address}
      />
      <TextArea
        label="About them (optional)"
        name="description"
        defaultValue={provider?.description ?? ""}
        error={fields.description}
      />

      <fieldset>
        <legend className="mb-2 text-sm font-medium">What they do</legend>
        <div className="grid gap-2 sm:grid-cols-2">
          {categories.map((category) => (
            <CheckInput
              key={category.code}
              label={category.name}
              name="category"
              value={category.code}
              defaultChecked={hasCategory(category.code)}
            />
          ))}
        </div>
        {fields.category_codes && (
          <p className="mt-1 text-sm text-error">{fields.category_codes}</p>
        )}
      </fieldset>

      <fieldset>
        <legend className="text-sm font-medium">Properties they serve</legend>
        <p className="mt-1 mb-2 text-sm text-fg-secondary">
          Tenants see their contact details for these properties. Notes about
          their contract stay private to you.
        </p>
        {properties.length === 0 ? (
          <p className="text-sm text-fg-tertiary">
            Add a property first to link them to it.
          </p>
        ) : (
          <ul className="divide-y divide-default rounded-xl border border-default">
            {properties.map((property) => (
              <PropertyLinkFields
                key={property.id}
                property={property}
                link={linkFor(property.id)}
              />
            ))}
          </ul>
        )}
        {fields.properties && (
          <p className="mt-1 text-sm text-error">{fields.properties}</p>
        )}
      </fieldset>

      {error && Object.keys(fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
      <div className="flex gap-3">
        <Button type="submit" pending={pending}>
          {pending ? "Saving…" : provider ? "Save changes" : "Add tradesperson"}
        </Button>
        <ButtonLink href={Route.landlord.providers} variant="quiet">
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
