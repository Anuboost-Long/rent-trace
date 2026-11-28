"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer, ApiUploadServer } from "@/api/api-helper";
import type {
  DocumentCase,
  DocumentCasePage,
  PaperDocument,
} from "@/types/documents/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetTenantDocuments = async (tenancyId: number | string) => {
  try {
    const data = await ApiServiceServer<PaperDocument[]>({
      url: EndPoints.documents.tenant.list(tenancyId),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetUnitDocuments = async (
  audience: "landlord" | "admin",
  unitId: number,
) => {
  try {
    const data = await ApiServiceServer<PaperDocument[]>({
      url: EndPoints.documents[audience].list,
      method: "GET",
      params: { unit_id: unitId },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUploadTenantDocument = async (
  tenancyId: number,
  formData: FormData,
) => {
  try {
    const data = await ApiUploadServer<PaperDocument>({
      url: EndPoints.documents.tenant.list(tenancyId),
      formData,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handlePublishDocument = async (formData: FormData) => {
  try {
    const data = await ApiUploadServer<PaperDocument>({
      url: EndPoints.documents.landlord.list,
      formData,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleAddDocumentVersion = async (
  documentId: number,
  formData: FormData,
) => {
  try {
    const data = await ApiUploadServer<PaperDocument>({
      url: EndPoints.documents.landlord.versions(documentId),
      formData,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleAnswerDocumentVersion = async (
  tenancyId: number,
  versionId: number,
  action: "confirm" | "flag" | "escalate",
  idempotencyKey: string,
  reason?: string,
) => {
  try {
    const data = await ApiServiceServer<PaperDocument>({
      url: EndPoints.documents.tenant.answer(tenancyId, versionId, action),
      method: "POST",
      data:
        action === "escalate"
          ? { reason }
          : { idempotency_key: idempotencyKey, reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleLandlordEscalateVersion = async (
  documentId: number,
  versionId: number,
  reason: string,
) => {
  try {
    const data = await ApiServiceServer<PaperDocument>({
      url: EndPoints.documents.landlord.escalate(documentId, versionId),
      method: "POST",
      data: { reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetDocumentCases = async (params: {
  status?: string;
  page?: number;
}) => {
  try {
    const data = await ApiServiceServer<DocumentCasePage>({
      url: EndPoints.documents.admin.cases,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDecideDocumentCase = async (
  id: number,
  action: "approve" | "reject",
  idempotencyKey: string,
  reason: string,
) => {
  try {
    const data = await ApiServiceServer<DocumentCase>({
      url: EndPoints.documents.admin.decide(id, action),
      method: "POST",
      data: { idempotency_key: idempotencyKey, reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
