"use client";
import { handleSearchSuburbs } from "@/api/services/locations/serve-action";
import ComboboxInput from "@/components/common/inputs/combobox-input";
import SelectInput from "@/components/common/inputs/select-input";
import TextAreaInput from "@/components/common/inputs/text-area-input";
import TextInput from "@/components/common/inputs/text-input";
import { AustralianStates, DEFAULT_COUNTRY } from "@/constants/locations";
import { labelOptions, PropertyTypeLabel } from "@/constants/properties";
import type { ApiFailure } from "@/types/api/common";
import type { PropertyBody, PropertySummary } from "@/types/properties/models";
import { useCallback, useState } from "react";

type PropertyFieldsProp = Readonly<{
  defaults?: Partial<
    Pick<
      PropertySummary,
      | "property_name"
      | "address_line_1"
      | "address_line_2"
      | "suburb"
      | "state"
      | "postcode"
      | "property_type"
    > & { public_description: string | null; private_notes: string | null }
  >;
  error: ApiFailure | null;
}>;

export const readPropertyFields = (form: FormData): PropertyBody => {
  const text = (name: keyof PropertyBody) => String(form.get(name) ?? "");
  return {
    property_name: text("property_name"),
    address_line_1: text("address_line_1"),
    address_line_2: text("address_line_2"),
    suburb: text("suburb"),
    state: text("state"),
    postcode: text("postcode"),
    country: DEFAULT_COUNTRY,
    property_type: text("property_type"),
    public_description: text("public_description"),
    private_notes: text("private_notes"),
  };
};

export default function PropertyFields({
  defaults,
  error,
}: PropertyFieldsProp) {
  const fieldError = (name: keyof PropertyBody) => error?.fields[name];
  const [state, setState] = useState(defaults?.state ?? "");
  const [suburb, setSuburb] = useState(defaults?.suburb ?? "");
  const [postcode, setPostcode] = useState(defaults?.postcode ?? "");

  const findSuburbs = useCallback(
    async (query: string) => {
      const { data } = await handleSearchSuburbs(state, query);
      return (data ?? []).map((found) => ({
        value: found.suburb,
        label: found.suburb,
        hint: found.postcode,
      }));
    },
    [state],
  );

  return (
    <>
      <TextInput
        label="Property name (optional)"
        name="property_name"
        defaultValue={defaults?.property_name ?? ""}
        placeholder="For example, Smith Street house"
        error={fieldError("property_name")}
      />
      <SelectInput
        label="Type"
        name="property_type"
        options={labelOptions(PropertyTypeLabel)}
        defaultValue={defaults?.property_type}
        error={fieldError("property_type")}
      />
      <fieldset className="flex flex-col gap-4">
        <legend className="mb-1 text-sm font-semibold">Address</legend>
        <TextInput
          label="Street address"
          name="address_line_1"
          defaultValue={defaults?.address_line_1}
          required
          error={fieldError("address_line_1")}
        />
        <TextInput
          label="Unit, building or floor (optional)"
          name="address_line_2"
          defaultValue={defaults?.address_line_2 ?? ""}
          error={fieldError("address_line_2")}
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <ComboboxInput
            label="State or territory"
            name="state"
            value={state}
            options={AustralianStates}
            placeholder="Search states"
            error={fieldError("state")}
            onSelect={(option) => {
              if (option.value === state) return;
              setState(option.value);
              setSuburb("");
              setPostcode("");
            }}
          />
          <ComboboxInput
            key={state}
            label="Suburb"
            name="suburb"
            value={suburb}
            loadOptions={findSuburbs}
            disabled={!state}
            placeholder={state ? "Search suburbs" : "Choose a state first"}
            emptyMessage="No suburbs match in this state"
            error={fieldError("suburb")}
            onSelect={(option) => {
              setSuburb(option.value);
              setPostcode(option.hint ?? "");
            }}
          />
        </div>
        <TextInput
          label="Postcode"
          name="postcode"
          inputMode="numeric"
          value={postcode}
          onChange={(event) => setPostcode(event.target.value)}
          required
          className="sm:max-w-40"
          error={fieldError("postcode")}
        />
      </fieldset>
      <TextAreaInput
        label="Public description (optional)"
        name="public_description"
        defaultValue={defaults?.public_description ?? ""}
        error={fieldError("public_description")}
      />
      <TextAreaInput
        label="Private notes (optional)"
        name="private_notes"
        defaultValue={defaults?.private_notes ?? ""}
        error={fieldError("private_notes")}
      />
    </>
  );
}
