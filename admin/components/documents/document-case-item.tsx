"use client";
import Button from "@/components/common/button";
import LocalTime from "@/components/common/local-time";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import StatusBadge from "@/components/common/status-badge";
import { Route } from "@/constants/web-routes";
import useDocumentCaseDecision from "@/hooks/form/useDocumentCaseDecision";
import type { DocumentCase } from "@/types/documents/models";
import Link from "next/link";
import { useState } from "react";

type Decision = "approve" | "reject";

const DIALOG: Record<
  Decision,
  { title: string; message: string; confirm: string }
> = {
  approve: {
    title: "Confirm this version?",
    message:
      "It becomes the current version of the paper. The tenants and owners are told, with your reason.",
    confirm: "Confirm version",
  },
  reject: {
    title: "Uphold the flag?",
    message:
      "Nothing becomes current and it can't be sent again. The tenants and owners are told, with your reason.",
    confirm: "Uphold flag",
  },
};

const Said = ({
  label,
  children,
}: Readonly<{ label: string; children: React.ReactNode }>) => (
  <div>
    <dt className="inline text-fg-secondary">{label}: </dt>
    <dd className="inline">{children}</dd>
  </div>
);

export default function DocumentCaseItem({
  item,
}: Readonly<{ item: DocumentCase }>) {
  const { pending, error, clearError, decide } = useDocumentCaseDecision();
  const [deciding, setDeciding] = useState<Decision | null>(null);

  const close = () => {
    setDeciding(null);
    clearError();
  };

  return (
    <div className="p-4">
      <div className="flex flex-wrap items-start justify-between gap-x-6 gap-y-3">
        <div className="min-w-0 max-w-[65ch] flex-1">
          <p className="font-medium">
            {item.title} · version {item.version_no}
          </p>
          <p className="text-body-sm text-fg-secondary">
            Asked by {item.raised_by_name} (
            {item.raised_by_side === "TENANT" ? "tenant" : "landlord"}) ·{" "}
            <LocalTime iso={item.submitted_at} />
          </p>
          <dl className="mt-3 space-y-1 text-body-sm">
            {item.flag_reason && (
              <Said label="The tenant flagged it">{item.flag_reason}</Said>
            )}
            <Said label="Why an admin was asked">{item.reason}</Said>
            {item.decision_reason && (
              <Said label="Your reason">{item.decision_reason}</Said>
            )}
          </dl>
          {item.tenancy_id && (
            <Link
              href={Route.admin.tenancy(item.tenancy_id)}
              className="mt-3 inline-block text-body-sm text-fg-brand underline-offset-2 hover:underline"
            >
              Open the tenancy to read the paper
            </Link>
          )}
        </div>
        {item.status === "PENDING_REVIEW" ? (
          <div className="flex gap-2">
            <Button
              size="sm"
              disabled={pending}
              onClick={() => setDeciding("approve")}
            >
              Confirm version
            </Button>
            <Button
              size="sm"
              variant="secondary"
              disabled={pending}
              onClick={() => setDeciding("reject")}
            >
              Uphold flag
            </Button>
          </div>
        ) : (
          <StatusBadge
            tone={item.status === "APPROVED" ? "success" : "neutral"}
          >
            {item.status === "APPROVED" ? "Confirmed" : "Flag upheld"}
          </StatusBadge>
        )}
      </div>

      {deciding && (
        <ConfirmDialog
          open
          title={DIALOG[deciding].title}
          message={DIALOG[deciding].message}
          confirmLabel={DIALOG[deciding].confirm}
          reasonLabel="Reason"
          pending={pending}
          error={error?.message}
          onConfirm={async (reason) => {
            if (await decide(item.id, deciding, reason)) close();
          }}
          onCancel={close}
        />
      )}
    </div>
  );
}
