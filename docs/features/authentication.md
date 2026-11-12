# Authentication and sessions

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
- **Changing email is not allowed** yet.

Admin app screens: sign-in, sign-up with a check-your-email step, email
verification (`/verify-email`), MFA (`/auth/mfa`), Google callback. Session
cookies and the signed-in user are handled in `admin/api/services/auth/`.
`admin/proxy.ts` guards routes.

## Source locations

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
