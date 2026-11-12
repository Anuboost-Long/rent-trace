"use client";
import {
  handleIssueAction,
  handleReportIssue,
  handleRespondClosure,
} from "@/api/services/maintenance/serve-action";
import { IssueRoutes } from "@/constants/maintenance";
import type { ApiFailure } from "@/types/api/common";
import type {
  ClosureAnswer,
  ClosureBody,
  MaintenanceAudience,
  ReportIssueBody,
} from "@/types/maintenance/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

type IssuePath = Parameters<typeof handleIssueAction>[1];

const useIssueActions = (audience: MaintenanceAudience, issueId?: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const finish = (failure: ApiFailure | null) => {
    setPending(false);
    setError(failure);
    if (!failure) router.refresh();
    return !failure;
  };

  const run = async (path: IssuePath, body?: ClosureBody) => {
    if (issueId === undefined) return false;
    setPending(true);
    setError(null);
    const { error } = await handleIssueAction(issueId, path, body);
    return finish(error);
  };

  const respond = async (proposalId: number, answer: ClosureAnswer) => {
    if (issueId === undefined) return false;
    setPending(true);
    setError(null);
    const { error } = await handleRespondClosure(issueId, proposalId, answer);
    return finish(error);
  };

  const report = async (body: ReportIssueBody) => {
    setPending(true);
    setError(null);
    const { data, error } = await handleReportIssue(body);
    setPending(false);
    setError(error);
    if (data) router.push(IssueRoutes[audience].detail(data.id));
    return !error;
  };

  const clearError = () => setError(null);

  return { pending, error, run, respond, report, clearError };
};

export default useIssueActions;
