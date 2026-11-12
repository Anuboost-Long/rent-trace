export type PropertyStatus =
  "ACTIVE" | "INACTIVE" | "UNDER_MAINTENANCE" | "ARCHIVED";

export type OwnerOption = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
};

export type PropertyOwner = {
  owner: OwnerOption;
  is_primary_owner: boolean;
  ownership_percentage: string | null;
  valid_from: string;
};

export type PropertyUnit = {
  id: number;
  name: string;
  unit_number: string | null;
  unit_type: string;
  description: string | null;
  is_public: boolean;
  occupancy_status: string;
  rent_amount: string | null;
  rent_frequency: string | null;
};

export type PropertyAudience = "admin" | "landlord";

export type PropertyFileKind = "PHOTO" | "DOCUMENT";

export type PropertyFile = {
  id: number;
  unit_id: number | null;
  kind: PropertyFileKind;
  caption: string | null;
  is_cover: boolean;
  sort_order: number;
  original_name: string;
  mime_type: string;
  size_bytes: number;
  created_at: string;
};

export type PropertySummary = {
  id: number;
  property_name: string | null;
  address_line_1: string;
  address_line_2: string | null;
  suburb: string;
  state: string;
  postcode: string;
  country: string;
  property_type: string;
  property_status: PropertyStatus;
  listing_status: string;
  owner: OwnerOption | null;
  unit_count: number;
  created_at: string;
};

export type PropertyDetail = PropertySummary & {
  public_description: string | null;
  private_notes: string | null;
  updated_at: string;
  owners: PropertyOwner[];
  units: PropertyUnit[];
  files: PropertyFile[];
};

export type PropertyPage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: PropertySummary[];
};

export type PropertyFilters = {
  q?: string;
  status?: string;
  page?: number;
  page_size?: number;
};

export type PropertyBody = {
  property_name: string;
  address_line_1: string;
  address_line_2: string;
  suburb: string;
  state: string;
  postcode: string;
  country: string;
  property_type: string;
  public_description: string;
  private_notes: string;
};

export type CreatePropertyBody = PropertyBody & { owner_id: number };

export type UpdatePropertyBody = PropertyBody & {
  property_status: PropertyStatus;
};

export type UnitBody = {
  name: string;
  unit_number: string;
  unit_type: string;
  description: string;
  is_public: boolean;
  rent_amount: string | null;
  rent_frequency: string | null;
};
