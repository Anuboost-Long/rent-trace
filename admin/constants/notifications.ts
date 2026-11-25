import type { NotificationKind } from "@/types/notifications/models";

import type { Audience } from "./audience";
import { Route } from "./web-routes";

export const NotificationsRoute: Record<Audience, string> = {
  tenant: Route.tenant.notifications,
  landlord: Route.landlord.notifications,
  admin: Route.admin.notifications,
};

type Destination = (subjectId: number | null) => string | null;

const DESTINATIONS: Partial<
  Record<NotificationKind, Partial<Record<Audience, Destination>>>
> = {
  CONTACT_REQUEST_RECEIVED: { landlord: () => Route.landlord.requests },
  CONTACT_REQUEST_CANCELLED: { landlord: () => Route.landlord.requests },
  CONTACT_REQUEST_ACCEPTED: { tenant: () => Route.tenant.requests },
  CONTACT_REQUEST_DECLINED: { tenant: () => Route.tenant.requests },
  CONTACT_REQUEST_REVOKED: { tenant: () => Route.tenant.requests },
  TENANCY_INVITATION_RECEIVED: { tenant: () => Route.tenant.tenancies },
  TENANCY_STARTED: { tenant: (id) => (id ? Route.tenant.tenancy(id) : null) },
  TENANCY_ENDED: { tenant: (id) => (id ? Route.tenant.tenancy(id) : null) },
  TENANCY_CANCELLED: { tenant: (id) => (id ? Route.tenant.tenancy(id) : null) },
  MAINTENANCE_REPORTED: {
    landlord: (id) => (id ? Route.landlord.issue(id) : null),
  },
  MAINTENANCE_ACKNOWLEDGED: {
    tenant: (id) => (id ? Route.tenant.issue(id) : null),
  },
  MAINTENANCE_STARTED: { tenant: (id) => (id ? Route.tenant.issue(id) : null) },
  MAINTENANCE_CLOSURE_PROPOSED: {
    tenant: (id) => (id ? Route.tenant.issue(id) : null),
    landlord: (id) => (id ? Route.landlord.issue(id) : null),
  },
  MAINTENANCE_CLOSURE_REJECTED: {
    tenant: (id) => (id ? Route.tenant.issue(id) : null),
    landlord: (id) => (id ? Route.landlord.issue(id) : null),
  },
  MAINTENANCE_PROVIDER_ASSIGNED: {
    tenant: (id) => (id ? Route.tenant.issue(id) : null),
  },
  MAINTENANCE_CLOSED: {
    tenant: (id) => (id ? Route.tenant.issue(id) : null),
    landlord: (id) => (id ? Route.landlord.issue(id) : null),
  },
  TENANCY_TERMS_PROPOSED: {
    tenant: (id) => (id ? Route.tenant.tenancy(id) : null),
  },
  TENANCY_TERMS_APPLIED: {
    landlord: (id) => (id ? Route.landlord.tenancy(id) : null),
    admin: (id) => (id ? Route.admin.tenancy(id) : null),
  },
  TENANCY_TERMS_DECLINED: {
    landlord: (id) => (id ? Route.landlord.tenancy(id) : null),
    admin: (id) => (id ? Route.admin.tenancy(id) : null),
  },
  TENANCY_TERMS_CHANGED: {
    tenant: (id) => (id ? Route.tenant.tenancy(id) : null),
  },
  TENANCY_HOUSEMATE_REQUESTED: {
    landlord: (id) => (id ? Route.landlord.tenancy(id) : null),
    admin: (id) => (id ? Route.admin.tenancy(id) : null),
  },
  TENANCY_HOUSEMATE_APPROVED: { tenant: () => Route.tenant.tenancies },
  TENANCY_HOUSEMATE_DECLINED: { tenant: () => Route.tenant.tenancies },
  CONDITION_EVIDENCE_SUBMITTED: {
    landlord: (id) => (id ? Route.landlord.tenancy(id) : null),
  },
  CONDITION_EVIDENCE_APPROVED: {
    tenant: (id) => (id ? Route.tenant.tenancy(id) : null),
  },
  CONDITION_EVIDENCE_REJECTED: {
    tenant: (id) => (id ? Route.tenant.tenancy(id) : null),
  },
  TENANCY_INVITATION_ACCEPTED: {
    landlord: (id) => (id ? Route.landlord.tenancy(id) : null),
    admin: (id) => (id ? Route.admin.tenancy(id) : null),
  },
};

export const notificationHref = (
  kind: NotificationKind,
  subjectId: number | null,
  audience: Audience,
) => DESTINATIONS[kind]?.[audience]?.(subjectId) ?? null;
