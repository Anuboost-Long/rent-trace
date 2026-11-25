"use client";
import Button from "@/components/common/button";
import Can from "@/components/common/can";
import LocalTime from "@/components/common/local-time";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useTermChange from "@/hooks/form/useTermChange";
import type { TermChange, TermChangeAnswer } from "@/types/tenancies/models";
import { useState } from "react";

import { Approvals, ChangedTerms } from "./term-change-summary";

const COPY: Record<
  TermChangeAnswer,
  { title: string; message: string; confirm: string }
> = {
  approve: {
    title: "Approve this change?",
    message:
      "It applies once every tenant has approved. You can't change your answer afterwards.",
    confirm: "Approve change",
  },
  decline: {
    title: "Decline this change?",
    message:
      "Nothing changes and your landlord is told. They can send a new proposal.",
    confirm: "Decline change",
  },
};

export default function TermChangeReview({
  tenancyId,
  change,
}: Readonly<{ tenancyId: number; change: TermChange }>) {
  const { pending, error, respond, clearError } = useTermChange(tenancyId);
  const [answer, setAnswer] = useState<TermChangeAnswer | null>(null);
  const expired = change.status === "EXPIRED";
  const answered = change.my_decision ?? null;

  const close = () => {
    setAnswer(null);
    clearError();
  };

  const confirm = async () => {
    if (answer && (await respond(change.id, answer))) setAnswer(null);
  };

  return (
    <section
      aria-labelledby="review-heading"
      className="mb-8 rounded-xl border border-default p-5"
    >
      <h2 id="review-heading" className="text-lg font-semibold">
        {expired
          ? "A proposed change expired"
          : "Your landlord proposed a change"}
      </h2>
      <p className="mt-1 text-sm text-fg-secondary">
        {expired ? (
          "Nobody answered in time, so nothing changed. Your landlord can send it again."
        ) : (
          <>
            Rent or bond would go up. Every tenant has to approve. It expires on{" "}
            <LocalTime iso={change.expires_at} />.
          </>
        )}
      </p>
      <div className="mt-3">
        <ChangedTerms change={change} />
      </div>
      {!expired && (
        <>
          <div className="mt-3">
            <Approvals change={change} />
          </div>
          <Can permission="tenancies.approve_terms">
            {answered === null ? (
              <div className="mt-5 flex gap-2">
                <Button onClick={() => setAnswer("approve")}>Approve</Button>
                <Button variant="quiet" onClick={() => setAnswer("decline")}>
                  Decline
                </Button>
              </div>
            ) : (
              <p className="mt-4 text-sm font-medium">
                You {answered === "APPROVED" ? "approved" : "declined"} this.
              </p>
            )}
          </Can>
        </>
      )}
      {answer && (
        <ConfirmDialog
          open
          title={COPY[answer].title}
          message={COPY[answer].message}
          confirmLabel={COPY[answer].confirm}
          pending={pending}
          error={error?.message}
          onConfirm={confirm}
          onCancel={close}
        >
          <ChangedTerms change={change} />
        </ConfirmDialog>
      )}
    </section>
  );
}
