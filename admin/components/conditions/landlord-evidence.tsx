"use client";
import Button from "@/components/common/button";
import TextArea from "@/components/common/inputs/text-area-input";
import LocalTime from "@/components/common/local-time";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useEvidenceActions from "@/hooks/form/useEvidenceActions";
import type {
  ConditionEvidence,
  EvidenceStatus,
} from "@/types/evidence/models";
import { useState } from "react";

const StatusLabel: Record<EvidenceStatus, string> = {
  PENDING_REVIEW: "Waiting for you",
  APPROVED: "Approved",
  DISPUTED: "Rejected",
  CANCELLED: "Withdrawn by the tenant",
};

export default function LandlordEvidence({
  reports,
}: Readonly<{ reports: ConditionEvidence[] }>) {
  const { pending, error, clearError, approve, reject } = useEvidenceActions();
  const [rejecting, setRejecting] = useState<ConditionEvidence | null>(null);
  const [reason, setReason] = useState("");

  if (reports.length === 0) return null;

  const closeReject = () => {
    setRejecting(null);
    setReason("");
    clearError();
  };

  return (
    <section aria-labelledby="landlord-evidence-heading" className="mt-12">
      <h2 id="landlord-evidence-heading" className="text-lg font-semibold">
        Conditions reported by tenants
      </h2>
      <ul className="mt-2 divide-y divide-foreground/10">
        {reports.map((report) => (
          <li key={report.id} className="py-4">
            <div className="flex flex-wrap items-start justify-between gap-x-6 gap-y-3">
              <div className="min-w-0 max-w-[65ch] flex-1">
                <p className="font-medium">{report.title}</p>
                {report.description && (
                  <p className="mt-1 whitespace-pre-line text-foreground/80">
                    {report.description}
                  </p>
                )}
                <p className="mt-1.5 text-sm text-foreground/60">
                  {report.author} saw it <LocalTime iso={report.observed_at} />{" "}
                  · {StatusLabel[report.status]}
                </p>
                {report.rejection_reason && (
                  <p className="mt-1 text-sm text-foreground/80">
                    Reason: {report.rejection_reason}
                  </p>
                )}
              </div>
              {report.status === "PENDING_REVIEW" && (
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    disabled={pending}
                    onClick={() => void approve(report.id)}
                  >
                    Approve
                  </Button>
                  <Button
                    variant="quiet"
                    size="sm"
                    disabled={pending}
                    onClick={() => setRejecting(report)}
                  >
                    Reject
                  </Button>
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
      {error && !rejecting && (
        <p role="alert" className="mt-2 text-sm text-red-600">
          {error.message}
        </p>
      )}

      {rejecting && (
        <ConfirmDialog
          open
          title={`Reject ${rejecting.title}?`}
          message="The tenant sees your reason."
          confirmLabel="Reject report"
          pending={pending}
          confirmDisabled={reason.trim() === ""}
          error={error?.message}
          onConfirm={async () => {
            if (await reject(rejecting.id, reason.trim())) closeReject();
          }}
          onCancel={closeReject}
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
    </section>
  );
}
