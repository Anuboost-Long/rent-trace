"use client";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import useGrantForm from "@/hooks/form/useGrantForm";
import type { PermissionItem } from "@/types/access/models";
import type { UserOption } from "@/types/users/models";

type GrantFormProp = Readonly<{
  users: UserOption[];
  permissions: PermissionItem[];
  defaultPermission?: string;
}>;

export default function GrantForm({
  users,
  permissions,
  defaultPermission,
}: GrantFormProp) {
  const { pending, error, grant } = useGrantForm();

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        grant(
          Number(form.get("user")),
          String(form.get("permission")),
          String(form.get("reason")),
        );
      }}
      className="grid gap-4"
    >
      <SelectInput
        label="Person"
        name="user"
        options={users.map((user) => ({
          value: String(user.id),
          label: `${user.first_name} ${user.last_name} (${user.email})`,
        }))}
      />
      <SelectInput
        label="Permission"
        name="permission"
        defaultValue={defaultPermission}
        options={permissions.map((item) => ({
          value: item.code,
          label: `${item.name} (${item.code})`,
        }))}
        error={error?.fields.permission}
      />
      <TextInput
        label="Reason"
        name="reason"
        placeholder="Why they need it"
        required
        error={error?.fields.reason}
      />
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-red-600">
          {error.message}
        </p>
      )}
      <div className="flex gap-3">
        <Button type="submit" pending={pending} disabled={users.length === 0}>
          {pending ? "Granting…" : "Grant permission"}
        </Button>
        <ButtonLink href={Route.admin.grants} variant="quiet">
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
