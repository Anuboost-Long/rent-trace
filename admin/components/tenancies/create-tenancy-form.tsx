"use client";
import Button from "@/components/common/button";
import ComboboxInput from "@/components/common/inputs/combobox-input";
import SelectInput from "@/components/common/inputs/select-input";
import useCreateTenancy, {
  findProperties,
  type InitialProperty,
} from "@/hooks/form/useCreateTenancy";
import type { TenancyAudience } from "@/types/tenancies/models";

import TenancyTermsFields, { readTerms } from "./tenancy-terms-fields";

type CreateTenancyFormProp = Readonly<{
  audience: TenancyAudience;
  initial: InitialProperty | null;
}>;

export default function CreateTenancyForm({
  audience,
  initial,
}: CreateTenancyFormProp) {
  const tenancy = useCreateTenancy(audience, initial);
  const fields = tenancy.error?.fields ?? {};
  const unit = tenancy.units.find((item) => String(item.id) === tenancy.unitId);

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        tenancy.createTenancy(readTerms(new FormData(event.currentTarget)));
      }}
      className="flex flex-col gap-4"
    >
      <ComboboxInput
        label="Property"
        name="property"
        value={tenancy.property?.label ?? ""}
        loadOptions={findProperties[audience]}
        placeholder="Search by name or address"
        emptyMessage="No properties match"
        onSelect={tenancy.chooseProperty}
      />
      {tenancy.property &&
        (tenancy.units.length === 0 ? (
          <p className="text-sm text-fg-secondary">
            This property has no units yet. Add a unit first.
          </p>
        ) : (
          <SelectInput
            key={tenancy.property.value}
            label="Unit"
            name="unit"
            value={tenancy.unitId}
            onValueChange={tenancy.setUnitId}
            error={fields.property_unit_id}
            options={[
              { value: "", label: "Choose a unit" },
              ...tenancy.units.map((unit) => ({
                value: String(unit.id),
                label: unit.name,
              })),
            ]}
          />
        ))}
      <TenancyTermsFields
        defaults={{
          rent_amount: unit?.rent_amount ?? null,
          rent_frequency: unit?.rent_frequency ?? null,
        }}
        errors={fields}
      />
      {tenancy.error && Object.keys(fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {tenancy.error.message}
        </p>
      )}
      <Button
        type="submit"
        pending={tenancy.pending}
        disabled={tenancy.unitId === ""}
      >
        {tenancy.pending ? "Creating tenancy…" : "Create tenancy"}
      </Button>
    </form>
  );
}
