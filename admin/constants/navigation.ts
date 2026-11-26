import { Route } from "@/constants/web-routes";
import {
  Ban,
  Bell,
  Building2,
  FileText,
  HardHat,
  KeyRound,
  LayoutDashboard,
  LayoutGrid,
  MessageSquare,
  MonitorSmartphone,
  Scale,
  Users,
  Wrench,
  type LucideIcon,
} from "lucide-react";

import type { Audience } from "./audience";

export const SIDEBAR_COOKIE = "sidebar_collapsed";

// Admin screens that are not in the Figma design sit in this group, below the main items.
const OPERATIONS = "Operations";

export type { Audience } from "./audience";

export type NavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  exact?: boolean;
  permission?: string;
  group?: string;
  description?: string;
};

type Navigation = {
  label: string;
  items: NavItem[];
};

export const Navigation: Record<Audience, Navigation> = {
  admin: {
    label: "Admin",
    items: [
      {
        label: "Overview",
        href: Route.admin.index,
        icon: LayoutGrid,
        exact: true,
      },
      {
        label: "Accounts",
        href: Route.admin.users,
        icon: Users,
        permission: "accounts.view",
        description: "Accounts, roles and status",
      },
      {
        label: "Team and permissions",
        href: Route.admin.access,
        icon: KeyRound,
        permission: "access.manage",
        description: "Admins, roles, permissions and grants",
      },
      {
        label: "Properties",
        href: Route.admin.properties,
        icon: Building2,
        permission: "properties.admin_view",
        group: OPERATIONS,
        description: "Set up properties for landlords",
      },
      {
        label: "Tenancies",
        href: Route.admin.tenancies,
        icon: FileText,
        permission: "tenancies.admin_view",
        group: OPERATIONS,
        description: "Tenancies and tenant invitations",
      },
      {
        label: "Contact requests",
        href: Route.admin.contact_requests,
        icon: MessageSquare,
        permission: "contact_requests.admin_view",
        group: OPERATIONS,
        description: "Tenants asking landlords for contact",
      },
      {
        label: "Tradespeople",
        href: Route.admin.providers,
        icon: HardHat,
        permission: "providers.admin_view",
        group: OPERATIONS,
        description: "Plumbers, electricians and others landlords use",
      },
      {
        label: "Maintenance",
        href: Route.admin.maintenance,
        icon: Wrench,
        permission: "maintenance.admin_view",
        group: OPERATIONS,
        description: "Issues reported on any property",
      },
      {
        label: "Review cases",
        href: Route.admin.review_cases,
        icon: Scale,
        permission: "reviews.admin_review",
        group: OPERATIONS,
        description: "Reports an admin has been asked to decide",
      },
      {
        label: "Bans",
        href: Route.admin.bans,
        icon: Ban,
        permission: "bans.view",
        group: OPERATIONS,
        description: "Blocked emails, domains and accounts",
      },
      {
        label: "Access tokens",
        href: Route.admin.tokens,
        icon: MonitorSmartphone,
        permission: "tokens.view",
        group: OPERATIONS,
        description: "Signed-in sessions",
      },
      {
        label: "Notifications",
        href: Route.admin.notifications,
        icon: Bell,
        group: OPERATIONS,
        description: "Updates sent to you",
      },
    ],
  },
  landlord: {
    label: "Landlord",
    items: [
      {
        label: "Overview",
        href: Route.landlord.index,
        icon: LayoutDashboard,
        exact: true,
      },
      { label: "Properties", href: Route.landlord.properties, icon: Building2 },
      { label: "Tenancies", href: Route.landlord.tenancies, icon: FileText },
      {
        label: "Contact requests",
        href: Route.landlord.requests,
        icon: MessageSquare,
      },
      { label: "Maintenance", href: Route.landlord.maintenance, icon: Wrench },
      {
        label: "Tradespeople",
        href: Route.landlord.providers,
        icon: HardHat,
        permission: "providers.view",
      },
    ],
  },
  tenant: {
    label: "Tenant",
    items: [
      {
        label: "Overview",
        href: Route.tenant.index,
        icon: LayoutDashboard,
        exact: true,
      },
      { label: "Tenancies", href: Route.tenant.tenancies, icon: FileText },
      {
        label: "Contact requests",
        href: Route.tenant.requests,
        icon: MessageSquare,
      },
      { label: "Maintenance", href: Route.tenant.maintenance, icon: Wrench },
    ],
  },
};

export const groupNavItems = (items: NavItem[]) =>
  Object.entries(Object.groupBy(items, (item) => item.group ?? "")) as [
    string,
    NavItem[],
  ][];

export { audienceFor, isMemberOf } from "./audience";
