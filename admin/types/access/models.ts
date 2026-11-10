export type PermissionItem = {
  code: string;
  name: string;
  module: string;
  is_admin_only: boolean;
  is_active: boolean;
  roles: string[];
};

export type RoleItem = {
  code: string;
  name: string;
  description: string | null;
  kind: "PARTY" | "ADMIN";
  is_system: boolean;
  is_active: boolean;
  parent: string | null;
  holder_count: number;
  permissions: string[];
  inherited_permissions: string[];
};

export type RoleBody = {
  name?: string;
  description?: string;
  parent?: string | null;
  permissions?: string[];
  is_active?: boolean;
};

export type Grant = {
  code: string;
  name: string;
  module: string;
  reason: string;
  is_active: boolean;
  created_at: string;
};

export type UserPermissions = {
  roles: string[];
  through_roles: { code: string; name: string; module: string }[];
  grants: Grant[];
  effective: string[];
};

export type UserBrief = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
};

export type PermissionBody = Partial<{
  name: string;
  is_admin_only: boolean;
  is_active: boolean;
}>;

export type HolderGrant = {
  user: UserBrief;
  reason: string;
  created_at: string;
  granted_by: UserBrief | null;
};

export type PermissionHolders = {
  permission: PermissionItem;
  roles: { code: string; name: string; inherited: boolean }[];
  people_through_roles: number;
  grants: HolderGrant[];
};

export type GrantListItem = HolderGrant & {
  permission_code: string;
  permission_name: string;
};

export type Page<T> = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: T[];
};

export type RoleMember = UserBrief & { role_names: string[] };
