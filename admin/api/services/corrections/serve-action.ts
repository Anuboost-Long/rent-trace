"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type { Correction, CorrectionPage } from "@/types/corrections/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetCorrections = async (params: {
  status?: string;
  page?: number;
}) => {
  try {
    const data = await ApiServiceServer<CorrectionPage>({
      url: EndPoints.corrections.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetCorrection = async (id: number | string) => {
  try {
    const data = await ApiServiceServer<Correction>({
      url: EndPoints.corrections.detail(id),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDecideCorrection = async (
  id: number,
  action: "approve" | "reject",
  idempotencyKey: string,
  reason: string,
) => {
  try {
    const data = await ApiServiceServer<Correction>({
      url: EndPoints.corrections.decide(id, action),
      method: "POST",
      data: { idempotency_key: idempotencyKey, reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
