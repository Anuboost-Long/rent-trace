import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { IssueRoutes, IssueStatusLabel } from "@/constants/maintenance";
import type { MaintenanceAudience } from "@/types/maintenance/models";
import clsx from "clsx";
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
  q,
}: Readonly<{ audience: MaintenanceAudience; status?: string; q?: string }>) {
  const canSearch = audience === "admin";
  return (
    <Form
      scroll={false}
      action={IssueRoutes[audience].list}
      className={clsx(
        "mb-4 grid gap-4 sm:items-end",
        canSearch
          ? "sm:grid-cols-[1fr_12rem_auto]"
          : "sm:grid-cols-[12rem_auto] sm:justify-start",
      )}
    >
      {canSearch && (
        <TextInput
          label="Search"
          name="q"
          type="search"
          placeholder="Title, property or suburb"
          defaultValue={q}
        />
      )}
      <SelectInput
        label="Status"
        name="status"
        defaultValue={status ?? ""}
        options={statusOptions}
      />
      <Button type="submit">{canSearch ? "Search" : "Filter"}</Button>
    </Form>
  );
}
