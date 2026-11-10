"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type {
  GrantListItem,
  Page,
  PermissionBody,
  PermissionHolders,
  PermissionItem,
  RoleBody,
  RoleMember,
  RoleItem,
  UserPermissions,
} from "@/types/access/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetPermissions = async () => {
  try {
    const data = await ApiServiceServer<PermissionItem[]>({
      url: EndPoints.access.permissions,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetRoles = async () => {
  try {
    const data = await ApiServiceServer<RoleItem[]>({
      url: EndPoints.access.roles,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleCreateRole = async (body: RoleBody & { name: string }) => {
  try {
    const data = await ApiServiceServer<RoleItem>({
      url: EndPoints.access.roles,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUpdateRole = async (code: string, body: RoleBody) => {
  try {
    const data = await ApiServiceServer<RoleItem>({
      url: EndPoints.access.role(code),
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetUserPermissions = async (id: number | string) => {
  try {
    const data = await ApiServiceServer<UserPermissions>({
      url: EndPoints.access.user_permissions(id),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGrantPermission = async (
  id: number | string,
  permission: string,
  reason: string,
) => {
  try {
    const data = await ApiServiceServer<UserPermissions>({
      url: EndPoints.access.grants(id),
      method: "POST",
      data: { permission, reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleRevokePermission = async (
  id: number | string,
  permission: string,
) => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.access.grant(id, permission),
      method: "DELETE",
      data: {},
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleCreatePermission = async (body: {
  code: string;
  name: string;
  is_admin_only: boolean;
}) => {
  try {
    const data = await ApiServiceServer<PermissionItem>({
      url: EndPoints.access.permissions,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUpdatePermission = async (
  code: string,
  body: PermissionBody,
) => {
  try {
    const data = await ApiServiceServer<PermissionItem>({
      url: EndPoints.access.permission(code),
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetPermissionHolders = async (code: string) => {
  try {
    const data = await ApiServiceServer<PermissionHolders>({
      url: EndPoints.access.holders(code),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetGrants = async (params: {
  q?: string;
  permission?: string;
  page?: number;
}) => {
  try {
    const data = await ApiServiceServer<Page<GrantListItem>>({
      url: EndPoints.access.grant_list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetRoleMembers = async (roleCode: string, page = 1) => {
  try {
    const data = await ApiServiceServer<Page<RoleMember>>({
      url: EndPoints.access.members(roleCode),
      method: "GET",
      params: { page, page_size: 100 },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleAddRoleMember = async (roleCode: string, userId: number) => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.access.members(roleCode),
      method: "POST",
      data: { user_id: userId },
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleRemoveRoleMember = async (
  roleCode: string,
  userId: number,
) => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.access.member(roleCode, userId),
      method: "DELETE",
      data: {},
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
