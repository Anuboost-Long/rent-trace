"use client";
import {
  handleGetProperties,
  handleGetProperty,
} from "@/api/services/properties/serve-action";
import { handleCreateTenancy } from "@/api/services/tenancies/serve-action";
import type { ComboboxOption } from "@/components/common/inputs/combobox-input";
import { TenancyRoutes } from "@/constants/tenancies";
import type { PropertyUnit } from "@/types/properties/models";
import type {
  CreateTenancyBody,
  TenancyAudience,
} from "@/types/tenancies/models";
import { propertyTitle } from "@/utils/property-address";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

export type InitialProperty = {
  option: ComboboxOption;
  units: PropertyUnit[];
};

const propertyFinder =
  (audience: TenancyAudience) =>
  async (query: string): Promise<ComboboxOption[]> => {
    const { data } = await handleGetProperties(
      { q: query, page_size: 8 },
      audience,
    );
    return (data?.results ?? []).map((property) => ({
      value: String(property.id),
      label: propertyTitle(property),
      hint: `${property.suburb} ${property.state}`,
    }));
  };

export const findProperties = {
  admin: propertyFinder("admin"),
  landlord: propertyFinder("landlord"),
};

const onlyUnitId = (units: PropertyUnit[]) =>
  units.length === 1 ? String(units[0].id) : "";

const useCreateTenancy = (
  audience: TenancyAudience,
  initial: InitialProperty | null,
) => {
  const router = useRouter();
  const [property, setProperty] = useState(initial?.option ?? null);
  const [units, setUnits] = useState(initial?.units ?? []);
  const [unitId, setUnitId] = useState(onlyUnitId(initial?.units ?? []));
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const chooseProperty = async (option: ComboboxOption) => {
    setProperty(option);
    setUnits([]);
    setUnitId("");
    const { data } = await handleGetProperty(option.value, audience);
    const found = data?.units ?? [];
    setUnits(found);
    setUnitId(onlyUnitId(found));
  };

  const createTenancy = async (
    body: Omit<CreateTenancyBody, "property_unit_id">,
  ) => {
    setPending(true);
    setError(null);
    const { data, error } = await handleCreateTenancy(
      { ...body, property_unit_id: Number(unitId) },
      audience,
    );
    setPending(false);
    setError(error);
    if (data) {
      toast.success("Tenancy created");
      router.push(TenancyRoutes[audience].detail(data.id));
    }
  };

  return {
    property,
    units,
    unitId,
    setUnitId,
    chooseProperty,
    pending,
    error,
    createTenancy,
  };
};

export default useCreateTenancy;
