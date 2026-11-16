"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type { Page } from "@/types/access/models";
import type {
  AdminContactRequest,
  ContactRequestFilters,
  LandlordContactRequest,
  SendContactRequestBody,
  TenantContactRequest,
} from "@/types/contact-requests/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetMyContactRequests = async (
  params: ContactRequestFilters = {},
) => {
  try {
    const data = await ApiServiceServer<Page<TenantContactRequest>>({
      url: EndPoints.contact_requests.tenant.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleSendContactRequest = async (
  body: SendContactRequestBody,
) => {
  try {
    const data = await ApiServiceServer<TenantContactRequest>({
      url: EndPoints.contact_requests.tenant.list,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleCancelContactRequest = async (id: number) => {
  try {
    const data = await ApiServiceServer<TenantContactRequest>({
      url: EndPoints.contact_requests.tenant.cancel(id),
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleGetAdminContactRequests = async (
  params: ContactRequestFilters = {},
) => {
  try {
    const data = await ApiServiceServer<Page<AdminContactRequest>>({
      url: EndPoints.contact_requests.admin.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetLandlordContactRequests = async (
  params: ContactRequestFilters = {},
) => {
  try {
    const data = await ApiServiceServer<Page<LandlordContactRequest>>({
      url: EndPoints.contact_requests.landlord.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleRespondToContactRequest = async (
  id: number,
  action: "accept" | "decline" | "revoke",
) => {
  try {
    const data = await ApiServiceServer<LandlordContactRequest>({
      url: EndPoints.contact_requests.landlord.respond(id, action),
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};
