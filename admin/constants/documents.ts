import type { StatusTone } from "@/components/common/status-badge";
import type { Confirmation, DocumentType } from "@/types/documents/models";

export const DocumentTypeLabel: Record<DocumentType, string> = {
  TENANCY_AGREEMENT: "Tenancy agreement",
  CONDITION_REPORT: "Condition report",
  NOTICE: "Notice",
  RECEIPT: "Receipt",
  OTHER: "Other paper",
};

export const TenantUploadTypes: DocumentType[] = ["NOTICE", "RECEIPT", "OTHER"];
export const LandlordTypes = Object.keys(DocumentTypeLabel) as DocumentType[];

export const ConfirmationLabel: Record<Confirmation, string> = {
  WAITING: "Waiting for the tenant",
  CONFIRMED: "Confirmed",
  FLAGGED: "Flagged by the tenant",
  EXPIRED: "Expired, no answer in 14 days",
  ESCALATED: "With an admin",
  SUPERSEDED: "Replaced by a newer version",
};

export const ConfirmationTone: Record<Confirmation, StatusTone> = {
  WAITING: "warning",
  CONFIRMED: "success",
  FLAGGED: "error",
  EXPIRED: "neutral",
  ESCALATED: "attention",
  SUPERSEDED: "neutral",
};

export const ACCEPTED_FILES =
  ".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png";

export const fileSize = (bytes: number) =>
  bytes < 1_000_000
    ? `${Math.max(1, Math.round(bytes / 1000))} KB`
    : `${(bytes / 1_000_000).toFixed(1)} MB`;
