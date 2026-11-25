"use client";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { labelOptions, PropertyTypeLabel } from "@/constants/properties";
import { Route } from "@/constants/web-routes";
import type { ListingFilters as Filters, Place } from "@/types/listings/models";
import Form from "next/form";

import PlaceFields from "./place-fields";

type ListingFiltersProp = Readonly<{
  places: Place[];
  values: Filters;
}>;

const SORTS = [
  { value: "newest", label: "Newest first" },
  { value: "rent_low", label: "Rent, low to high" },
  { value: "rent_high", label: "Rent, high to low" },
];

export default function ListingFilters({ places, values }: ListingFiltersProp) {
  return (
    <Form
      action={Route.listings}
      scroll={false}
      className="grid gap-4 rounded-2xl border border-default p-4 sm:grid-cols-2 lg:grid-cols-4"
    >
      <TextInput
        label="Search"
        name="q"
        type="search"
        placeholder="Suburb, postcode or name"
        defaultValue={values.q}
        className="sm:col-span-2 lg:col-span-1"
      />
      <PlaceFields
        places={places}
        defaultState={values.state}
        defaultSuburb={values.suburb}
      />
      <SelectInput
        label="Type"
        name="type"
        defaultValue={values.type ?? ""}
        options={[
          { value: "", label: "Any type" },
          ...labelOptions(PropertyTypeLabel),
        ]}
      />
      <TextInput
        label="Lowest rent per week"
        name="min_rent"
        type="number"
        inputMode="decimal"
        min="0"
        placeholder="No minimum"
        defaultValue={values.min_rent}
      />
      <TextInput
        label="Highest rent per week"
        name="max_rent"
        type="number"
        inputMode="decimal"
        min="0"
        placeholder="No maximum"
        defaultValue={values.max_rent}
      />
      <SelectInput
        label="Sort by"
        name="sort"
        defaultValue={values.sort ?? "newest"}
        options={SORTS}
      />
      <div className="flex gap-2 sm:col-span-2 lg:col-span-1 lg:self-end">
        <Button type="submit" className="flex-1">
          Show results
        </Button>
        <ButtonLink href={Route.listings} variant="quiet">
          Clear
        </ButtonLink>
      </div>
    </Form>
  );
}
