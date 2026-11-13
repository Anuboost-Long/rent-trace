import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { TokenStatusLabel } from "@/constants/security";
import { Route } from "@/constants/web-routes";
import Form from "next/form";

type TokensFilterProp = Readonly<{ q?: string; status?: string }>;

export default function TokensFilter({ q, status }: TokensFilterProp) {
  return (
    <Form
      scroll={false}
      action={Route.admin.tokens}
      className="mb-4 grid gap-4 sm:grid-cols-[1fr_12rem_auto] sm:items-end"
    >
      <TextInput
        label="Search"
        name="q"
        type="search"
        placeholder="Person or device"
        defaultValue={q}
      />
      <SelectInput
        label="Status"
        name="status"
        defaultValue={status ?? ""}
        options={[
          { value: "", label: "All statuses" },
          ...Object.entries(TokenStatusLabel).map(([value, label]) => ({
            value,
            label,
          })),
        ]}
      />
      <Button type="submit">Search</Button>
    </Form>
  );
}
