"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type {
  CreateUserBody,
  UpdateUserBody,
  UserDetail,
  UserFilters,
  UserOption,
  UserPage,
} from "@/types/users/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetUsers = async (params: UserFilters = {}) => {
  try {
    const data = await ApiServiceServer<UserPage>({
      url: EndPoints.users.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetAllUsers = async (
  params: Pick<UserFilters, "q" | "role" | "status"> = {},
) => {
  try {
    const data = await ApiServiceServer<UserOption[]>({
      url: EndPoints.users.all,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetUser = async (id: number | string) => {
  try {
    const data = await ApiServiceServer<UserDetail>({
      url: EndPoints.users.detail(id),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleCreateUser = async (body: CreateUserBody) => {
  try {
    const data = await ApiServiceServer<UserDetail>({
      url: EndPoints.users.list,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUpdateUser = async (
  id: number | string,
  body: UpdateUserBody,
) => {
  try {
    const data = await ApiServiceServer<UserDetail>({
      url: EndPoints.users.detail(id),
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDeactivateUser = async (id: number | string) => {
  try {
    const data = await ApiServiceServer<UserDetail>({
      url: EndPoints.users.deactivate(id),
      method: "POST",
      data: {},
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleActivateUser = async (id: number | string) => {
  try {
    const data = await ApiServiceServer<UserDetail>({
      url: EndPoints.users.activate(id),
      method: "POST",
      data: {},
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDeleteUser = async (id: number | string) => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.users.detail(id),
      method: "DELETE",
      data: {},
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
