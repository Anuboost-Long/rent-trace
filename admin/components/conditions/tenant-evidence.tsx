"use client";
import Button from "@/components/common/button";
import LocalTime from "@/components/common/local-time";
import { canEscalate, evidenceLabel } from "@/constants/evidence";
import useEvidenceActions from "@/hooks/form/useEvidenceActions";
import type { ConditionEvidence } from "@/types/evidence/models";
import { Plus } from "lucide-react";
import { useState } from "react";

import EscalateDialog from "./escalate-dialog";
import EvidenceDialog from "./evidence-dialog";

type TenantEvidenceProp = Readonly<{
  tenancyId: number;
  reports: ConditionEvidence[];
  canReport: boolean;
}>;

export default function TenantEvidence({
  tenancyId,
  reports,
  canReport,
}: TenantEvidenceProp) {
  const { pending, error, clearError, submit, withdraw, escalate } =
    useEvidenceActions();
  const [reporting, setReporting] = useState(false);
  const [escalating, setEscalating] = useState<ConditionEvidence | null>(null);

  if (reports.length === 0 && !canReport) return null;

  const closeDialog = () => {
    setReporting(false);
    setEscalating(null);
    clearError();
  };

  return (
    <section aria-labelledby="evidence-heading" className="mt-12">
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3">
        <h2 id="evidence-heading" className="text-lg font-semibold">
          Conditions you reported
        </h2>
        {canReport && (
          <Button
            size="sm"
            className="gap-2"
            onClick={() => setReporting(true)}
          >
            <Plus aria-hidden className="size-4" />
            Report a condition
          </Button>
        )}
      </div>

      {reports.length === 0 ? (
        <p className="mt-3 max-w-[65ch] text-sm text-foreground/70">
          See something the landlord hasn&apos;t noted, like damage or damp?
          Report it here and your landlord can approve it.
        </p>
      ) : (
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
                    Seen <LocalTime iso={report.observed_at} /> ·{" "}
                    {evidenceLabel(report, "tenant")}
                  </p>
                  {report.rejection_reason && (
                    <p className="mt-1 text-sm text-foreground/80">
                      Reason: {report.rejection_reason}
                    </p>
                  )}
                  {report.admin_reason && (
                    <p className="mt-1 text-sm text-foreground/80">
                      Admin&apos;s reason: {report.admin_reason}
                    </p>
                  )}
                </div>
                {report.status === "PENDING_REVIEW" && (
                  <Button
                    variant="quiet"
                    size="sm"
                    disabled={pending}
                    onClick={() => void withdraw(tenancyId, report.id)}
                  >
                    Withdraw
                  </Button>
                )}
                {canEscalate(report) && (
                  <Button
                    variant="quiet"
                    size="sm"
                    disabled={pending}
                    onClick={() => setEscalating(report)}
                  >
                    Ask an admin to decide
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {escalating && (
        <EscalateDialog
          title={escalating.title}
          pending={pending}
          error={error}
          onCancel={closeDialog}
          onConfirm={async (reason) => {
            if (await escalate(escalating.id, reason, tenancyId)) closeDialog();
          }}
        />
      )}

      {reporting && (
        <EvidenceDialog
          pending={pending}
          error={error}
          onCancel={closeDialog}
          onSend={async (body) => {
            if (await submit(tenancyId, body)) closeDialog();
          }}
        />
      )}
    </section>
  );
}
