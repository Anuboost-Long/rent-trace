# Access control: permissions, roles and grants

## Status — 25 November 2026 (Team and permissions, Figma look)

The admin screens became **Team and permissions**, as in Figma (see
[Admin design alignment](admin-design-alignment.md)). Type-checked and linted; **not seen in a
browser yet.** No back-end change.

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

Admin screens ("Team and permissions", `/admin/access`), with four tabs:

- **Admins** (`/admin/access`, the default) lists everyone holding an admin-kind role:
  - name and email, with "(you)" on your own row
  - up to six permission chips, then "+ N more"; "All permissions" for a super admin
  - MFA: On, or "Setup pending" if no authenticator is set up
  - last log in

  It loads each admin's detail and permissions one by one, which is fine for a small team.
  Clicking a row opens **Edit permissions** (`/admin/access/admins/<id>`):
  - a switch for each active admin-only permission
  - a permission that comes from a role is on and locked
  - a required reason
  - saving sends one grant or revoke per changed permission, each with that reason (revokes now
    pass the reason too)
  - read-only on your own account and on a super admin
- **Roles** (`/admin/access/roles`, moved from `/admin/access`): role list, create and edit with
  members.
- **Permissions:** permission list, create and edit.
- **Grants:** grant list, create and revoke.

## Source locations

- `back-end/access/`: `/api/access/`.
- `admin/app/(app)/admin/access/`: `page.tsx` and `admin-team.ts` (Admins tab), `admins/[id]/`
  (Edit permissions), `permissions/`, `roles/`, `grants/`,
  `role-editor.tsx`, `revoke-grant-button.tsx`.
- `admin/hooks/form/useAdminPermissions.ts`, `useGrantForm.ts`, `useGrants.ts`, `usePermissionForm.ts`,
  `useRoleEditor.ts`, `useRoleMembers.ts`.
- `admin/api/services/access/serve-action.ts`, `admin/types/access/models.ts`,
  `admin/utils/user-permissions.ts`.
