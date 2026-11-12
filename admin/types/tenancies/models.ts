export type TenancyAudience = "admin" | "landlord";

export type TenancyStatus =
  "DRAFT" | "PENDING" | "ACTIVE" | "ENDED" | "CANCELLED";

export type InvitationStatus = "PENDING" | "ACCEPTED" | "REVOKED" | "EXPIRED";

type PlaceRef = {
  property: { id: number; name: string | null; suburb: string };
  unit: { id: number; name: string };
};

export type TenancySummary = PlaceRef & {
  id: number;
  reference_no: string;
  status: TenancyStatus;
  start_date: string;
  end_date: string | null;
  tenant_count: number;
  pending_invitations: number;
};

export type Tenant = {
  user_id: number;
  first_name: string;
  last_name: string;
  is_primary: boolean;
  joined_at: string;
};

export type Invitation = {
  id: number;
  email: string;
  is_primary: boolean;
  status: InvitationStatus;
  expires_at: string;
  created_at: string;
  accepted_at: string | null;
  revoked_at: string | null;
};

export type TenancyDetail = PlaceRef & {
  id: number;
  reference_no: string;
  status: TenancyStatus;
  tenancy_type: string;
  start_date: string;
  end_date: string | null;
  notes: string | null;
  tenants: Tenant[];
  invitations: Invitation[];
};

export type TenancyPage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: TenancySummary[];
};

export type TenancyFilters = {
  q?: string;
  status?: string;
  page?: number;
};

export type CreateTenancyBody = {
  property_unit_id: number;
  start_date: string;
  end_date?: string;
  notes?: string;
};

export type InviteTenantBody = { email: string; is_primary: boolean };

export type InvitationAction = "resend" | "revoke";

export type MyInvitation = {
  id: number;
  property_name: string;
  unit_name: string;
  invited_by: string;
  is_primary: boolean;
  expires_at: string;
};

export type AcceptedInvitation = {
  id: number;
  property_name: string;
  unit_name: string;
  invited_by: string;
  is_primary: boolean;
};
