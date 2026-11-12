"use server";
import { EndPoints } from "@/api/api-config";
import { ApiPublicServer } from "@/api/api-helper";
import type {
  ListingDetail,
  ListingFilters,
  ListingPage,
  Place,
} from "@/types/listings/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

export const handleGetListings = async (params: ListingFilters = {}) => {
  try {
    const data = await ApiPublicServer<ListingPage>({
      url: EndPoints.listings.list,
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleGetListing = async (id: number | string) => {
  try {
    const data = await ApiPublicServer<ListingDetail>({
      url: EndPoints.listings.detail(id),
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleGetPlaces = async () => {
  try {
    const data = await ApiPublicServer<Place[]>({
      url: EndPoints.listings.places,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};
