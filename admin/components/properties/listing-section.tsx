"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import {
  ListingStatusHint,
  ListingStatusLabel,
  PropertyAccess,
  PUBLIC_LISTING_STATUSES,
} from "@/constants/properties";
import useListingStatus from "@/hooks/form/useListingStatus";
import type { PropertyAudience } from "@/types/properties/models";
import { useAtomValue } from "jotai";
import { ExternalLink } from "lucide-react";
import Link from "next/link";

type ListingSectionProp = Readonly<{
  audience: PropertyAudience;
  propertyId: number;
  status: string;
}>;

const ADMIN_ONLY = ["SUSPENDED", "ARCHIVED"];
const LANDLORD_OPTIONS = [
  "DRAFT",
  "AVAILABLE",
  "PARTIALLY_AVAILABLE",
  "FULLY_OCCUPIED",
  "UNLISTED",
];

export default function ListingSection({
  audience,
  propertyId,
  status,
}: ListingSectionProp) {
  const me = useAtomValue(UserAtom);
  const { pending, error, change } = useListingStatus(audience, propertyId);
  const canPublish = me?.permissions.includes(PropertyAccess[audience].publish);
  const locked = audience === "landlord" && ADMIN_ONLY.includes(status);
  const options = (
    audience === "admin"
      ? [...LANDLORD_OPTIONS, ...ADMIN_ONLY]
      : LANDLORD_OPTIONS
  ).map((value) => ({ value, label: ListingStatusLabel[value] }));
  const isPublic = PUBLIC_LISTING_STATUSES.includes(status);

  return (
    <section aria-labelledby="listing-heading" className="mt-10">
      <h2 id="listing-heading" className="text-section">
        Public listing
      </h2>
      <div className="mt-3 space-y-4 rounded-xl border border-default p-4">
        <div>
          <p className="font-medium">{ListingStatusLabel[status]}</p>
          <p className="text-sm text-fg-secondary">
            {ListingStatusHint[status]}
          </p>
          {isPublic && (
            <Link
              href={`/properties/${propertyId}`}
              target="_blank"
              className="mt-2 inline-flex items-center gap-1.5 text-sm font-medium underline underline-offset-2"
            >
              View public listing
              <ExternalLink aria-hidden className="size-3.5" />
            </Link>
          )}
        </div>
        {locked && (
          <p className="text-sm text-fg-secondary">
            An admin has locked this listing. Contact support to change it.
          </p>
        )}
        {canPublish && !locked && (
          <form
            onSubmit={(event) => {
              event.preventDefault();
              change(
                String(new FormData(event.currentTarget).get("listing_status")),
              );
            }}
            className="flex flex-wrap items-end gap-3"
          >
            <SelectInput
              key={status}
              label="Listing status"
              name="listing_status"
              options={options}
              defaultValue={status}
              error={error?.fields.listing_status}
              className="max-w-xs"
            />
            <Button type="submit" pending={pending}>
              {pending ? "Saving…" : "Update listing"}
            </Button>
          </form>
        )}
        {error && !error.fields.listing_status && (
          <p role="alert" className="text-sm text-error">
            {error.message}
          </p>
        )}
        {canPublish && !locked && (
          <p className="text-sm text-fg-secondary">
            To go live the property must be active and have at least one unit
            set to be shown publicly.
          </p>
        )}
      </div>
    </section>
  );
}
