"use client";
import Button from "@/components/common/button";
import TextArea from "@/components/common/inputs/text-area-input";
import LocalTime from "@/components/common/local-time";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useCaseActions from "@/hooks/form/useCaseActions";
import type { ReviewCase } from "@/types/evidence/models";
import { useState } from "react";

type Decision = "approve" | "reject";

const OUTCOME: Record<ReviewCase["status"], string> = {
  PENDING_REVIEW: "Waiting for a decision",
  APPROVED: "Approved",
  REJECTED: "Rejected",
};

const DIALOG: Record<
  Decision,
  { title: string; message: string; confirm: string }
> = {
  approve: {
    title: "Approve this report?",
    message:
      "It becomes the accepted account of the condition. The tenant and landlord are told, with your reason.",
    confirm: "Approve report",
  },
  reject: {
    title: "Reject this report?",
    message:
      "The record stays as it was. The tenant and landlord are told, with your reason.",
    confirm: "Reject report",
  },
};

export default function ReviewCaseItem({
  item,
}: Readonly<{ item: ReviewCase }>) {
  const { pending, error, clearError, decide } = useCaseActions();
  const [deciding, setDeciding] = useState<Decision | null>(null);
  const [reason, setReason] = useState("");

  const close = () => {
    setDeciding(null);
    setReason("");
    clearError();
  };

  return (
    <div className="p-4">
      <div className="flex flex-wrap items-start justify-between gap-x-6 gap-y-3">
        <div className="min-w-0 max-w-[65ch] flex-1">
          <p className="font-medium">{item.title}</p>
          <p className="text-sm text-foreground/60">
            {item.place} · {item.author} saw it{" "}
            <LocalTime iso={item.observed_at} />
          </p>
          {item.description && (
            <p className="mt-2 whitespace-pre-line text-foreground/80">
              {item.description}
            </p>
          )}
          <dl className="mt-3 space-y-1 text-sm">
            <div>
              <dt className="inline text-foreground/60">
                Landlord&apos;s reason:{" "}
              </dt>
              <dd className="inline">
                {item.landlord_rejection_reason ?? "Never answered"}
              </dd>
            </div>
            <div>
              <dt className="inline text-foreground/60">
                Asked for a decision by {item.escalated_by}:{" "}
              </dt>
              <dd className="inline">{item.escalation_reason}</dd>
            </div>
            {item.admin_reason && (
              <div>
                <dt className="inline text-foreground/60">Your reason: </dt>
                <dd className="inline">{item.admin_reason}</dd>
              </div>
            )}
          </dl>
          <p className="mt-2 text-xs text-foreground/60">
            {OUTCOME[item.status]}
          </p>
        </div>
        {item.status === "PENDING_REVIEW" && (
          <div className="flex gap-1">
            <Button
              size="sm"
              disabled={pending}
              onClick={() => setDeciding("approve")}
            >
              Approve
            </Button>
            <Button
              variant="quiet"
              size="sm"
              disabled={pending}
              onClick={() => setDeciding("reject")}
            >
              Reject
            </Button>
          </div>
        )}
      </div>

      {deciding && (
        <ConfirmDialog
          open
          title={DIALOG[deciding].title}
          message={DIALOG[deciding].message}
          confirmLabel={DIALOG[deciding].confirm}
          pending={pending}
          confirmDisabled={reason.trim() === ""}
          error={error?.message}
          onConfirm={async () => {
            if (await decide(item.id, deciding, reason.trim())) close();
          }}
          onCancel={close}
        >
          <TextArea
            label="Reason"
            name="reason"
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            required
          />
        </ConfirmDialog>
      )}
    </div>
  );
}
