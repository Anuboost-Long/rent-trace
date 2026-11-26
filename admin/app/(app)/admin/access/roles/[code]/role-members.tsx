"use client";
import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { Route } from "@/constants/web-routes";
import useRoleMembers from "@/hooks/form/useRoleMembers";
import type { RoleMember } from "@/types/access/models";
import type { UserOption } from "@/types/users/models";
import { UserMinus } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

type RoleMembersProp = Readonly<{
  roleCode: string;
  roleName: string;
  members: RoleMember[];
  total: number;
  candidates: UserOption[];
  canChange: boolean;
}>;

export default function RoleMembers({
  roleCode,
  roleName,
  members,
  total,
  candidates,
  canChange,
}: RoleMembersProp) {
  const { pending, error, add, remove } = useRoleMembers(roleCode);
  const [removing, setRemoving] = useState<RoleMember | null>(null);
  const [formKey, setFormKey] = useState(0);

  return (
    <section className="mt-10">
      <h2 className="text-section">People in this role</h2>
      <p className="mt-1 mb-3 text-sm text-fg-secondary">
        {total} {total === 1 ? "person holds" : "people hold"} {roleName}.
        {total > members.length && ` Showing the first ${members.length}.`}
      </p>
      <div className="divide-y divide-default rounded-xl border border-default">
        {members.length === 0 ? (
          <p className="p-4 text-sm text-fg-secondary">
            Nobody has this role yet.
          </p>
        ) : (
          <ul className="divide-y divide-default">
            {members.map((member) => (
              <li
                key={member.id}
                className="flex items-center justify-between gap-4 p-4"
              >
                <div className="text-sm">
                  <Link
                    href={Route.admin.user(member.id)}
                    className="font-medium underline-offset-2 hover:underline"
                  >
                    {member.first_name} {member.last_name}
                  </Link>
                  <p className="text-fg-secondary">
                    {member.email} · {member.role_names.join(", ")}
                  </p>
                </div>
                {canChange && (
                  <Button
                    variant="quiet"
                    size="icon"
                    title="Remove from role"
                    aria-label={`Remove ${member.first_name} ${member.last_name} from ${roleName}`}
                    onClick={() => setRemoving(member)}
                  >
                    <UserMinus aria-hidden className="size-4" />
                  </Button>
                )}
              </li>
            ))}
          </ul>
        )}
        {canChange && (
          <form
            key={formKey}
            onSubmit={async (event) => {
              event.preventDefault();
              const form = new FormData(event.currentTarget);
              if (await add(Number(form.get("user"))))
                setFormKey((key) => key + 1);
            }}
            className="grid gap-4 p-4 sm:grid-cols-[1fr_auto] sm:items-end"
          >
            <SelectInput
              label="Add a person"
              name="user"
              options={candidates.map((user) => ({
                value: String(user.id),
                label: `${user.first_name} ${user.last_name} (${user.email})`,
              }))}
            />
            <Button
              type="submit"
              pending={pending}
              disabled={candidates.length === 0}
            >
              Add to role
            </Button>
            {error && !removing && (
              <p role="alert" className="text-sm text-error sm:col-span-2">
                {error.message}
              </p>
            )}
          </form>
        )}
      </div>
      {removing && (
        <ConfirmDialog
          open
          title={`Remove ${removing.first_name} from ${roleName}?`}
          message="They lose what this role gives them. They keep their other roles."
          confirmLabel="Remove"
          pending={pending}
          error={error?.message}
          onConfirm={async () => {
            if (await remove(removing.id)) setRemoving(null);
          }}
          onCancel={() => setRemoving(null)}
        />
      )}
    </section>
  );
}
