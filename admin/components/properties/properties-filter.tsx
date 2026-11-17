import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import {
  labelOptions,
  PropertyRoutes,
  PropertyStatusLabel,
} from "@/constants/properties";
import type { PropertyAudience } from "@/types/properties/models";
import Form from "next/form";

type PropertiesFilterProp = Readonly<{
  audience: PropertyAudience;
  q?: string;
  status?: string;
}>;

export default function PropertiesFilter({
  audience,
  q,
  status,
}: PropertiesFilterProp) {
  return (
    <Form
      scroll={false}
      action={PropertyRoutes[audience].list}
      className="mb-4 grid gap-4 sm:grid-cols-[1fr_12rem_auto] sm:items-end"
    >
      <TextInput
        label="Search"
        name="q"
        type="search"
        placeholder="Name, address or owner"
        defaultValue={q}
      />
      <SelectInput
        label="Status"
        name="status"
        defaultValue={status ?? ""}
        options={[
          { value: "", label: "All statuses" },
          ...labelOptions(PropertyStatusLabel),
        ]}
      />
      <Button type="submit">Search</Button>
    </Form>
  );
}
