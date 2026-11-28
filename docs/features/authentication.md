# Authentication and sessions

## Status — 25 November 2026 (Figma look for log in and MFA)

The sign-in, MFA and other auth cards were restyled to the Figma screens (see
[Admin design alignment](admin-design-alignment.md)). Type-checked and linted; **not seen in a
browser yet.** What changed for the person signing in:

- The page says **Log in** (was "Sign in"). If the URL has `?reason=session_ended`, a "Your session
  ended" notice shows above the form. The proxy (`admin/proxy.ts`) adds that reason when the API
  refuses to refresh a session the person had, but not when the API can't be reached. A 401 from a
  server action that redirects to log in adds it too.
- **Setting up MFA** starts straight away and shows numbered steps: scan the QR code (or type the
  key, shown in groups of four), then enter the 6-digit code in six boxes.
- **Entering a code** uses the same six boxes, with "Use a backup code" to switch to a plain text
  field and "Back to log in" to sign out.
- **Backup codes** show under a warning that this is the only time they appear and each works once, in one
  grouped two-column block, with Copy (changes to "Copied"), Download (a `.txt` file) and Continue. Copy and
  Download raise an alert. Updated 28 November 2026; typecheck, lint and build pass, **not yet seen in a
  browser** (`admin/components/auth/backup-codes.tsx`).

## Status — 18 November 2026 (forgot and reset password)

Built. 8 new back-end tests pass (and all 81 in accounts); ruff, the migration check and the
OpenAPI validation pass; admin typecheck and lint pass. Walked through in Chrome as the test
landlord using a link issued from the shell (so no real email was sent): a bad link shows "Link
expired"; a weak password shows an error and keeps the link usable; a valid password changes it;
the same link is then refused; the new password signs in; the sign-in page shows "Forgot
password?". **Not seen in a browser:** the authenticator code field and a wrong-code run (no admin
account with an authenticator was available; covered by back-end tests), submitting the forgot
form and the real reset email.

### Changing the password from the profile

- Landlords and tenants: the current password, as before.
- Admins with an authenticator set up (anyone with two-step verification on, shown by
  `mfa_status` `VERIFIED`): the profile form also asks for a code from the app or a backup code.
  A missing or wrong code is refused and nothing changes; a refused change sends no email and
  leaves the code usable. The endpoint is limited to 5 attempts a minute (the `mfa` rate).
- **Everyone** gets an email saying the password was changed, after both a change and a reset,
  with a link to reset it again if it was not them.
- Built; 7 new back-end tests pass and all 89 in accounts; the full suite (713 tests) passed
  before this change. The profile page renders for a landlord with no code field. **Not seen in
  a browser:** the code field for an admin, and a real change (it would email the account).

### Forgot and reset password

- **Everyone:** on the sign-in page, "Forgot password?" takes an email and always answers "If an
  account exists, we've sent a reset link" (same as before). The emailed link opens
  `/reset-password?token=…` on the web app, where the person chooses a new password. Landlords
  and tenants need only that email link. Google-only accounts get the existing "your account
  uses Google" email instead.
- **Admins with an authenticator app set up** also have to enter a code from the app (or one of
  their backup codes) on the reset page. A wrong code **uses up the link**, so a stolen link
  can't be used to guess codes: the person asks for a new link. A missing code does not.
- The reset page first asks the back end whether a code is needed (`GET
/api/auth/reset-password/?token=…`, which does not use the link up), so it only shows the code
  field when it must, and shows "link expired" straight away for a bad link.
- A reset signs the person out of their other devices by default (tick box on the page), as
  before, and clears the sign-in lock.
- The reset email now links to the web app (`WEB_APP_URL`), like the verify-email link. The old
  `AUTH_LINK_BASE_URL` setting (which pointed at a page that does not exist) is removed.
- **Not covered:** an admin who has lost their authenticator and backup codes cannot reset by
  themselves. A super admin resetting someone's authenticator is still not built
  (`back-end/docs/authentication.md`, open items). Super admins are exempt from the sign-in
  check unless they have set up an authenticator, in which case they are asked for the code too.
- Acceptance: a tenant resets with the email link alone; an admin with an authenticator cannot
  reset without a valid code; a wrong code burns the link; a bad or used link is refused on the
  preview; after a reset the old password fails and the new one signs in.

## Status — 12 November 2026

Shipped (back end 29 October and 11 November 2026, admin screens 11 November).
Back-end rules are written in full in `back-end/docs/authentication.md`; this
document is the feature-level summary. Not re-verified when this was written.

## Goal

People sign up and sign in with Google or an email and password, stay signed in
safely across devices, and admins get an extra two-step check.

## How it works

- **Two sign-in methods, one per account.** `GOOGLE` (identity checked by Google
  through Supabase; no Google tokens stored) or `EMAIL_PASSWORD` (hash stored in
  our database). The method never changes after sign-up.
- **Our own sessions for both.** After either sign-in the person gets our access
  and refresh tokens. Each refresh token works once. Sessions record device, IP
  and last use.
- **Email/password:** sign-up sends a verification link; verify, resend,
  forgot-password and reset-password flows; failed attempts are throttled per
  email; the API never reveals whether an email exists.
- **Google:** the admin app signs in with Supabase, then exchanges the Supabase
  access token for ours (`POST /api/auth/google/`). 503 when Supabase isn't set up.
- **Admin two-step verification (MFA):** authenticator-app enrolment, confirm
  with a first code (backup codes shown once), then verify each session. A super
  admin skips it. Secrets are encrypted with `MFA_ENCRYPTION_KEY`.
- **First admin:** `POST bootstrap-admin/` with `ADMIN_BOOTSTRAP_SECRET`, once.
- **API key:** every `/api/` request needs `X-API-Key`; the docs pages are exempt.
- **Sign out, change password** (optionally signing out other devices), and
  `GET me/` returning roles, join date, last sign-in and effective permissions.
  In the sidebar shell, **Log out** opens a confirm dialog before the session is
  cleared.
- **Changing email is not allowed** yet.

Admin app screens: sign-in, sign-up with a check-your-email step, email
verification (`/verify-email`), MFA (`/auth/mfa`), Google callback. Session
cookies and the signed-in user are handled in `admin/api/services/auth/`.
`admin/proxy.ts` guards routes.

## Source locations

- Forgot and reset: `back-end/accounts/services/reset_password.py`, `preview_password_reset.py`,
  `shared/links.py` (`usable_link`); `admin/app/auth/forgot-password/`, `admin/app/reset-password/`,
  `admin/hooks/form/usePasswordReset.ts`.
- `back-end/accounts/`: `views.py`, `services/`, `security/` (token check, JWT,
  rate limits), `integrations/` (email, Supabase), `models/`.
- `back-end/docs/authentication.md`: the full rules.
- `admin/app/auth/` (`sign-in`, `sign-up`, `mfa`, `google/callback`),
  `admin/app/verify-email/`.
- `admin/api/services/auth/`: `serve-action.ts`, `session-cookies.ts`, `jotai.ts`.
- `admin/hooks/form/useAuth.ts`, `useMfa.ts`.
- `admin/proxy.ts`, `admin/utils/supabase-client.ts`.
- `admin/components/common/google-sign-in.tsx`, `auth-card.tsx`.

## Not done

- Changing email (needs an `EMAIL_CHANGE` token purpose and a notice to the old
  address).
