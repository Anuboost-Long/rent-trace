"use client";
import {
  handleIssueAction,
  handleReportIssue,
  handleRespondClosure,
} from "@/api/services/maintenance/serve-action";
import { IssueRoutes } from "@/constants/maintenance";
import type { ApiFailure } from "@/types/api/common";
import type {
  AssignBody,
  ClosureAnswer,
  ClosureBody,
  MaintenanceAudience,
  ReportIssueBody,
} from "@/types/maintenance/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

type IssuePath = Parameters<typeof handleIssueAction>[1];

const ISSUE_DONE: Partial<Record<IssuePath, string>> = {
  acknowledge: "Issue acknowledged",
  start: "Work marked as started",
  closure: "Closing proposed",
  "closure/withdraw": "Closing withdrawn",
  close: "Issue closed",
  assignment: "Tradesperson booked",
  "assignment/complete": "Visit marked done",
};

const useIssueActions = (audience: MaintenanceAudience, issueId?: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const finish = (failure: ApiFailure | null, done: string) => {
    setPending(false);
    setError(failure);
    if (!failure) {
      toast.success(done);
      router.refresh();
    }
    return !failure;
  };

  const run = async (path: IssuePath, body?: ClosureBody | AssignBody) => {
    if (issueId === undefined) return false;
    setPending(true);
    setError(null);
    const { error } = await handleIssueAction(issueId, path, body, audience);
    return finish(error, ISSUE_DONE[path] ?? "Done");
  };

  const respond = async (proposalId: number, answer: ClosureAnswer) => {
    if (issueId === undefined) return false;
    setPending(true);
    setError(null);
    const { error } = await handleRespondClosure(issueId, proposalId, answer);
    return finish(
      error,
      answer === "approve" ? "Closing approved" : "Closing rejected",
    );
  };

  const report = async (body: ReportIssueBody) => {
    setPending(true);
    setError(null);
    const { data, error } = await handleReportIssue(body);
    setPending(false);
    setError(error);
    if (data) {
      toast.success("Issue reported");
      router.push(IssueRoutes[audience].detail(data.id));
    }
    return !error;
  };

  const clearError = () => setError(null);

  return { pending, error, run, respond, report, clearError };
};

export default useIssueActions;
