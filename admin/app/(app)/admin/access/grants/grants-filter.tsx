import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import type { PermissionItem } from "@/types/access/models";
import Form from "next/form";

type GrantsFilterProp = Readonly<{
  q?: string;
  permission?: string;
  permissions: PermissionItem[];
}>;

export default function GrantsFilter({
  q,
  permission,
  permissions,
}: GrantsFilterProp) {
  return (
    <Form
      scroll={false}
      action={Route.admin.grants}
      className="mb-4 grid gap-4 sm:grid-cols-[1fr_16rem_auto] sm:items-end"
    >
      <TextInput
        label="Person"
        name="q"
        type="search"
        placeholder="Name or email"
        defaultValue={q}
      />
      <SelectInput
        label="Permission"
        name="permission"
        defaultValue={permission ?? ""}
        options={[
          { value: "", label: "All permissions" },
          ...permissions.map((item) => ({
            value: item.code,
            label: item.name,
          })),
        ]}
      />
      <Button type="submit">Search</Button>
    </Form>
  );
}
