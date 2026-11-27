export type EvidenceStatus =
  | "PENDING_REVIEW"
  | "APPROVED"
  | "DISPUTED"
  | "REJECTED"
  | "CANCELLED"
  | "EXPIRED";

export type EvidencePhoto = { id: number; name: string };

export type ConditionEvidence = {
  id: number;
  status: EvidenceStatus;
  title: string;
  description: string | null;
  observed_at: string;
  unit_id: number;
  tenancy_id: number;
  author: string;
  rejection_reason: string | null;
  photos: EvidencePhoto[];
  escalated_at: string | null;
  admin_reason: string | null;
  submitted_at: string;
  completed_at: string | null;
};

export type EvidenceBody = {
  title: string;
  description: string;
  observed_at: string;
};

export type ReviewCase = {
  id: number;
  status: "PENDING_REVIEW" | "APPROVED" | "REJECTED";
  report_id: number;
  title: string;
  description: string | null;
  observed_at: string;
  unit_id: number;
  tenancy_id: number;
  place: string;
  author: string;
  landlord_rejection_reason: string | null;
  photos: EvidencePhoto[];
  escalated_by: string | null;
  escalated_at: string | null;
  escalation_reason: string | null;
  admin_reason: string | null;
  completed_at: string | null;
};

export type ReviewCasePage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: ReviewCase[];
};

export type EvidenceAudience = "tenant" | "landlord";
