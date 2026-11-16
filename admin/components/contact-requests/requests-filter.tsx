import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { ContactRequestStatusLabel } from "@/constants/contact-requests";
import clsx from "clsx";
import Form from "next/form";

type RequestsFilterProp = Readonly<{
  action: string;
  status?: string;
  q?: string;
  canSearch?: boolean;
}>;

const OPTIONS = [
  { value: "", label: "All statuses" },
  ...Object.entries(ContactRequestStatusLabel).map(([value, label]) => ({
    value,
    label,
  })),
];

export default function RequestsFilter({
  action,
  status,
  q,
  canSearch,
}: RequestsFilterProp) {
  return (
    <Form
      scroll={false}
      action={action}
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
          placeholder="Property, suburb or tenant"
          defaultValue={q}
        />
      )}
      <SelectInput
        label="Status"
        name="status"
        defaultValue={status ?? ""}
        options={OPTIONS}
      />
      <Button type="submit">Show requests</Button>
    </Form>
  );
}
