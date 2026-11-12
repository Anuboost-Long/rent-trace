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
  | "CLOSE_VACANT";

export type MaintenanceAudience = "tenant" | "landlord";

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
  sequence_no: number;
  from_status: IssueStatus | null;
  to_status: IssueStatus;
  trigger: string;
  actor: string;
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
};

export type IssuePage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: IssueSummary[];
};

export type IssueFilters = { status?: string; page?: number };

export type ReportIssueBody = {
  tenancy_id: number;
  title: string;
  description: string;
  priority: IssuePriority;
};

export type ClosureBody = { outcome: ClosureOutcome; reason: string };

export type ClosureAnswer = "approve" | "reject";
