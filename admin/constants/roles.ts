import type { RoleItem } from "@/types/access/models";

export const StatusLabel: Record<string, string> = {
  ACTIVE: "Active",
  SUSPENDED: "Suspended",
};

export const BUILT_IN_PARTY_ROLES: RoleItem[] = ["TENANT", "LANDLORD"].map(
  (code) => ({
    code,
    name: code === "TENANT" ? "Tenant" : "Landlord",
    description: null,
    kind: "PARTY",
    is_system: true,
    is_active: true,
    parent: null,
    holder_count: 0,
    permissions: [],
    inherited_permissions: [],
  }),
);
