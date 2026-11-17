"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type {
  PropertyProvider,
  ProviderLinkBody,
  AdminProviderPage,
  ProviderBody,
  ProviderFilters,
  ProviderPage,
  ServiceCategory,
  ServiceProvider,
  TenantProvider,
} from "@/types/providers/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetAdminProviders = async (params: ProviderFilters = {}) => {
  try {
    const data = await ApiServiceServer<AdminProviderPage>({
      url: EndPoints.admin_providers.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetAdminServiceCategories = async () => {
  try {
    const data = await ApiServiceServer<ServiceCategory[]>({
      url: EndPoints.admin_providers.categories,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetProviders = async (params: ProviderFilters = {}) => {
  try {
    const data = await ApiServiceServer<ProviderPage>({
      url: EndPoints.providers.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetProvider = async (id: number | string) => {
  try {
    const data = await ApiServiceServer<ServiceProvider>({
      url: EndPoints.providers.detail(id),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetServiceCategories = async () => {
  try {
    const data = await ApiServiceServer<ServiceCategory[]>({
      url: EndPoints.providers.categories,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleCreateProvider = async (body: ProviderBody) => {
  try {
    const data = await ApiServiceServer<ServiceProvider>({
      url: EndPoints.providers.list,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUpdateProvider = async (id: number, body: ProviderBody) => {
  try {
    const data = await ApiServiceServer<ServiceProvider>({
      url: EndPoints.providers.detail(id),
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDeleteProvider = async (id: number) => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.providers.detail(id),
      method: "DELETE",
      data: {},
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetMyPropertyProviders = async (
  tenancyId: number | string,
) => {
  try {
    const data = await ApiServiceServer<TenantProvider[]>({
      url: EndPoints.tenant_tenancies.providers(tenancyId),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetPropertyProviders = async (
  propertyId: number | string,
) => {
  try {
    const data = await ApiServiceServer<PropertyProvider[]>({
      url: EndPoints.property_providers.list(propertyId),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleLinkProviders = async (
  propertyId: number,
  providerIds: number[],
) => {
  try {
    const data = await ApiServiceServer<PropertyProvider[]>({
      url: EndPoints.property_providers.list(propertyId),
      method: "POST",
      data: { provider_ids: providerIds },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUpdateProviderLink = async (
  propertyId: number,
  providerId: number,
  body: ProviderLinkBody,
) => {
  try {
    const data = await ApiServiceServer<PropertyProvider>({
      url: EndPoints.property_providers.detail(propertyId, providerId),
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUnlinkProvider = async (
  propertyId: number,
  providerId: number,
) => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.property_providers.detail(propertyId, providerId),
      method: "DELETE",
      data: {},
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
