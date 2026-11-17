"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type { Page } from "@/types/access/models";
import type { AccessToken, ListFilters } from "@/types/security/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetTokens = async (params: ListFilters = {}) => {
  try {
    const data = await ApiServiceServer<Page<AccessToken>>({
      url: EndPoints.tokens.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleRevokeToken = async (id: number) => {
  try {
    const data = await ApiServiceServer<AccessToken>({
      url: EndPoints.tokens.revoke(id),
      method: "POST",
      data: {},
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
