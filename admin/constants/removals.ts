import type { RemovalStatus } from "@/types/removals/models";

export const RemovalStatusLabel: Record<RemovalStatus, string> = {
  PENDING_REVIEW: "Pending review",
  APPROVED: "Approved · hidden",
  REJECTED: "Rejected",
};

export const RemovalFilters: { label: string; status?: RemovalStatus }[] = [
  { label: "Pending" },
  { label: "Approved", status: "APPROVED" },
  { label: "Rejected", status: "REJECTED" },
];

export const SideLabel = { TENANT: "tenant", LANDLORD: "landlord" } as const;
