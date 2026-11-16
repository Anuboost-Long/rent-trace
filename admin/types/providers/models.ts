export type ServiceCategory = { code: string; name: string };

export type ProviderProperty = {
  property_id: number;
  property_name: string;
  is_recommended: boolean;
  contract_notes: string | null;
};

export type ServiceProvider = {
  id: number;
  business_name: string;
  contact_name: string | null;
  phone_number: string | null;
  email: string | null;
  website: string | null;
  address: string | null;
  description: string | null;
  categories: ServiceCategory[];
  properties: ProviderProperty[];
};

export type AdminServiceProvider = Omit<ServiceProvider, "properties"> & {
  owner: { id: number; first_name: string; last_name: string };
  properties: Omit<ProviderProperty, "contract_notes">[];
};

export type AdminProviderPage = Omit<ProviderPage, "results"> & {
  results: AdminServiceProvider[];
};

export type ProviderPage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: ServiceProvider[];
};

export type ProviderFilters = { q?: string; category?: string; page?: number };

export type ProviderBody = {
  business_name: string;
  contact_name: string | null;
  phone_number: string | null;
  email: string | null;
  website: string | null;
  address: string | null;
  description: string | null;
  category_codes: string[];
  properties: {
    property_id: number;
    is_recommended: boolean;
    contract_notes: string | null;
  }[];
};

export type TenantProvider = Omit<ServiceProvider, "properties"> & {
  is_recommended: boolean;
};
