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
  REVOKED: "Revoked",
  EXPIRED: "Expired",
};

export const TenancyAccess = {
  admin: {
    create: "tenancies.admin_manage",
    invite: "tenancies.admin_manage",
  },
  landlord: {
    create: "tenancies.create",
    invite: "tenancies.manage_parties",
  },
} as const;

export const TenancyRoutes = {
  admin: {
    list: Route.admin.tenancies,
    create: Route.admin.tenancy_new,
    detail: Route.admin.tenancy,
  },
  landlord: {
    list: Route.landlord.tenancies,
    create: Route.landlord.tenancy_new,
    detail: Route.landlord.tenancy,
  },
} as const;
