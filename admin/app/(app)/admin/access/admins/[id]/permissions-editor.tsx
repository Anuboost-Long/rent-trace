"use client";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import Card from "@/components/common/card";
import SwitchInput from "@/components/common/inputs/switch-input";
import TextAreaInput from "@/components/common/inputs/text-area-input";
import { Route } from "@/constants/web-routes";
import useAdminPermissions from "@/hooks/form/useAdminPermissions";
import type { PermissionItem, UserPermissions } from "@/types/access/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

type PermissionsEditorProp = Readonly<{
  userId: number;
  firstName: string;
  access: UserPermissions;
  catalogue: PermissionItem[];
  readOnly: boolean;
  readOnlyReason?: string;
}>;

export default function PermissionsEditor({
  userId,
  firstName,
  access,
  catalogue,
  readOnly,
  readOnlyReason,
}: PermissionsEditorProp) {
  const router = useRouter();
  const [checked, setChecked] = useState(() => new Set(access.effective));
  const [reason, setReason] = useState("");
  const { pending, error, save } = useAdminPermissions(userId, () =>
    router.push(Route.admin.access),
  );

  // A permission that comes from a role can only be changed on the role.
  const fromRole = new Set(access.through_roles.map((item) => item.code));
  const granted = new Set(
    access.grants.filter((grant) => grant.is_active).map((grant) => grant.code),
  );
  const change = {
    grant: [...checked].filter(
      (code) => !access.effective.includes(code) && !fromRole.has(code),
    ),
    revoke: [...granted].filter((code) => !checked.has(code)),
  };
  const hasChanges = change.grant.length + change.revoke.length > 0;

  const toggle = (code: string, on: boolean) =>
    setChecked((current) => {
      const next = new Set(current);
      if (on) next.add(code);
      else next.delete(code);
      return next;
    });

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start">
      <Card title="Permissions">
        {catalogue.length === 0 ? (
          <p className="text-body-sm text-fg-secondary">
            There are no admin permissions to give.
          </p>
        ) : (
          <ul className="divide-y divide-default">
            {catalogue.map((permission) => (
              <li key={permission.code}>
                <SwitchInput
                  name={`permission-${permission.code}`}
                  label={permission.name}
                  description={
                    <>
                      {fromRole.has(permission.code)
                        ? `From role: ${access.roles.join(", ")}`
                        : permission.module}
                      {" · "}
                      <code>{permission.code}</code>
                    </>
                  }
                  checked={checked.has(permission.code)}
                  disabled={
                    readOnly || pending || fromRole.has(permission.code)
                  }
                  onChange={(event) =>
                    toggle(permission.code, event.target.checked)
                  }
                />
              </li>
            ))}
          </ul>
        )}
      </Card>
      <Card title="Save changes">
        {readOnly ? (
          <p className="text-body-sm text-fg-secondary">{readOnlyReason}</p>
        ) : (
          <form
            onSubmit={(event) => {
              event.preventDefault();
              save(change, reason.trim());
            }}
            className="flex flex-col gap-3"
          >
            <TextAreaInput
              name="reason"
              label="Reason (required)"
              required
              maxLength={500}
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              error={error?.fields.reason}
            />
            {error && !error.fields.reason && (
              <p role="alert" className="text-body-sm text-error">
                {error.message}
              </p>
            )}
            <Button
              type="submit"
              pending={pending}
              disabled={!hasChanges || reason.trim() === ""}
            >
              {pending ? "Saving…" : "Save permissions"}
            </Button>
            <ButtonLink href={Route.admin.access} variant="secondary">
              Cancel
            </ButtonLink>
            <p className="rounded-lg border border-default p-3 text-caption font-normal text-fg-secondary">
              Changes apply on {firstName}&apos;s next request and are saved
              with the reason.
            </p>
          </form>
        )}
      </Card>
    </div>
  );
}
