"use client";
import Button from "@/components/common/button";
import ComboboxInput from "@/components/common/inputs/combobox-input";
import DateInput from "@/components/common/inputs/date-input";
import SelectInput from "@/components/common/inputs/select-input";
import TextArea from "@/components/common/inputs/text-area-input";
import useCreateTenancy, {
  findProperties,
  type InitialProperty,
} from "@/hooks/form/useCreateTenancy";
import type { TenancyAudience } from "@/types/tenancies/models";
import { addDays } from "@/utils/calendar";
import { useState } from "react";

type CreateTenancyFormProp = Readonly<{
  audience: TenancyAudience;
  initial: InitialProperty | null;
}>;

export default function CreateTenancyForm({
  audience,
  initial,
}: CreateTenancyFormProp) {
  const tenancy = useCreateTenancy(audience, initial);
  const [startDate, setStartDate] = useState("");
  const fields = tenancy.error?.fields ?? {};

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        tenancy.createTenancy({
          start_date: String(form.get("start_date")),
          end_date: String(form.get("end_date") ?? "") || undefined,
          notes: String(form.get("notes") ?? "").trim() || undefined,
        });
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
          <p className="text-sm text-foreground/70">
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
      <div className="grid gap-4 sm:grid-cols-2">
        <DateInput
          label="Start date"
          name="start_date"
          required
          onValueChange={setStartDate}
          error={fields.start_date}
        />
        <DateInput
          label="End date (optional)"
          name="end_date"
          min={startDate ? addDays(startDate, 1) : undefined}
          error={fields.end_date}
        />
      </div>
      <TextArea label="Notes (optional)" name="notes" error={fields.notes} />
      {tenancy.error && Object.keys(fields).length === 0 && (
        <p role="alert" className="text-sm text-red-600">
          {tenancy.error.message}
        </p>
      )}
      <Button
        type="submit"
        pending={tenancy.pending}
        disabled={tenancy.unitId === "" || startDate === ""}
      >
        {tenancy.pending ? "Creating tenancy…" : "Create tenancy"}
      </Button>
    </form>
  );
}
