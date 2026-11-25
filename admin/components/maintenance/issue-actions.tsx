"use client";
import Button from "@/components/common/button";
import DateInput from "@/components/common/inputs/date-input";
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

type Dialog = "propose" | "close" | "assign" | ClosureAnswer | null;

const DIALOG_COPY = {
  assign: {
    title: "Book a tradesperson",
    message: "Your tenants are told who is coming, with their contact details.",
    confirm: "Book",
  },
  propose: {
    title: "Propose closing this issue",
    message: "The other side has to approve before it closes.",
    confirm: "Send proposal",
  },
  close: {
    title: "Close this issue",
    message: "Nobody lives here now, so you can close it yourself.",
    confirm: "Close issue",
  },
  approve: {
    title: "Approve closing?",
    message: "The issue closes with the outcome that was proposed.",
    confirm: "Approve",
  },
  reject: {
    title: "Reject closing?",
    message: "The issue stays open and they are told.",
    confirm: "Reject",
  },
} as const;

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
  const [providerId, setProviderId] = useState("");
  const [visitDate, setVisitDate] = useState("");
  const can = (action: IssueDetail["actions"][number]) =>
    issue.actions.includes(action);
  const closure = issue.open_closure;

  const close = () => {
    setDialog(null);
    setReason("");
    setProviderId("");
    setVisitDate("");
    clearError();
  };

  const providerOptions = issue.provider_options.map((option) => ({
    value: String(option.id),
    label: [
      option.business_name,
      option.matches_category && "matches the problem",
      option.is_recommended && "preferred",
    ]
      .filter(Boolean)
      .join(" · "),
  }));

  const confirm = async () => {
    if (dialog === "assign") {
      const done = await run("assignment", {
        service_provider_id: Number(providerId || providerOptions[0]?.value),
        scheduled_at: visitDate ? `${visitDate}T00:00:00Z` : null,
      });
      if (done) close();
      return;
    }
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
  const copy = dialog ? DIALOG_COPY[dialog] : DIALOG_COPY.assign;
  const message =
    dialog === "close" && audience === "admin"
      ? "Nobody lives here now, so you can close it for the owner."
      : copy.message;

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
        {can("ASSIGN_PROVIDER") && (
          <Button variant="quiet" onClick={() => setDialog("assign")}>
            {issue.assignment ? "Change tradesperson" : "Book tradesperson"}
          </Button>
        )}
        {can("COMPLETE_VISIT") && (
          <Button
            variant="quiet"
            disabled={pending}
            onClick={() => run("assignment/complete")}
          >
            Mark visit done
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
        <p role="alert" className="mt-3 text-sm text-error">
          {error.message}
        </p>
      )}
      {dialog && (
        <ConfirmDialog
          open
          title={copy.title}
          message={message}
          confirmLabel={copy.confirm}
          pending={pending}
          confirmDisabled={
            (showForm && reason.trim() === "") ||
            (dialog === "assign" && providerOptions.length === 0)
          }
          error={error?.fields.reason ?? error?.message}
          onConfirm={confirm}
          onCancel={close}
        >
          {dialog === "assign" &&
            (providerOptions.length === 0 ? (
              <p className="text-sm text-fg-secondary">
                Link a tradesperson to this property first, under Tradespeople.
              </p>
            ) : (
              <div className="space-y-4">
                <SelectInput
                  label="Tradesperson"
                  name="provider"
                  value={providerId || providerOptions[0].value}
                  onValueChange={setProviderId}
                  options={providerOptions}
                  error={error?.fields.service_provider_id}
                />
                <DateInput
                  label="Date they are coming (optional)"
                  name="visit_date"
                  defaultValue={visitDate}
                  onValueChange={setVisitDate}
                  error={error?.fields.scheduled_at}
                />
              </div>
            ))}
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
