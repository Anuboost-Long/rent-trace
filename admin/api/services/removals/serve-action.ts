"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type { Removal, RemovalPage } from "@/types/removals/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetRemovals = async (params: {
  status?: string;
  page?: number;
}) => {
  try {
    const data = await ApiServiceServer<RemovalPage>({
      url: EndPoints.removals.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetRemoval = async (id: number | string) => {
  try {
    const data = await ApiServiceServer<Removal>({
      url: EndPoints.removals.detail(id),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDecideRemoval = async (
  id: number,
  action: "approve" | "reject",
  idempotencyKey: string,
  reason: string,
) => {
  try {
    const data = await ApiServiceServer<Removal>({
      url: EndPoints.removals.decide(id, action),
      method: "POST",
      data: { idempotency_key: idempotencyKey, reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
