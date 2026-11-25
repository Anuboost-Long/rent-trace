"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import CheckInput from "@/components/common/inputs/check-input";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import useRoleEditor from "@/hooks/form/useRoleEditor";
import type { PermissionItem, RoleItem } from "@/types/access/models";
import { useAtomValue } from "jotai";

type RoleEditorProp = Readonly<{
  role: RoleItem | null;
  roles: RoleItem[];
  permissions: PermissionItem[];
}>;

const HIDDEN_RECORDS = "access.view_hidden_records";

export default function RoleEditor({
  role,
  roles,
  permissions,
}: RoleEditorProp) {
  const me = useAtomValue(UserAtom);
  const { direct, inherited, parent, setParent, toggle, save, pending, error } =
    useRoleEditor(role, roles);
  const kind = role?.kind ?? "ADMIN";
  const parentOptions = [
    { value: "", label: "No parent" },
    ...roles
      .filter(
        (candidate) =>
          candidate.kind === kind &&
          candidate.is_active &&
          candidate.code !== role?.code,
      )
      .map((candidate) => ({ value: candidate.code, label: candidate.name })),
  ];
  const parentName = roles.find((candidate) => candidate.code === parent)?.name;
  const holds = (code: string) =>
    me?.is_top_level_admin || me?.permissions.includes(code);
  const sides = [
    {
      label: "Platform administration",
      hint: "Users, access, bans and sessions. Only admin roles can hold these.",
      adminOnly: true,
    },
    {
      label: "Renting activity",
      hint: "Properties, tenancies, maintenance and reviews. Landlords and tenants use these; an admin role can hold them to act on someone's behalf.",
      adminOnly: false,
    },
  ].map(({ label, hint, adminOnly }) => ({
    label,
    hint,
    modules: Object.entries(
      Object.groupBy(
        permissions.filter(
          (permission) => permission.is_admin_only === adminOnly,
        ),
        (permission) => permission.module,
      ),
    ) as [string, PermissionItem[]][],
  }));

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        save({
          name: String(form.get("name")),
          description: String(form.get("description") ?? ""),
          ...(role &&
            !role.is_system && { is_active: form.get("is_active") === "on" }),
        });
      }}
      className="flex flex-col gap-6"
    >
      <div className="grid max-w-xl gap-4">
        <TextInput
          label="Name"
          name="name"
          defaultValue={role?.name}
          required
          error={error?.fields.name}
        />
        <TextInput
          label="Description"
          name="description"
          defaultValue={role?.description ?? ""}
          error={error?.fields.description}
        />
        <SelectInput
          label="Inherits from"
          name="parent"
          options={parentOptions}
          value={parent}
          onValueChange={setParent}
          disabled={role?.is_system}
          error={error?.fields.parent}
        />
        {role && !role.is_system && (
          <CheckInput
            name="is_active"
            label="Active"
            defaultChecked={role.is_active}
          />
        )}
        {error?.fields.is_active && (
          <p className="text-sm text-error">{error.fields.is_active}</p>
        )}
      </div>

      <section>
        <h2 className="text-lg font-semibold">Permissions</h2>
        <p className="mt-1 mb-3 text-sm text-fg-secondary">
          Greyed out: inherited from {parentName ?? "the parent role"}, not
          available to this kind of role, or not held by you, so you can&apos;t
          hand it out.
        </p>
        <div className="flex flex-col gap-6">
          {sides
            .filter((side) => side.modules.length > 0)
            .map((side) => (
              <div key={side.label}>
                <h3 className="text-sm font-semibold">{side.label}</h3>
                <p className="mt-0.5 mb-2 text-sm text-fg-secondary">
                  {side.hint}
                </p>
                <div className="divide-y divide-default rounded-xl border border-default">
                  {side.modules.map(([module, items]) => (
                    <fieldset key={module} className="p-4">
                      <legend className="px-1 text-sm font-medium capitalize">
                        {module}
                      </legend>
                      <div className="mt-2 grid gap-2 sm:grid-cols-2">
                        {items.map((permission) => {
                          const isInherited = inherited.has(permission.code);
                          const unavailable =
                            permission.code === HIDDEN_RECORDS ||
                            (permission.is_admin_only && kind !== "ADMIN");
                          const disabled =
                            isInherited ||
                            unavailable ||
                            !holds(permission.code);
                          return (
                            <CheckInput
                              key={permission.code}
                              label={
                                isInherited
                                  ? `${permission.name} (inherited)`
                                  : permission.name
                              }
                              checked={
                                isInherited || direct.has(permission.code)
                              }
                              disabled={disabled || pending}
                              onChange={() => toggle(permission.code)}
                            />
                          );
                        })}
                      </div>
                    </fieldset>
                  ))}
                </div>
              </div>
            ))}
        </div>
        {error?.fields.permissions && (
          <p className="mt-2 text-sm text-error">{error.fields.permissions}</p>
        )}
      </section>

      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
      <div className="flex gap-3">
        <Button type="submit" pending={pending}>
          {pending ? "Saving…" : role ? "Save changes" : "Create role"}
        </Button>
        <ButtonLink href={Route.admin.access} variant="quiet">
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
