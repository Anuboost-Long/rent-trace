export type CorrectionStatus = "PENDING_REVIEW" | "APPROVED" | "REJECTED";

export type Correction = {
  id: number;
  status: CorrectionStatus;
  requester_side: "TENANT" | "LANDLORD";
  record_id: number;
  unit_id: number;
  place: string;
  requested_by_name: string;
  current_title: string;
  current_description: string | null;
  proposed_title: string;
  proposed_description: string;
  what_is_incorrect: string;
  why_change_needed: string;
  admin_reason: string | null;
  submitted_at: string;
  completed_at: string | null;
};

export type CorrectionPage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: Correction[];
};
