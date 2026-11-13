# Access control: permissions, roles and grants

## Status — 12 November 2026

Shipped 11 November 2026. Not re-verified when this was written. A person can
hold several admin roles, roles can inherit, and the rule below applies to every
write.

## Goal

Super admins and delegated admins decide who can do what, without code changes.

## How it works

- **The rule:** you can't give or act on what you don't hold. The super admin
  (`is_top_level_admin`) passes it.
- **Permissions** (`module.action`, lower case): add, rename, change
  `is_admin_only`, deactivate. Codes can't change or be deleted. `accounts` and
  `access` codes are always admin-only. A permission can't become admin-only while
  a tenant or landlord role or person holds it. See who holds one, through which
  roles, and by individual grant.
- **Roles:** built-in (`TENANT`, `LANDLORD`, `ADMIN`) and custom admin roles with
  a name, description, parent and permissions. Permissions inherit from the
  parent. Built-ins can't be deactivated or given a parent. Cycles and chains
  over 5 levels are refused.
- **Members:** add or remove people from an admin role. An admin always keeps at
  least one admin role.
- **Individual grants:** grant a permission to one person with a required reason;
  revoke it (switched off, not deleted); re-granting reactivates it.
- **History:** role changes go to `role_change_history`; grant changes to
  `account_access_history`.
- Everything needs `access.manage`.

Admin screens (`/admin/access`, tabs for permissions, roles and grants):
permission list, create and edit; role list, create and edit with members; grant
list, create, and revoke.

## Source locations

- `back-end/access/`: `/api/access/`.
- `admin/app/(app)/admin/access/`: `permissions/`, `roles/`, `grants/`,
  `role-editor.tsx`, `revoke-grant-button.tsx`.
- `admin/hooks/form/useGrantForm.ts`, `useGrants.ts`, `usePermissionForm.ts`,
  `useRoleEditor.ts`, `useRoleMembers.ts`.
- `admin/api/services/access/serve-action.ts`, `admin/types/access/models.ts`,
  `admin/utils/user-permissions.ts`.
