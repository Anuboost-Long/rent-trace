"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import CheckInput from "@/components/common/inputs/check-input";
import RadioInput from "@/components/common/inputs/radio-input";
import type { RoleItem } from "@/types/access/models";
import { useAtomValue } from "jotai";
import { useState } from "react";

type RolePickerProp = Readonly<{
  roles: RoleItem[];
  defaultRoles: string[];
  error?: string;
}>;

export const readRoles = (form: FormData) =>
  form.get("account_type") === "admin"
    ? form.getAll("admin_roles").map(String)
    : [String(form.get("party_role"))];

export default function RolePicker({
  roles,
  defaultRoles,
  error,
}: RolePickerProp) {
  const me = useAtomValue(UserAtom);
  const partyRoles = roles.filter((role) => role.kind === "PARTY");
  const adminRoles = roles.filter(
    (role) => role.kind === "ADMIN" && role.is_active,
  );
  const canPickAdmin =
    adminRoles.length > 0 && me?.permissions.includes("access.manage") === true;
  const startsAdmin = defaultRoles.some((code) =>
    adminRoles.some((role) => role.code === code),
  );
  const [type, setType] = useState(
    startsAdmin && canPickAdmin ? "admin" : "party",
  );

  return (
    <fieldset className="flex flex-col gap-3">
      <legend className="mb-1.5 text-sm font-medium">Role</legend>
      {canPickAdmin && (
        <div className="flex gap-6">
          <RadioInput
            name="account_type"
            value="party"
            label="Tenant or landlord"
            checked={type === "party"}
            onChange={() => setType("party")}
          />
          <RadioInput
            name="account_type"
            value="admin"
            label="Admin"
            checked={type === "admin"}
            onChange={() => setType("admin")}
          />
        </div>
      )}
      {type === "party" ? (
        <div className="flex flex-col gap-2">
          {partyRoles.map((role, index) => (
            <RadioInput
              key={role.code}
              name="party_role"
              value={role.code}
              label={role.name}
              defaultChecked={
                defaultRoles.includes(role.code) ||
                (index === 0 &&
                  !defaultRoles.some((code) =>
                    partyRoles.some((r) => r.code === code),
                  ))
              }
            />
          ))}
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {adminRoles.map((role) => (
            <CheckInput
              key={role.code}
              name="admin_roles"
              value={role.code}
              label={role.name}
              defaultChecked={defaultRoles.includes(role.code)}
            />
          ))}
          <p className="text-sm text-foreground/70">
            An admin can hold several roles. They get everything from all of
            them.
          </p>
        </div>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </fieldset>
  );
}
