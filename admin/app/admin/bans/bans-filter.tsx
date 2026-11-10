import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { BanStatusLabel, BanTypeLabel } from "@/constants/security";
import { Route } from "@/constants/web-routes";
import Form from "next/form";

type BansFilterProp = Readonly<{ q?: string; status?: string; type?: string }>;

const toOptions = (labels: Record<string, string>, any: string) => [
  { value: "", label: any },
  ...Object.entries(labels).map(([value, label]) => ({ value, label })),
];

export default function BansFilter({ q, status, type }: BansFilterProp) {
  return (
    <Form
      scroll={false}
      action={Route.admin.bans}
      className="mb-4 grid gap-4 sm:grid-cols-[1fr_10rem_12rem_auto] sm:items-end"
    >
      <TextInput
        label="Search"
        name="q"
        type="search"
        placeholder="Email, person or reason"
        defaultValue={q}
      />
      <SelectInput
        label="Status"
        name="status"
        defaultValue={status ?? ""}
        options={toOptions(BanStatusLabel, "All statuses")}
      />
      <SelectInput
        label="Type"
        name="type"
        defaultValue={type ?? ""}
        options={toOptions(BanTypeLabel, "All types")}
      />
      <Button type="submit">Search</Button>
    </Form>
  );
}
