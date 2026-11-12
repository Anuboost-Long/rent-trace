"use client";
import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import { labelOptions, PropertyTypeLabel } from "@/constants/properties";
import { Route } from "@/constants/web-routes";
import type { Place } from "@/types/listings/models";
import { Search } from "lucide-react";
import Form from "next/form";

import PlaceFields from "./place-fields";

type SearchFormProp = Readonly<{ places: Place[] }>;

export default function SearchForm({ places }: SearchFormProp) {
  return (
    <Form
      action={Route.listings}
      className="grid gap-3 rounded-2xl border border-foreground/15 p-3 sm:grid-cols-2 sm:items-end"
    >
      <PlaceFields places={places} />
      <SelectInput
        label="Type"
        name="type"
        options={[
          { value: "", label: "Any type" },
          ...labelOptions(PropertyTypeLabel),
        ]}
      />
      <Button type="submit" className="gap-2">
        <Search aria-hidden className="size-4" />
        Search
      </Button>
    </Form>
  );
}
