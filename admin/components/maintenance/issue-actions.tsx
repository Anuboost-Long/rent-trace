"use client";
import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextArea from "@/components/common/inputs/text-area-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { ClosureOutcomeLabel } from "@/constants/maintenance";
import useIssueActions from "@/hooks/form/useIssueActions";
import type {
  ClosureAnswer,
  ClosureOutcome,
  IssueDetail,
  MaintenanceAudience,
} from "@/types/maintenance/models";
import { useState } from "react";

type IssueActionsProp = Readonly<{
  audience: MaintenanceAudience;
  issue: IssueDetail;
}>;

type Dialog = "propose" | "close" | ClosureAnswer | null;

const outcomeOptions = Object.entries(ClosureOutcomeLabel).map(
  ([value, label]) => ({ value, label }),
);

export default function IssueActions({ audience, issue }: IssueActionsProp) {
  const { pending, error, run, respond, clearError } = useIssueActions(
    audience,
    issue.id,
  );
  const [dialog, setDialog] = useState<Dialog>(null);
  const [outcome, setOutcome] = useState<ClosureOutcome>("FIXED");
  const [reason, setReason] = useState("");
  const can = (action: IssueDetail["actions"][number]) =>
    issue.actions.includes(action);
  const closure = issue.open_closure;

  const close = () => {
    setDialog(null);
    setReason("");
    clearError();
  };

  const confirm = async () => {
    if (dialog === "propose" || dialog === "close") {
      const done = await run(dialog === "propose" ? "closure" : "close", {
        outcome,
        reason: reason.trim(),
      });
      if (done) close();
      return;
    }
    if (dialog && closure && (await respond(closure.id, dialog))) close();
  };

  const showForm = dialog === "propose" || dialog === "close";

  return (
    <>
      <div className="flex flex-wrap items-center gap-2">
        {can("ACKNOWLEDGE") && (
          <Button disabled={pending} onClick={() => run("acknowledge")}>
            Acknowledge
          </Button>
        )}
        {can("START") && (
          <Button disabled={pending} onClick={() => run("start")}>
            Start work
          </Button>
        )}
        {can("PROPOSE_CLOSURE") && (
          <Button variant="quiet" onClick={() => setDialog("propose")}>
            Propose closing
          </Button>
        )}
        {can("CLOSE_VACANT") && (
          <Button variant="quiet" onClick={() => setDialog("close")}>
            Close issue
          </Button>
        )}
        {can("WITHDRAW_CLOSURE") && (
          <Button
            variant="quiet"
            disabled={pending}
            onClick={() => run("closure/withdraw")}
          >
            Withdraw proposal
          </Button>
        )}
        {can("APPROVE_CLOSURE") && (
          <Button onClick={() => setDialog("approve")}>Approve closing</Button>
        )}
        {can("REJECT_CLOSURE") && (
          <Button variant="quiet" onClick={() => setDialog("reject")}>
            Reject
          </Button>
        )}
      </div>
      {error && !dialog && (
        <p role="alert" className="mt-3 text-sm text-red-600">
          {error.message}
        </p>
      )}
      {dialog && (
        <ConfirmDialog
          open
          title={
            dialog === "propose"
              ? "Propose closing this issue"
              : dialog === "close"
                ? "Close this issue"
                : dialog === "approve"
                  ? "Approve closing?"
                  : "Reject closing?"
          }
          message={
            dialog === "propose"
              ? "The other side has to approve before it closes."
              : dialog === "close"
                ? "Nobody lives here now, so you can close it yourself."
                : dialog === "approve"
                  ? "The issue closes with the outcome that was proposed."
                  : "The issue stays open and they are told."
          }
          confirmLabel={
            dialog === "propose"
              ? "Send proposal"
              : dialog === "close"
                ? "Close issue"
                : dialog === "approve"
                  ? "Approve"
                  : "Reject"
          }
          pending={pending}
          confirmDisabled={showForm && reason.trim() === ""}
          error={error?.fields.reason ?? error?.message}
          onConfirm={confirm}
          onCancel={close}
        >
          {showForm && (
            <div className="space-y-4">
              <SelectInput
                label="Outcome"
                name="outcome"
                value={outcome}
                onValueChange={(value) => setOutcome(value as ClosureOutcome)}
                options={outcomeOptions}
              />
              <TextArea
                label="Why it can be closed"
                name="reason"
                value={reason}
                onChange={(event) => setReason(event.target.value)}
                required
              />
            </div>
          )}
        </ConfirmDialog>
      )}
    </>
  );
}
