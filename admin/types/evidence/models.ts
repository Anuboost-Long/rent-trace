export type EvidenceStatus =
  "PENDING_REVIEW" | "APPROVED" | "DISPUTED" | "CANCELLED";

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
  submitted_at: string;
  completed_at: string | null;
};

export type EvidenceBody = {
  title: string;
  description: string;
  observed_at: string;
};
