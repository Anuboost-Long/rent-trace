"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type {
  AssignBody,
  ClosureAnswer,
  ClosureBody,
  IssueDetail,
  IssueFilters,
  IssuePage,
  ReportIssueBody,
} from "@/types/maintenance/models";
import type { ServiceCategory } from "@/types/providers/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetIssues = async (params: IssueFilters = {}) => {
  try {
    const data = await ApiServiceServer<IssuePage>({
      url: EndPoints.maintenance.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetIssue = async (id: number | string) => {
  try {
    const data = await ApiServiceServer<IssueDetail>({
      url: EndPoints.maintenance.detail(id),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleReportIssue = async (body: ReportIssueBody) => {
  try {
    const data = await ApiServiceServer<IssueDetail>({
      url: EndPoints.maintenance.list,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleIssueAction = async (
  id: number,
  path:
    | "acknowledge"
    | "start"
    | "closure"
    | "closure/withdraw"
    | "close"
    | "assignment"
    | "assignment/complete",
  body?: ClosureBody | AssignBody,
) => {
  try {
    const data = await ApiServiceServer<IssueDetail>({
      url: EndPoints.maintenance.action(id, path),
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleRespondClosure = async (
  id: number,
  proposalId: number,
  answer: ClosureAnswer,
) => {
  try {
    const data = await ApiServiceServer<IssueDetail>({
      url: EndPoints.maintenance.respond(id, proposalId, answer),
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetIssueCategories = async () => {
  try {
    const data = await ApiServiceServer<ServiceCategory[]>({
      url: EndPoints.maintenance.categories,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
