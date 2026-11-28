import type { CorrectionStatus } from "@/types/corrections/models";

export const CorrectionStatusLabel: Record<CorrectionStatus, string> = {
  PENDING_REVIEW: "Waiting for a decision",
  APPROVED: "Approved",
  REJECTED: "Rejected",
};

export const CorrectionFilters: { label: string; status?: CorrectionStatus }[] =
  [
    { label: "Waiting" },
    { label: "Approved", status: "APPROVED" },
    { label: "Rejected", status: "REJECTED" },
  ];
