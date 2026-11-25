# Admin users

## Status — 25 November 2026 (Accounts, Figma look)

The Users screens became **Accounts**, laid out as in Figma (see
[Admin design alignment](admin-design-alignment.md)). Type-checked and linted; **not seen in a
browser yet.** The URLs are unchanged (`/admin/users`).

- **List:** chips across the top: All, Tenants, Landlords, Admins and Suspended, each showing its
  count. Admins means the `ADMIN` role only, not custom admin roles. Next to them are a search box
  ("Search name or email"; searching keeps the chip that is selected) and "Add account". The
  columns are Name with the email under it, Role, a Status badge (Active green, Suspended amber)
  and Last active (the last log in, or "Never"). Clicking a row opens the account. The old Role
  and Status drop-downs and the row action icons are gone.
- **Detail:** a status badge, the name, and a line with email · role · sign-in method · joined
  date. Below that:
  - a **Details** card: phone, two-step sign-in, email verified and last log in
  - a **Tenancies** card for tenants, if you can view tenancies: tenancy search by their email,
    linking to each tenancy
  - the Permissions section
- **Account actions** card on the right:
  - **Suspend account** or **Reactivate account**, which now ask for a reason (sent as `reason`)
  - **Ban account** (red), new here: creates an `ACCOUNT` ban through `POST /api/bans/` with the
    reason. Shown with `bans.manage`, never on yourself or a super admin.
  - **Delete account**, **Edit details** and **Reset authenticator**, with the same permission
    rules as before

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
