"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import useUpdateUser from "@/hooks/form/useUpdateUser";
import type { RoleItem } from "@/types/access/models";
import type { UserDetail } from "@/types/users/models";
import { useAtomValue } from "jotai";

import RolePicker, { readRoles } from "../../role-picker";

export default function EditUserForm({
  user,
  roles,
}: Readonly<{ user: UserDetail; roles: RoleItem[] }>) {
  const me = useAtomValue(UserAtom);
  const { pending, error, updateUser } = useUpdateUser(user.id);
  const canChangeRole = !user.is_top_level_admin && me?.id !== user.id;

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        updateUser({
          first_name: String(form.get("first_name")),
          last_name: String(form.get("last_name")),
          phone_number: String(form.get("phone_number")),
          ...(canChangeRole && { roles: readRoles(form) }),
        });
      }}
      className="flex flex-col gap-4"
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <TextInput
          label="First name"
          name="first_name"
          defaultValue={user.first_name}
          required
          error={error?.fields.first_name}
        />
        <TextInput
          label="Last name"
          name="last_name"
          defaultValue={user.last_name}
          required
          error={error?.fields.last_name}
        />
      </div>
      <TextInput
        label="Phone number"
        name="phone_number"
        type="tel"
        autoComplete="off"
        defaultValue={user.phone_number ?? ""}
        error={error?.fields.phone_number}
      />
      <TextInput
        label="Email"
        name="email"
        type="email"
        defaultValue={user.email}
        disabled
      />
      {canChangeRole && (
        <RolePicker
          roles={roles}
          defaultRoles={user.roles}
          error={error?.fields.roles}
        />
      )}
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
      <div className="flex gap-3">
        <Button type="submit" pending={pending}>
          {pending ? "Saving…" : "Save changes"}
        </Button>
        <ButtonLink href={Route.admin.user(user.id)} variant="quiet">
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
