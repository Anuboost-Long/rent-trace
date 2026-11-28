"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer, ApiUploadServer } from "@/api/api-helper";
import type {
  AssignBody,
  ClosureAnswer,
  ClosureBody,
  IssueDetail,
  IssueFilters,
  IssuePage,
  MaintenanceAudience,
  ReportIssueBody,
} from "@/types/maintenance/models";
import type { ServiceCategory } from "@/types/providers/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetIssues = async (
  params: IssueFilters = {},
  audience?: MaintenanceAudience,
) => {
  try {
    const data = await ApiServiceServer<IssuePage>({
      url:
        audience === "admin"
          ? EndPoints.admin_maintenance.list
          : EndPoints.maintenance.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetIssue = async (
  id: number | string,
  audience?: MaintenanceAudience,
) => {
  try {
    const data = await ApiServiceServer<IssueDetail>({
      url:
        audience === "admin"
          ? EndPoints.admin_maintenance.detail(id)
          : EndPoints.maintenance.detail(id),
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
  audience?: MaintenanceAudience,
) => {
  try {
    const data = await ApiServiceServer<IssueDetail>({
      url:
        audience === "admin"
          ? EndPoints.admin_maintenance.action(id, path)
          : EndPoints.maintenance.action(id, path),
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
  audience?: MaintenanceAudience,
) => {
  try {
    const data = await ApiServiceServer<IssueDetail>({
      url:
        audience === "admin"
          ? EndPoints.admin_maintenance.respond(id, proposalId, answer)
          : EndPoints.maintenance.respond(id, proposalId, answer),
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

export const handleAddIssuePhoto = async (id: number, formData: FormData) => {
  try {
    const data = await ApiUploadServer<IssueDetail>({
      url: EndPoints.maintenance.photos(id),
      formData,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleRemoveIssuePhoto = async (id: number, fileId: number) => {
  try {
    const data = await ApiServiceServer<IssueDetail>({
      url: EndPoints.maintenance.photo(id, fileId),
      method: "DELETE",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
