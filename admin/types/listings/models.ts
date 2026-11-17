export type Rent = { amount: string; frequency: string };

export type ListingSummary = {
  id: number;
  title: string;
  property_type: string;
  suburb: string;
  state: string;
  postcode: string;
  cover_file_id: number | null;
  photo_count: number;
  unit_count: number;
  from_rent: Rent | null;
};

export type ListingPhoto = {
  id: number;
  unit_id: number | null;
  caption: string | null;
  is_cover: boolean;
};

export type ListingUnit = {
  id: number;
  name: string;
  unit_type: string;
  description: string | null;
  occupancy_status: string;
  rent: Rent | null;
  photos: ListingPhoto[];
};

export type ListingDetail = ListingSummary & {
  public_description: string | null;
  listed_by: string | null;
  photos: ListingPhoto[];
  units: ListingUnit[];
};

export type ListingPage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: ListingSummary[];
};

export type Place = { state: string; suburb: string; listings: number };

export type ListingFilters = {
  q?: string;
  state?: string;
  suburb?: string;
  type?: string;
  min_rent?: string;
  max_rent?: string;
  sort?: string;
  page?: number;
  page_size?: number;
};
