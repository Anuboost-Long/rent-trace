import { Route } from "./web-routes";

export const TenancyStatusLabel: Record<string, string> = {
  DRAFT: "Draft",
  PENDING: "Pending",
  ACTIVE: "Active",
  ENDED: "Ended",
  CANCELLED: "Cancelled",
};

export const InvitationStatusLabel: Record<string, string> = {
  PENDING: "Pending",
  ACCEPTED: "Accepted",
  DECLINED: "Declined",
  REVOKED: "Revoked",
  EXPIRED: "Expired",
};

export const TenancyAccess = {
  admin: {
    create: "tenancies.admin_manage",
    invite: "tenancies.admin_manage",
    update: "tenancies.admin_manage",
  },
  landlord: {
    create: "tenancies.create",
    invite: "tenancies.manage_parties",
    update: "tenancies.update",
  },
} as const;

export const TenancyRoutes = {
  admin: {
    list: Route.admin.tenancies,
    create: Route.admin.tenancy_new,
    detail: Route.admin.tenancy,
    edit: Route.admin.tenancy_edit,
  },
  landlord: {
    list: Route.landlord.tenancies,
    create: Route.landlord.tenancy_new,
    detail: Route.landlord.tenancy,
    edit: Route.landlord.tenancy_edit,
  },
} as const;

export const TenantTenancyStatusLabel: Record<string, string> = {
  DRAFT: "Being set up",
  PENDING: "Starting soon",
  ACTIVE: "Current",
  ENDED: "Ended",
  CANCELLED: "Cancelled",
};

export const waitingText = (waitingOn: string[]) => {
  if (waitingOn.includes("LANDLORD") && waitingOn.includes("INVITEE")) {
    return "Waiting for the landlord and for them to accept";
  }
  if (waitingOn.includes("LANDLORD")) return "Waiting for the landlord";
  return "Waiting for them to accept";
};

export const TermChangeStatusLabel: Record<string, string> = {
  PENDING: "Waiting for approval",
  EXPIRED: "Expired",
  APPLIED: "Applied",
  DECLINED: "Declined",
  WITHDRAWN: "Withdrawn",
  SUPERSEDED: "Replaced",
  CLOSED: "Closed with the tenancy",
};
