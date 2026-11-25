"use client";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import CheckInput from "@/components/common/inputs/check-input";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import usePermissionForm from "@/hooks/form/usePermissionForm";
import type { PermissionItem } from "@/types/access/models";

export default function PermissionForm({
  permission,
}: Readonly<{ permission: PermissionItem | null }>) {
  const { pending, error, save } = usePermissionForm(permission);

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        save({
          code: String(form.get("code") ?? ""),
          name: String(form.get("name")),
          is_admin_only: form.get("is_admin_only") === "on",
          is_active: form.get("is_active") === "on",
        });
      }}
      className="grid max-w-xl gap-4"
    >
      <TextInput
        label="Code"
        name="code"
        placeholder="module.action"
        defaultValue={permission?.code}
        disabled={permission !== null}
        required={permission === null}
        error={error?.fields.code}
      />
      {permission === null && (
        <p className="-mt-2 text-sm text-fg-secondary">
          Lower case, like reports.export. The code can&apos;t be changed later,
          because the code that checks it uses this exact text.
        </p>
      )}
      <TextInput
        label="Name"
        name="name"
        defaultValue={permission?.name}
        required
        error={error?.fields.name}
      />
      <CheckInput
        name="is_admin_only"
        label="Only admins can hold it"
        defaultChecked={permission?.is_admin_only}
      />
      {error?.fields.is_admin_only && (
        <p className="text-sm text-error">{error.fields.is_admin_only}</p>
      )}
      {permission && (
        <CheckInput
          name="is_active"
          label="Active"
          defaultChecked={permission.is_active}
        />
      )}
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
      <div className="flex gap-3">
        <Button type="submit" pending={pending}>
          {pending
            ? "Saving…"
            : permission
              ? "Save changes"
              : "Create permission"}
        </Button>
        <ButtonLink href={Route.admin.permissions} variant="quiet">
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
