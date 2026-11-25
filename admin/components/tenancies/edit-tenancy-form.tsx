"use client";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import { TenancyRoutes } from "@/constants/tenancies";
import useUpdateTenancy from "@/hooks/form/useUpdateTenancy";
import type { TenancyAudience, TenancyDetail } from "@/types/tenancies/models";

import TenancyTermsFields, { readTerms } from "./tenancy-terms-fields";

type EditTenancyFormProp = Readonly<{
  audience: TenancyAudience;
  tenancy: TenancyDetail;
}>;

export default function EditTenancyForm({
  audience,
  tenancy,
}: EditTenancyFormProp) {
  const { pending, error, save } = useUpdateTenancy(audience, tenancy.id);
  const fields = error?.fields ?? {};

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        void save(readTerms(new FormData(event.currentTarget)));
      }}
      className="flex flex-col gap-4"
    >
      <TenancyTermsFields
        defaults={tenancy}
        errors={fields}
        lockStart={tenancy.status === "ACTIVE"}
      />
      {error && Object.keys(fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
      <div className="flex gap-3">
        <Button type="submit" pending={pending}>
          {pending ? "Saving…" : "Save changes"}
        </Button>
        <ButtonLink
          href={TenancyRoutes[audience].detail(tenancy.id)}
          variant="quiet"
        >
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
