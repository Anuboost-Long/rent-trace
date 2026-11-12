export type RequestedListing = {
  id: number;
  title: string;
  suburb: string;
  state: string;
};

export type LandlordContact = {
  name: string;
  email: string;
  phone_number: string | null;
};

type ContactRequestBase = {
  id: number;
  status: string;
  message: string;
  created_at: string;
  decided_at: string | null;
  listing: RequestedListing;
  unit: { id: number; name: string } | null;
};

export type TenantContactRequest = ContactRequestBase & {
  landlord: LandlordContact | null;
};

export type TenantContact = {
  email: string;
  phone_number: string | null;
};

export type LandlordContactRequest = ContactRequestBase & {
  tenant: { id: number; first_name: string; last_name: string };
  tenant_contact: TenantContact | null;
};

export type ContactRequestFilters = {
  status?: string;
  page?: number;
  page_size?: number;
};

export type SendContactRequestBody = {
  listing_id: number;
  unit_id: number | null;
  message: string;
};
