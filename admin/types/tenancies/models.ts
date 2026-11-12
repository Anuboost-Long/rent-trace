import type { TenantCondition } from "@/types/conditions/models";

export type TenancyAudience = "admin" | "landlord";

export type TenancyStatus =
  "DRAFT" | "PENDING" | "ACTIVE" | "ENDED" | "CANCELLED";

export type InvitationStatus =
  "PENDING" | "ACCEPTED" | "DECLINED" | "REVOKED" | "EXPIRED";

export type Approver = "LANDLORD" | "INVITEE";

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
  requested_by_tenant: boolean;
  requested_by: string | null;
  landlord_decision: "APPROVED" | "DECLINED" | null;
  invitee_accepted_at: string | null;
  waiting_on: Approver[];
  expires_at: string;
  created_at: string;
  accepted_at: string | null;
  revoked_at: string | null;
};

export type MoneyTerms = {
  rent_amount: string | null;
  rent_frequency: string | null;
  bond_amount: string | null;
};

export type TermChangeStatus =
  | "PENDING"
  | "EXPIRED"
  | "APPLIED"
  | "DECLINED"
  | "WITHDRAWN"
  | "SUPERSEDED"
  | "CLOSED";

export type TermApproval = {
  name: string;
  decision: "APPROVED" | "DECLINED" | null;
};

export type TermChange = {
  id: number;
  status: TermChangeStatus;
  requires_approval: boolean;
  proposed_by: string | null;
  created_at: string;
  decided_at: string | null;
  expires_at: string | null;
  before: MoneyTerms;
  after: MoneyTerms;
  approvals: TermApproval[];
  my_decision?: "APPROVED" | "DECLINED" | null;
};

export type TenancyDetail = PlaceRef & {
  id: number;
  max_occupants: number | null;
  people_count: number;
  reference_no: string;
  status: TenancyStatus;
  tenancy_type: string;
  start_date: string;
  end_date: string | null;
  notes: string | null;
  rent_amount: string | null;
  rent_frequency: string | null;
  bond_amount: string | null;
  currency: string;
  tenants: Tenant[];
  invitations: Invitation[];
  pending_change: TermChange | null;
  term_history: TermChange[];
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

export type TenancyTerms = {
  start_date: string;
  end_date: string | null;
  notes: string | null;
  rent_amount: string | null;
  rent_frequency: string | null;
  bond_amount: string | null;
};

export type CreateTenancyBody = TenancyTerms & { property_unit_id: number };

export type UpdateTenancyBody = TenancyTerms;

export type InviteTenantBody = { email: string; is_primary: boolean };

export type InvitationAction = "resend" | "revoke" | "approve" | "decline";

export type TenancyAction = "activate" | "end" | "cancel";

export type TermChangeAnswer = "approve" | "decline";

export type MyInvitation = {
  id: number;
  property_name: string;
  unit_name: string;
  invited_by: string;
  is_primary: boolean;
  requested_by_tenant: boolean;
  joined: boolean;
  waiting_on: Approver[];
  expires_at: string;
};

export type AcceptedInvitation = {
  id: number;
  property_name: string;
  unit_name: string;
  invited_by: string;
  is_primary: boolean;
  joined: boolean;
  waiting_on: Approver[];
};

export type MyTenancy = {
  id: number;
  reference_no: string;
  status: TenancyStatus;
  start_date: string;
  end_date: string | null;
  rent_amount: string | null;
  rent_frequency: string | null;
  bond_amount: string | null;
  currency: string;
  unit: { id: number; name: string };
  property: { id: number; name: string | null; suburb: string; state: string };
  landlord: string | null;
  is_primary: boolean;
  joined_at: string;
  left_at: string | null;
  is_current: boolean;
  max_occupants: number | null;
  people_count: number;
};

export type Housemate = {
  first_name: string;
  last_name: string;
  is_primary: boolean;
};

export type HousemateRequest = {
  id: number;
  email: string;
  status: InvitationStatus;
  waiting_on: Approver[];
  created_at: string;
  expires_at: string;
};

export type MyTenancyDetail = MyTenancy & {
  housemates: Housemate[];
  housemate_requests: HousemateRequest[];
  unit_conditions: TenantCondition[];
  pending_change: TermChange | null;
  term_history: TermChange[];
};
