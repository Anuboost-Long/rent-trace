"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type {
  ConditionEvidence,
  EvidenceBody,
  ReviewCase,
  ReviewCasePage,
} from "@/types/evidence/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetMyEvidence = async (tenancyId: number | string) => {
  try {
    const data = await ApiServiceServer<ConditionEvidence[]>({
      url: EndPoints.evidence.mine(tenancyId),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetUnitEvidence = async (unitId: number) => {
  try {
    const data = await ApiServiceServer<ConditionEvidence[]>({
      url: EndPoints.evidence.unit,
      method: "GET",
      params: { unit_id: unitId },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleSubmitEvidence = async (
  tenancyId: number,
  body: EvidenceBody,
) => {
  try {
    const data = await ApiServiceServer<ConditionEvidence>({
      url: EndPoints.evidence.mine(tenancyId),
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleWithdrawEvidence = async (tenancyId: number, id: number) => {
  try {
    const data = await ApiServiceServer<ConditionEvidence>({
      url: EndPoints.evidence.withdraw(tenancyId, id),
      method: "POST",
      data: {},
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleAnswerEvidence = async (
  id: number,
  action: "approve" | "reject",
  idempotencyKey: string,
  reason?: string,
) => {
  try {
    const data = await ApiServiceServer<ConditionEvidence>({
      url: EndPoints.evidence.answer(id, action),
      method: "POST",
      data: { idempotency_key: idempotencyKey, reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleEscalateEvidence = async (
  id: number,
  reason: string,
  tenancyId?: number,
) => {
  try {
    const data = await ApiServiceServer<ConditionEvidence>({
      url:
        tenancyId === undefined
          ? EndPoints.evidence.escalate_landlord(id)
          : EndPoints.evidence.escalate_mine(tenancyId, id),
      method: "POST",
      data: { reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetReviewCases = async (params: {
  status?: string;
  page?: number;
}) => {
  try {
    const data = await ApiServiceServer<ReviewCasePage>({
      url: EndPoints.reviewCases.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDecideCase = async (
  id: number,
  action: "approve" | "reject",
  idempotencyKey: string,
  reason: string,
) => {
  try {
    const data = await ApiServiceServer<ReviewCase>({
      url: EndPoints.reviewCases.decide(id, action),
      method: "POST",
      data: { idempotency_key: idempotencyKey, reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
