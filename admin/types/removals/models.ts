export type RemovalStatus = "PENDING_REVIEW" | "APPROVED" | "REJECTED";

export type RemovalItem = {
  record_id: number;
  title: string | null;
  include_descendants: boolean;
};

export type Removal = {
  id: number;
  status: RemovalStatus;
  requester_side: "TENANT" | "LANDLORD";
  requested_by_name: string;
  reason: string;
  items: RemovalItem[];
  admin_reason: string | null;
  submitted_at: string;
  completed_at: string | null;
};

export type RemovalPage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: Removal[];
};
