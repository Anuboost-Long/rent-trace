"use client";
import { handleCreateProperty } from "@/api/services/properties/serve-action";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import SelectInput from "@/components/common/inputs/select-input";
import { PropertyRoutes } from "@/constants/properties";
import { Route } from "@/constants/web-routes";
import {
  uploadPropertyFiles,
  type UploadFailure,
} from "@/hooks/form/usePropertyFiles";
import useSaveProperty from "@/hooks/form/useSaveProperty";
import useStagedFiles from "@/hooks/form/useStagedFiles";
import type { OwnerOption, PropertyAudience } from "@/types/properties/models";
import { ownerName } from "@/utils/property-address";
import Link from "next/link";
import { useState } from "react";

import FilePicker from "./file-picker";
import PropertyFields, { readPropertyFields } from "./property-fields";

type CreatePropertyFormProp = Readonly<{
  audience: PropertyAudience;
  owners?: OwnerOption[];
}>;

export default function CreatePropertyForm({
  audience,
  owners = [],
}: CreatePropertyFormProp) {
  const { pending, error, save } = useSaveProperty(
    (body: Parameters<typeof handleCreateProperty>[0]) =>
      handleCreateProperty(body, audience),
    audience,
  );
  const staged = useStagedFiles();
  const [unsent, setUnsent] = useState<{
    propertyId: number;
    failures: UploadFailure[];
  } | null>(null);

  if (audience === "admin" && owners.length === 0) {
    return (
      <p>
        There are no active landlords yet.{" "}
        <Link href={Route.admin.users_new} className="underline">
          Create a landlord account
        </Link>{" "}
        first.
      </p>
    );
  }

  if (unsent) {
    return (
      <div role="alert" className="rounded-xl border border-foreground/15 p-6">
        <h2 className="text-lg font-semibold">
          Property created, but some files didn&apos;t upload
        </h2>
        <ul className="mt-3 space-y-0.5 text-sm">
          {unsent.failures.map((failure) => (
            <li key={failure.id}>
              {failure.name}: {failure.message}
            </li>
          ))}
        </ul>
        <p className="mt-3 text-sm text-foreground/70">
          You can add them again from the property page.
        </p>
        <ButtonLink
          href={PropertyRoutes[audience].detail(unsent.propertyId)}
          className="mt-4"
        >
          Open property
        </ButtonLink>
      </div>
    );
  }

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const fields = readPropertyFields(form);
        save(
          audience === "admin"
            ? { ...fields, owner_id: Number(form.get("owner_id")) }
            : fields,
          async (saved) => {
            const failures = await uploadPropertyFiles(
              audience,
              saved.id,
              staged.items,
            );
            if (failures.length === 0) return true;
            setUnsent({ propertyId: saved.id, failures });
            return false;
          },
        );
      }}
      className="flex flex-col gap-4"
    >
      {audience === "admin" && (
        <SelectInput
          label="Landlord"
          name="owner_id"
          options={owners.map((owner) => ({
            value: String(owner.id),
            label: `${ownerName(owner)} (${owner.email})`,
          }))}
          error={error?.fields.owner_id}
        />
      )}
      <PropertyFields error={error} />
      <FilePicker staged={staged} disabled={pending} />
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-red-600">
          {error.message}
        </p>
      )}
      <Button type="submit" pending={pending}>
        {pending
          ? staged.items.length > 0
            ? "Creating and uploading…"
            : "Creating property…"
          : "Create property"}
      </Button>
    </form>
  );
}
