"use client";
import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useGrants from "@/hooks/form/useGrants";
import type { PermissionItem, UserPermissions } from "@/types/access/models";
import { formatDate } from "@/utils/format-date";
import { Trash2 } from "lucide-react";
import { useState } from "react";

type UserPermissionsProp = Readonly<{
  userId: number;
  name: string;
  data: UserPermissions;
  allPermissions: PermissionItem[];
}>;

export default function UserPermissionsSection({
  userId,
  name,
  data,
  allPermissions,
}: UserPermissionsProp) {
  const { pending, error, grant, revoke } = useGrants(userId);
  const [revoking, setRevoking] = useState<string | null>(null);
  const [formKey, setFormKey] = useState(0);

  const activeGrants = data.grants.filter((item) => item.is_active);
  const available = allPermissions
    .filter((permission) => !data.effective.includes(permission.code))
    .map((permission) => ({
      value: permission.code,
      label: `${permission.name} (${permission.code})`,
    }));
  const throughRoles = Object.entries(
    Object.groupBy(data.through_roles, (permission) => permission.module),
  );

  return (
    <section className="mt-10">
      <h2 className="text-lg font-semibold">Permissions</h2>
      <p className="mt-1 mb-4 text-sm text-foreground/70">
        {data.roles.join(", ") || "No role"} gives the access below. Individual
        grants add to it.
      </p>

      <div className="divide-y divide-foreground/15 rounded-xl border border-foreground/15">
        <div className="p-4">
          <h3 className="mb-2 text-sm font-medium">From their role</h3>
          {throughRoles.length === 0 ? (
            <p className="text-sm text-foreground/70">
              Nothing from their role.
            </p>
          ) : (
            <dl className="grid gap-2 text-sm sm:grid-cols-[8rem_1fr]">
              {throughRoles.map(([module, items]) => (
                <div key={module} className="contents">
                  <dt className="text-foreground/70 capitalize">{module}</dt>
                  <dd>{items?.map((item) => item.name).join(", ")}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>

        <div className="p-4">
          <h3 className="mb-2 text-sm font-medium">Individual grants</h3>
          {activeGrants.length === 0 ? (
            <p className="text-sm text-foreground/70">
              No individual grants. Add one below when {name} needs something
              their role doesn&apos;t give.
            </p>
          ) : (
            <ul className="divide-y divide-foreground/15">
              {activeGrants.map((item) => (
                <li
                  key={item.code}
                  className="flex items-start justify-between gap-4 py-2"
                >
                  <div className="text-sm">
                    <p className="font-medium">{item.name}</p>
                    <p className="text-foreground/70">
                      {item.reason} · {formatDate(item.created_at)}
                    </p>
                  </div>
                  <Button
                    variant="quiet"
                    size="icon"
                    title="Revoke"
                    aria-label={`Revoke ${item.name}`}
                    onClick={() => setRevoking(item.code)}
                  >
                    <Trash2 aria-hidden className="size-4" />
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <form
          key={formKey}
          onSubmit={async (event) => {
            event.preventDefault();
            const form = new FormData(event.currentTarget);
            const ok = await grant(
              String(form.get("permission")),
              String(form.get("reason")),
            );
            if (ok) setFormKey((key) => key + 1);
          }}
          className="grid gap-4 p-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end"
        >
          <SelectInput
            label="Permission"
            name="permission"
            options={available}
            error={error?.fields.permission}
          />
          <TextInput
            label="Reason"
            name="reason"
            placeholder="Why they need it"
            required
            error={error?.fields.reason}
          />
          <Button
            type="submit"
            pending={pending}
            disabled={available.length === 0}
          >
            Add grant
          </Button>
          {error && Object.keys(error.fields).length === 0 && (
            <p role="alert" className="text-sm text-red-600 sm:col-span-3">
              {error.message}
            </p>
          )}
        </form>
      </div>

      {revoking && (
        <ConfirmDialog
          open
          title="Revoke this grant?"
          message={`${name} loses this permission unless their role gives it.`}
          confirmLabel="Revoke"
          pending={pending}
          error={error?.message}
          onConfirm={async () => {
            if (await revoke(revoking)) setRevoking(null);
          }}
          onCancel={() => setRevoking(null)}
        />
      )}
    </section>
  );
}
