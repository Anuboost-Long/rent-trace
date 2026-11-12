import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import { IssueRoutes, IssueStatusLabel } from "@/constants/maintenance";
import type { MaintenanceAudience } from "@/types/maintenance/models";
import Form from "next/form";

const statusOptions = [
  { value: "", label: "All statuses" },
  ...Object.entries(IssueStatusLabel).map(([value, label]) => ({
    value,
    label,
  })),
];

export default function IssuesFilter({
  audience,
  status,
}: Readonly<{ audience: MaintenanceAudience; status?: string }>) {
  return (
    <Form
      scroll={false}
      action={IssueRoutes[audience].list}
      className="mb-4 grid gap-4 sm:grid-cols-[12rem_auto] sm:items-end"
    >
      <SelectInput
        label="Status"
        name="status"
        defaultValue={status ?? ""}
        options={statusOptions}
      />
      <Button type="submit">Filter</Button>
    </Form>
  );
}
