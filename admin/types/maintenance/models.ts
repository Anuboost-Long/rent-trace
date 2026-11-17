import type { ServiceCategory, TenantProvider } from "@/types/providers/models";

export type IssueStatus =
  "REPORTED" | "ACKNOWLEDGED" | "IN_PROGRESS" | "CLOSED";
export type IssuePriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";
export type ClosureOutcome = "FIXED" | "NOT_FIXED_NO_ACTION";

export type IssueAction =
  | "ACKNOWLEDGE"
  | "START"
  | "PROPOSE_CLOSURE"
  | "WITHDRAW_CLOSURE"
  | "APPROVE_CLOSURE"
  | "REJECT_CLOSURE"
  | "CLOSE_VACANT"
  | "ASSIGN_PROVIDER"
  | "COMPLETE_VISIT";

export type MaintenanceAudience = "tenant" | "landlord" | "admin";

export type IssueSummary = {
  id: number;
  title: string;
  priority: IssuePriority;
  status: IssueStatus;
  reported_at: string;
  closed_at: string | null;
  closure_outcome: ClosureOutcome | null;
  unit: { id: number; name: string };
  property: { id: number; name: string | null; suburb: string };
  reported_by_name: string;
  has_open_closure: boolean;
  category: ServiceCategory | null;
};

export type OpenClosure = {
  id: number;
  outcome: ClosureOutcome;
  reason: string;
  proposed_by: string;
  proposer_side: "LANDLORD" | "TENANT";
  created_at: string;
};

export type IssueHistoryEntry = {
  kind: "STATUS" | "PROVIDER_BOOKED" | "VISIT_DONE" | "CLOSING_REJECTED";
  from_status: IssueStatus | null;
  to_status: IssueStatus | null;
  trigger: string;
  actor: string;
  on_behalf_of: string | null;
  reason: string;
  created_at: string;
};

export type IssueDetail = IssueSummary & {
  description: string;
  acknowledged_at: string | null;
  work_started_at: string | null;
  open_closure: OpenClosure | null;
  history: IssueHistoryEntry[];
  actions: IssueAction[];
  my_side: "LANDLORD" | "TENANT" | null;
  assignment: IssueAssignment | null;
  provider_options: ProviderOption[];
};

export type IssueAssignment = {
  id: number;
  scheduled_at: string | null;
  completed_at: string | null;
  created_at: string;
  provider: Omit<TenantProvider, "is_recommended">;
};

export type ProviderOption = {
  id: number;
  business_name: string;
  is_recommended: boolean;
  matches_category: boolean;
};

export type AssignBody = {
  service_provider_id: number;
  scheduled_at: string | null;
};

export type IssuePage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: IssueSummary[];
};

export type IssueFilters = { status?: string; q?: string; page?: number };

export type ReportIssueBody = {
  tenancy_id: number;
  title: string;
  description: string;
  priority: IssuePriority;
  category_code: string | null;
};

export type ClosureBody = { outcome: ClosureOutcome; reason: string };

export type ClosureAnswer = "approve" | "reject";
