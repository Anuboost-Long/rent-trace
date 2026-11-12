import { Route } from "./web-routes";

export const IssueStatusLabel: Record<string, string> = {
  REPORTED: "Reported",
  ACKNOWLEDGED: "Acknowledged",
  IN_PROGRESS: "In progress",
  CLOSED: "Closed",
};

export const IssuePriorityLabel: Record<string, string> = {
  LOW: "Low",
  MEDIUM: "Medium",
  HIGH: "High",
  URGENT: "Urgent",
};

export const ClosureOutcomeLabel: Record<string, string> = {
  FIXED: "Fixed",
  NOT_FIXED_NO_ACTION: "Not fixed, no action will be taken",
};

export const IssueRoutes = {
  tenant: { list: Route.tenant.maintenance, detail: Route.tenant.issue },
  landlord: { list: Route.landlord.maintenance, detail: Route.landlord.issue },
} as const;
