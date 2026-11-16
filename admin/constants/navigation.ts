import { Route } from "@/constants/web-routes";
import {
  Ban,
  Building2,
  KeyRound,
  ShieldCheck,
  FileText,
  LayoutDashboard,
  MessageSquare,
  Users,
  Wrench,
  HardHat,
  type LucideIcon,
} from "lucide-react";

import type { Audience } from "./audience";

export const SIDEBAR_COOKIE = "sidebar_collapsed";

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
        icon: LayoutDashboard,
        exact: true,
      },
      {
        label: "Users",
        href: Route.admin.users,
        icon: Users,
        permission: "accounts.view",
        group: "People & access",
        description: "Accounts, roles and status",
      },
      {
        label: "Access",
        href: Route.admin.access,
        icon: ShieldCheck,
        permission: "access.manage",
        group: "People & access",
        description: "Roles, permissions and grants",
      },
      {
        label: "Properties",
        href: Route.admin.properties,
        icon: Building2,
        permission: "properties.admin_view",
        group: "Rentals",
        description: "Set up properties for landlords",
      },
      {
        label: "Tenancies",
        href: Route.admin.tenancies,
        icon: FileText,
        permission: "tenancies.admin_view",
        group: "Rentals",
        description: "Tenancies and tenant invitations",
      },
      {
        label: "Contact requests",
        href: Route.admin.contact_requests,
        icon: MessageSquare,
        permission: "contact_requests.admin_view",
        group: "Rentals",
        description: "Tenants asking landlords for contact",
      },
      {
        label: "Maintenance",
        href: Route.admin.maintenance,
        icon: Wrench,
        permission: "maintenance.admin_view",
        group: "Rentals",
        description: "Issues reported on any property",
      },
      {
        label: "Bans",
        href: Route.admin.bans,
        icon: Ban,
        permission: "bans.view",
        group: "Security",
        description: "Blocked emails, domains and accounts",
      },
      {
        label: "Access tokens",
        href: Route.admin.tokens,
        icon: KeyRound,
        permission: "tokens.view",
        group: "Security",
        description: "Signed-in sessions",
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
