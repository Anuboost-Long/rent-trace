import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import { ContactRequestStatusLabel } from "@/constants/contact-requests";
import Form from "next/form";

type RequestsFilterProp = Readonly<{ action: string; status?: string }>;

const OPTIONS = [
  { value: "", label: "All statuses" },
  ...Object.entries(ContactRequestStatusLabel).map(([value, label]) => ({
    value,
    label,
  })),
];

export default function RequestsFilter({ action, status }: RequestsFilterProp) {
  return (
    <Form
      scroll={false}
      action={action}
      className="mb-4 grid gap-4 sm:grid-cols-[12rem_auto] sm:items-end sm:justify-start"
    >
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
