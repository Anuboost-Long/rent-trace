import type { StatusTone } from "@/components/common/status-badge";

// Which badge colour each status shows in lists. Anything not listed is neutral.
export const TenancyStatusTone: Record<string, StatusTone> = {
  PENDING: "warning",
  ACTIVE: "success",
};

export const IssueStatusTone: Record<string, StatusTone> = {
  REPORTED: "attention",
  ACKNOWLEDGED: "warning",
  IN_PROGRESS: "warning",
};

export const PropertyStatusTone: Record<string, StatusTone> = {
  ACTIVE: "success",
  UNDER_MAINTENANCE: "warning",
};

export const ContactRequestStatusTone: Record<string, StatusTone> = {
  PENDING: "attention",
  ACCEPTED: "success",
  DECLINED: "error",
};

export const RemovalStatusTone: Record<string, StatusTone> = {
  PENDING_REVIEW: "warning",
  APPROVED: "success",
};

export const CorrectionStatusTone = RemovalStatusTone;

export const BanStatusTone: Record<string, StatusTone> = { ACTIVE: "error" };

export const TokenStatusTone: Record<string, StatusTone> = {
  ACTIVE: "success",
};

export const toneFor = (tones: Record<string, StatusTone>, status: string) =>
  tones[status] ?? "neutral";
