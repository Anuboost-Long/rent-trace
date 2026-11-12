# Admin users

## Status — 12 November 2026

Shipped 11 November 2026. Not re-verified when this was written.

## Goal

Admins find, create, edit, suspend and remove accounts.

## How it works

- **List** (`/admin/users`): paginated, newest first, filter by search (`q`), role
  and status. A plain `GET all/` list (capped at 500) feeds dropdowns.
- **Detail** (`/admin/users/<id>`): the person's details, roles, and what they get
  through roles and individual grants.
- **Create** (`/admin/users/new`): a verified account with a starting password
  the admin chooses; no email is sent.
- **Edit:** first name, last name, phone number and role. Email can't be changed.
- **Deactivate / activate:** suspends an account and signs the person out
  everywhere, or lets them back in. Repeating it changes nothing.
- **Delete:** soft-delete; the email stays reserved and sessions end.
- An optional `reason` on deactivate, activate and delete is saved in history.
- **Rule:** only the super admin may create or edit admin accounts or set `ADMIN`.
  Admins need to have finished two-step verification (the super admin skips it).

## Source locations

- `back-end/users/`: `/api/users/`.
- `admin/app/admin/users/`: `page.tsx`, `[id]/`, `new/`, `role-picker.tsx`,
  `user-actions.tsx`, `users-filter.tsx`.
- `admin/hooks/form/useCreateUser.ts`, `useUpdateUser.ts`, `useUserActions.ts`.
- `admin/api/services/users/serve-action.ts`, `admin/types/users/models.ts`.
