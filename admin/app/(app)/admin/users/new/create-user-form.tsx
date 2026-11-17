"use client";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import useCreateUser from "@/hooks/form/useCreateUser";
import type { RoleItem } from "@/types/access/models";

import RolePicker, { readRoles } from "../role-picker";

export default function CreateUserForm({
  roles,
}: Readonly<{ roles: RoleItem[] }>) {
  const { pending, error, createUser } = useCreateUser();

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        createUser({
          first_name: String(form.get("first_name")),
          last_name: String(form.get("last_name")),
          email: String(form.get("email")),
          password: String(form.get("password")),
          roles: readRoles(form),
        });
      }}
      className="flex flex-col gap-4"
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <TextInput
          label="First name"
          name="first_name"
          autoComplete="off"
          required
          error={error?.fields.first_name}
        />
        <TextInput
          label="Last name"
          name="last_name"
          autoComplete="off"
          required
          error={error?.fields.last_name}
        />
      </div>
      <TextInput
        label="Email"
        name="email"
        type="email"
        autoComplete="off"
        required
        error={error?.fields.email}
      />
      <TextInput
        label="Starting password"
        name="password"
        type="password"
        autoComplete="new-password"
        required
        error={error?.fields.password}
      />
      <RolePicker roles={roles} defaultRoles={[]} error={error?.fields.roles} />
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-red-600">
          {error.message}
        </p>
      )}
      <Button type="submit" pending={pending}>
        {pending ? "Creating user…" : "Create user"}
      </Button>
    </form>
  );
}
