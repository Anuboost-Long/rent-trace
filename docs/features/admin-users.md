# Admin users

## Status — 18 November 2026 (reset authenticator)

Built. Seen in a browser on 19 November 2026 as a super admin: the button, the confirm dialog,
a real reset (the person's page then read "Not set up"), and the resend button. **Not seen:** the
reset email actually arriving (the Gmail sending token had expired, so every send failed), and the
person being asked to enrol again at their next sign-in. 158 back-end tests pass in users and
accounts; ruff, the migration check, admin typecheck, lint and Prettier pass.

### Resetting someone's authenticator

For an admin who has lost their phone and backup codes, so they cannot get past two-step
verification or reset their password (which also needs a code).

- **Who:** a super admin only, and not on their own account. The usual rule applies: you can't act
  on someone who holds permissions you don't.
- `POST /api/users/<id>/reset-authenticator/` with a required `reason`. It deletes the person's
  authenticator and unused backup codes, ends all their sessions, and writes an
  `ADMIN_RESET_AUTHENTICATOR` entry in the account history (reason, who, nothing secret). The
  person gets an email saying it happened. A person with no authenticator set up gets a 400.
- The response carries `notice_sent`. When the email could not be sent the reset still stands and
  `notice_sent` is false; the admin page says so.
- `POST /api/users/<id>/resend-authenticator-notice/` (super admin) sends the same email again and
  answers `{"notice_sent": true|false}`. It answers 400 unless the person's authenticator was
  reset by an admin and they have not set up a new one yet. The user detail carries
  `authenticator_was_reset` for exactly that state.
- Next sign-in the person is asked to set up a new authenticator, as on first sign-in.
- The user's page shows a "Two-step verification" row (set up or not), and a **Reset
  authenticator** button for a super admin when it is set up. The button asks for the reason. After
  a reset a **Resend reset email** button shows until the person sets up a new authenticator, with a
  line saying whether the email went.
- **Verify who is asking first.** After a reset, someone who knows the password can sign in and
  set up their own authenticator, so a super admin should confirm the person's identity outside
  the app before resetting.
- Acceptance: a super admin resets an enrolled admin and the person must enrol again; a normal
  admin, landlord or tenant is refused; resetting yourself or someone with no authenticator is
  refused; the history entry exists and holds no secret; the sessions are ended and an email goes
  out.

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

- Reset authenticator: `back-end/users/services/reset_authenticator.py`, `ResetAuthenticatorView` in
  `users/views.py`, `accounts/security/super_admin_permission.py`, `users/services/resend_authenticator_notice.py`; the buttons are
  `admin/app/(app)/admin/users/[id]/reset-authenticator-button.tsx`.
- `back-end/users/`: `/api/users/`.
- `admin/app/(app)/admin/users/`: `page.tsx`, `[id]/`, `new/`, `role-picker.tsx`,
  `user-actions.tsx`, `users-filter.tsx`.
- `admin/hooks/form/useCreateUser.ts`, `useUpdateUser.ts`, `useUserActions.ts`.
- `admin/api/services/users/serve-action.ts`, `admin/types/users/models.ts`.
