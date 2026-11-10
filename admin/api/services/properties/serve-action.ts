"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer, ApiUploadServer } from "@/api/api-helper";
import type {
  CreatePropertyBody,
  OwnerOption,
  PropertyAudience,
  PropertyBody,
  PropertyDetail,
  PropertyFile,
  PropertyFilters,
  PropertyPage,
  PropertyUnit,
  UnitBody,
  UpdatePropertyBody,
} from "@/types/properties/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

const apiFor = (audience: PropertyAudience) =>
  audience === "landlord"
    ? EndPoints.landlord_properties
    : EndPoints.properties;

export const handleGetProperties = async (
  params: PropertyFilters = {},
  audience: PropertyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<PropertyPage>({
      url: apiFor(audience).list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetOwnerOptions = async () => {
  try {
    const data = await ApiServiceServer<OwnerOption[]>({
      url: EndPoints.properties.owner_options,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetProperty = async (
  id: number | string,
  audience: PropertyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<PropertyDetail>({
      url: apiFor(audience).detail(id),
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleCreateProperty = async (
  body: CreatePropertyBody | PropertyBody,
  audience: PropertyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<PropertyDetail>({
      url: apiFor(audience).list,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUpdateProperty = async (
  id: number | string,
  body: UpdatePropertyBody,
  audience: PropertyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<PropertyDetail>({
      url: apiFor(audience).detail(id),
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDeleteProperty = async (id: number | string) => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.properties.detail(id),
      method: "DELETE",
      data: {},
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleCreateUnit = async (
  propertyId: number | string,
  body: UnitBody,
  audience: PropertyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<PropertyUnit>({
      url: apiFor(audience).units(propertyId),
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUpdateUnit = async (
  propertyId: number | string,
  unitId: number,
  body: UnitBody,
  audience: PropertyAudience = "admin",
) => {
  try {
    const data = await ApiServiceServer<PropertyUnit>({
      url: apiFor(audience).unit(propertyId, unitId),
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDeleteUnit = async (
  propertyId: number | string,
  unitId: number,
  audience: PropertyAudience = "admin",
) => {
  try {
    await ApiServiceServer<null>({
      url: apiFor(audience).unit(propertyId, unitId),
      method: "DELETE",
      data: {},
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUploadPropertyFile = async (
  audience: PropertyAudience,
  propertyId: number | string,
  formData: FormData,
  unitId?: number,
) => {
  try {
    const data = await ApiUploadServer<PropertyFile>({
      url: EndPoints.property_files[audience].list(propertyId, unitId),
      formData,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleUpdatePropertyFile = async (
  audience: PropertyAudience,
  propertyId: number | string,
  fileId: number,
  body: Partial<{ caption: string; is_cover: boolean }>,
  unitId?: number,
) => {
  try {
    const data = await ApiServiceServer<PropertyFile>({
      url: EndPoints.property_files[audience].detail(
        propertyId,
        fileId,
        unitId,
      ),
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleDeletePropertyFile = async (
  audience: PropertyAudience,
  propertyId: number | string,
  fileId: number,
  unitId?: number,
) => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.property_files[audience].detail(
        propertyId,
        fileId,
        unitId,
      ),
      method: "DELETE",
      data: {},
    });
    return { data: true, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
