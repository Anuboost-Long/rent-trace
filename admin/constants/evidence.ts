import type {
  ConditionEvidence,
  EvidenceAudience,
} from "@/types/evidence/models";

export const canEscalate = (report: ConditionEvidence) =>
  report.status === "EXPIRED" ||
  (report.status === "DISPUTED" && report.escalated_at === null);

export const evidenceLabel = (
  report: ConditionEvidence,
  audience: EvidenceAudience,
) => {
  const tenant = audience === "tenant";
  switch (report.status) {
    case "PENDING_REVIEW":
      return tenant ? "Waiting for your landlord" : "Waiting for you";
    case "APPROVED":
      return report.admin_reason ? "Approved by an admin" : "Approved";
    case "REJECTED":
      return "Rejected by an admin";
    case "DISPUTED":
      return report.escalated_at ? "With an admin" : "Rejected";
    case "CANCELLED":
      return tenant ? "Withdrawn" : "Withdrawn by the tenant";
    case "EXPIRED":
      return tenant ? "Expired — send a new report" : "Expired";
  }
};
