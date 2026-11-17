import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { TenancyRoutes, TenancyStatusLabel } from "@/constants/tenancies";
import type { TenancyAudience } from "@/types/tenancies/models";
import Form from "next/form";

type TenanciesFilterProp = Readonly<{
  audience: TenancyAudience;
  q?: string;
  status?: string;
}>;

const statusOptions = [
  { value: "", label: "All statuses" },
  ...Object.entries(TenancyStatusLabel).map(([value, label]) => ({
    value,
    label,
  })),
];

export default function TenanciesFilter({
  audience,
  q,
  status,
}: TenanciesFilterProp) {
  return (
    <Form
      scroll={false}
      action={TenancyRoutes[audience].list}
      className="mb-4 grid gap-4 sm:grid-cols-[1fr_12rem_auto] sm:items-end"
    >
      <TextInput
        label="Search"
        name="q"
        type="search"
        placeholder="Reference, property, unit or tenant"
        defaultValue={q}
      />
      <SelectInput
        label="Status"
        name="status"
        defaultValue={status ?? ""}
        options={statusOptions}
      />
      <Button type="submit">Search</Button>
    </Form>
  );
}
