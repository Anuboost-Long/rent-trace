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
  TENANCY_HOUSEMATE_REQUESTED: {
    landlord: (id) => (id ? Route.landlord.tenancy(id) : null),
    admin: (id) => (id ? Route.admin.tenancy(id) : null),
  },
  TENANCY_HOUSEMATE_APPROVED: { tenant: () => Route.tenant.tenancies },
  TENANCY_HOUSEMATE_DECLINED: { tenant: () => Route.tenant.tenancies },
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
