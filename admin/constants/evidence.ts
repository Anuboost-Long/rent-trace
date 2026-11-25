import type { EvidenceStatus } from "@/types/evidence/models";

export const EvidenceStatusLabel: Record<EvidenceStatus, string> = {
  PENDING_REVIEW: "Waiting for your landlord",
  APPROVED: "Approved",
  DISPUTED: "Rejected",
  CANCELLED: "Withdrawn",
  EXPIRED: "Expired — send a new report",
};
