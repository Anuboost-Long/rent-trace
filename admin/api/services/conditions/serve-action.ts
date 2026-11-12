"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type { ConditionBody, UnitCondition } from "@/types/conditions/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetConditions = async (unitId: number) => {
  try {
    const data = await ApiServiceServer<UnitCondition[]>({
      url: EndPoints.conditions.list,
      method: "GET",
      params: { unit_id: unitId },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleCreateCondition = async (
  unitId: number,
  body: ConditionBody,
) => {
  try {
    const data = await ApiServiceServer<UnitCondition>({
      url: EndPoints.conditions.list,
      method: "POST",
      data: { unit_id: unitId, ...body },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUpdateCondition = async (
  id: number,
  body: Partial<ConditionBody>,
) => {
  try {
    const data = await ApiServiceServer<UnitCondition>({
      url: EndPoints.conditions.detail(id),
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDeleteCondition = async (id: number) => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.conditions.detail(id),
      method: "DELETE",
      data: {},
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
