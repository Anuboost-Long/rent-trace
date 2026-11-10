import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { StatusLabel } from "@/constants/roles";
import { Route } from "@/constants/web-routes";
import type { RoleItem } from "@/types/access/models";
import Form from "next/form";

type UsersFilterProp = Readonly<{
  q?: string;
  role?: string;
  status?: string;
  roles: RoleItem[];
}>;

const toOptions = (labels: Record<string, string>, any: string) => [
  { value: "", label: any },
  ...Object.entries(labels).map(([value, label]) => ({ value, label })),
];

export default function UsersFilter({
  q,
  role,
  status,
  roles,
}: UsersFilterProp) {
  return (
    <Form
      scroll={false}
      action={Route.admin.users}
      className="mb-4 grid gap-4 sm:grid-cols-[1fr_10rem_10rem_auto] sm:items-end"
    >
      <TextInput
        label="Search"
        name="q"
        type="search"
        placeholder="Name or email"
        defaultValue={q}
      />
      <SelectInput
        label="Role"
        name="role"
        defaultValue={role ?? ""}
        options={toOptions(
          Object.fromEntries(roles.map((item) => [item.code, item.name])),
          "All roles",
        )}
      />
      <SelectInput
        label="Status"
        name="status"
        defaultValue={status ?? ""}
        options={toOptions(StatusLabel, "All statuses")}
      />
      <Button type="submit">Search</Button>
    </Form>
  );
}
