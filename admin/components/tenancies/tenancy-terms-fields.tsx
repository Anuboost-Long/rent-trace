"use client";
import DateInput from "@/components/common/inputs/date-input";
import SelectInput from "@/components/common/inputs/select-input";
import TextArea from "@/components/common/inputs/text-area-input";
import TextInput from "@/components/common/inputs/text-input";
import { labelOptions, RentFrequencyLabel } from "@/constants/properties";
import type { TenancyTerms } from "@/types/tenancies/models";
import { addDays } from "@/utils/calendar";
import { useState } from "react";

type TenancyTermsFieldsProp = Readonly<{
  defaults: Partial<TenancyTerms>;
  errors: Record<string, string>;
  lockStart?: boolean;
}>;

const text = (form: FormData, name: string) =>
  String(form.get(name) ?? "").trim();

export const readTerms = (form: FormData): TenancyTerms => ({
  start_date: text(form, "start_date"),
  end_date: text(form, "end_date") || null,
  notes: text(form, "notes") || null,
  rent_amount: text(form, "rent_amount") || null,
  rent_frequency: text(form, "rent_frequency") || null,
  bond_amount: text(form, "bond_amount") || null,
});

export default function TenancyTermsFields({
  defaults,
  errors,
  lockStart,
}: TenancyTermsFieldsProp) {
  const [startDate, setStartDate] = useState(defaults.start_date ?? "");

  return (
    <>
      <div className="grid gap-4 sm:grid-cols-2">
        <DateInput
          label="Start date"
          name="start_date"
          defaultValue={defaults.start_date}
          disabled={lockStart}
          required
          onValueChange={setStartDate}
          error={errors.start_date}
        />
        <DateInput
          label="End date (optional)"
          name="end_date"
          defaultValue={defaults.end_date ?? ""}
          min={startDate ? addDays(startDate, 1) : undefined}
          error={errors.end_date}
        />
      </div>
      {lockStart && (
        <p className="-mt-2 text-sm text-foreground/60">
          The start date can&apos;t change once the tenancy has started.
        </p>
      )}
      <div
        key={`${defaults.rent_amount}-${defaults.rent_frequency}`}
        className="grid gap-4 sm:grid-cols-2"
      >
        <TextInput
          label="Rent in dollars (optional)"
          name="rent_amount"
          type="number"
          inputMode="decimal"
          min="0.01"
          step="0.01"
          defaultValue={defaults.rent_amount ?? ""}
          error={errors.rent_amount}
        />
        <SelectInput
          label="Rent is paid"
          name="rent_frequency"
          options={[
            { value: "", label: "Not set" },
            ...labelOptions(RentFrequencyLabel),
          ]}
          defaultValue={defaults.rent_frequency ?? ""}
          error={errors.rent_frequency}
        />
      </div>
      <TextInput
        label="Bond in dollars (optional)"
        name="bond_amount"
        type="number"
        inputMode="decimal"
        min="0.01"
        step="0.01"
        defaultValue={defaults.bond_amount ?? ""}
        error={errors.bond_amount}
      />
      <TextArea
        label="Notes (optional, only you and admins see these)"
        name="notes"
        defaultValue={defaults.notes ?? ""}
        error={errors.notes}
      />
    </>
  );
}
