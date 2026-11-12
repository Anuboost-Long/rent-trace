"use client";
import Button from "@/components/common/button";
import Can from "@/components/common/can";
import CheckInput from "@/components/common/inputs/check-input";
import TextInput from "@/components/common/inputs/text-input";
import DataTable, { type Column } from "@/components/common/table/data-table";
import { InvitationStatusLabel, TenancyAccess } from "@/constants/tenancies";
import useInvitations from "@/hooks/form/useInvitations";
import type { Invitation, TenancyAudience } from "@/types/tenancies/models";
import { formatDate } from "@/utils/format-date";
import { useRef } from "react";

type InvitationsSectionProp = Readonly<{
  audience: TenancyAudience;
  tenancyId: number;
  invitations: Invitation[];
  closed: boolean;
}>;

export default function InvitationsSection({
  audience,
  tenancyId,
  invitations,
  closed,
}: InvitationsSectionProp) {
  const { pending, error, invite, act } = useInvitations(audience, tenancyId);
  const formRef = useRef<HTMLFormElement>(null);

  const columns: Column<Invitation>[] = [
    { header: "Email", cell: (item) => item.email },
    {
      header: "Role",
      cell: (item) => (item.is_primary ? "Primary tenant" : "Tenant"),
    },
    {
      header: "Status",
      cell: (item) => (
        <>
          {InvitationStatusLabel[item.status]}
          {item.status === "PENDING" && (
            <p className="text-xs text-foreground/60">
              Expires {formatDate(item.expires_at)}
            </p>
          )}
        </>
      ),
    },
    {
      header: "Actions",
      className: "text-right",
      cell: (item) =>
        (item.status === "PENDING" || item.status === "EXPIRED") && (
          <Can permission={TenancyAccess[audience].invite}>
            <div className="flex justify-end gap-2">
              <Button
                variant="quiet"
                disabled={pending}
                onClick={() => act(item.id, "resend")}
              >
                Resend
              </Button>
              <Button
                variant="quiet"
                disabled={pending}
                onClick={() => act(item.id, "revoke")}
              >
                Revoke
              </Button>
            </div>
          </Can>
        ),
    },
  ];

  return (
    <section className="mt-10">
      <h2 className="text-lg font-semibold">Invitations</h2>
      <p className="mt-1 mb-4 text-foreground/70">
        Invited people get an email link that lasts 7 days. Resending sends a
        new link and the old one stops working.
      </p>
      <Can permission={TenancyAccess[audience].invite}>
        {!closed && (
          <form
            ref={formRef}
            onSubmit={async (event) => {
              event.preventDefault();
              const form = new FormData(event.currentTarget);
              const sent = await invite(
                String(form.get("email")),
                form.get("is_primary") === "on",
              );
              if (sent) formRef.current?.reset();
            }}
            className="mb-6 grid gap-4 sm:grid-cols-[1fr_auto_auto] sm:items-end"
          >
            <TextInput
              label="Invite by email"
              name="email"
              type="email"
              autoComplete="off"
              required
              error={error?.fields.email}
            />
            <CheckInput label="Primary tenant" name="is_primary" />
            <Button type="submit" pending={pending}>
              Send invite
            </Button>
          </form>
        )}
      </Can>
      {error && !error.fields.email && (
        <p role="alert" className="mb-4 text-sm text-red-600">
          {error.message}
        </p>
      )}
      <DataTable
        caption="Invitations"
        columns={columns}
        rows={invitations}
        rowKey={(item) => item.id}
        empty={<p className="text-foreground/70">No invitations yet.</p>}
      />
    </section>
  );
}
