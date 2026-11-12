"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type {
  AcceptedInvitation,
  CreateTenancyBody,
  HousemateRequest,
  Invitation,
  InvitationAction,
  InviteTenantBody,
  MyInvitation,
  MyTenancy,
  MyTenancyDetail,
  TenancyAction,
  TenancyAudience,
  TenancyDetail,
  TenancyFilters,
  TenancyPage,
} from "@/types/tenancies/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

const apiFor = (audience: TenancyAudience) =>
  audience === "landlord" ? EndPoints.landlord_tenancies : EndPoints.tenancies;

export const handleGetTenancies = async (
  params: TenancyFilters = {},
  audience: TenancyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<TenancyPage>({
      url: apiFor(audience).list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetTenancy = async (
  id: number | string,
  audience: TenancyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<TenancyDetail>({
      url: apiFor(audience).detail(id),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleCreateTenancy = async (
  body: CreateTenancyBody,
  audience: TenancyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<TenancyDetail>({
      url: apiFor(audience).list,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleInviteTenant = async (
  tenancyId: number,
  body: InviteTenantBody,
  audience: TenancyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<Invitation>({
      url: apiFor(audience).invitations(tenancyId),
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleInvitationAction = async (
  tenancyId: number,
  invitationId: number,
  action: InvitationAction,
  audience: TenancyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<Invitation>({
      url: apiFor(audience).invitation_action(tenancyId, invitationId, action),
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleAcceptInvitation = async (token: string) => {
  try {
    const data = await ApiServiceServer<AcceptedInvitation>({
      url: EndPoints.tenant_invitations.accept,
      method: "POST",
      data: { token },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetMyInvitations = async () => {
  try {
    const data = await ApiServiceServer<MyInvitation[]>({
      url: EndPoints.tenant_invitations.list,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleAcceptInvitationById = async (id: number) => {
  try {
    const data = await ApiServiceServer<AcceptedInvitation>({
      url: EndPoints.tenant_invitations.accept_by_id(id),
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetMyTenancies = async () => {
  try {
    const data = await ApiServiceServer<MyTenancy[]>({
      url: EndPoints.tenant_tenancies.list,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetMyTenancy = async (id: number | string) => {
  try {
    const data = await ApiServiceServer<MyTenancyDetail>({
      url: EndPoints.tenant_tenancies.detail(id),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleTenancyAction = async (
  id: number,
  action: TenancyAction,
  audience: TenancyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<TenancyDetail>({
      url: apiFor(audience).action(id, action),
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleRequestHousemate = async (
  tenancyId: number,
  email: string,
) => {
  try {
    const data = await ApiServiceServer<HousemateRequest>({
      url: EndPoints.tenant_tenancies.request_housemate(tenancyId),
      method: "POST",
      data: { email },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleWithdrawHousemate = async (
  tenancyId: number,
  invitationId: number,
) => {
  try {
    const data = await ApiServiceServer<HousemateRequest>({
      url: EndPoints.tenant_tenancies.withdraw_housemate(
        tenancyId,
        invitationId,
      ),
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
