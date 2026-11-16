import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import type { ServiceCategory } from "@/types/providers/models";
import Form from "next/form";

type ProviderFilterProp = Readonly<{
  action: string;
  categories: ServiceCategory[];
  q?: string;
  category?: string;
}>;

export default function ProviderFilter({
  action,
  categories,
  q,
  category,
}: ProviderFilterProp) {
  return (
    <Form
      scroll={false}
      action={action}
      className="mb-4 grid gap-4 sm:grid-cols-[1fr_12rem_auto] sm:items-end"
    >
      <TextInput
        label="Search"
        name="q"
        type="search"
        placeholder="Business or contact name"
        defaultValue={q}
      />
      <SelectInput
        label="Trade"
        name="category"
        defaultValue={category ?? ""}
        options={[
          { value: "", label: "All trades" },
          ...categories.map(({ code, name }) => ({ value: code, label: name })),
        ]}
      />
      <Button type="submit">Search</Button>
    </Form>
  );
}
