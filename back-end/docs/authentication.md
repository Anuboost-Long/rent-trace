# Authentication and accounts

Decisions made after spec v3 (`RentTrace_Database_Structure_and_Processes_v3.md`). Where this document and spec §3 disagree, this document is the current rule. Models live in `accounts/models/` (`users.py`, `sessions.py`, `access.py`).

## 1. Sign-in methods

Each account has exactly one method, stored in `users.auth_method` and never changed after registration.

| Method           | Who checks the identity  | What we store                                                          |
| ---------------- | ------------------------ | ---------------------------------------------------------------------- |
| `GOOGLE`         | Google, through Supabase | `users.auth_subject` = Supabase user id. No Google or Supabase tokens. |
| `EMAIL_PASSWORD` | Our backend              | Password hash in `user_credentials`. `auth_subject` is empty.          |

The database enforces this: `auth_subject` is required for `GOOGLE` and forbidden for `EMAIL_PASSWORD` (`ck_users_auth_subject`). Supabase's own email/password provider must be turned off, so no email/password account can exist in Supabase.

After either sign-in, both methods use **our own session and tokens** (section 4).

## 2. Identity tables

| Table               | Purpose                                                                                                                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `users`             | Application account. `email_normalized` = `email` trimmed and lowercased (CHECK), unique forever, including deleted accounts. `email_verified_at` is set once the email is verified.                          |
| `user_credentials`  | One row per email/password user: `password_hash`, `password_changed_at`. Kept apart from `users` so loading a user never loads the hash.                                                                      |
| `auth_tokens`       | Email verification and password reset links. Stores only `sha256(token)`, with `expires_at` and `used_at`.                                                                                                    |
| `auth_sessions`     | One row per signed-in session, for both methods. `session_id`, `verified_method`, `mfa_verified_at`, `expires_at`, `revoked_at`, plus device info: `last_used_at`, `device_name`, `user_agent`, `ip_address`. |
| `user_mfa`          | Authenticator-app MFA (section 9): encrypted secret, `confirmed_at`, `last_used_step`. One per user.                                                                                                          |
| `mfa_backup_codes`  | One-time backup codes, hashed with `make_password`, with `used_at`.                                                                                                                                           |
| `refresh_tokens`    | Our refresh tokens, as `sha256(token)` only. One unused token per session; used rows are kept.                                                                                                                |
| `sign_in_throttles` | Failed password attempts per email (section 6).                                                                                                                                                               |
| `ban_list`          | Banned identities and accounts (section 7).                                                                                                                                                                   |

## 3. Google sign-in

### Flow

```
Mobile app  ──(1) sign in with Google──────▶ Google
Google      ──(2) Google ID token──────────▶ Supabase      (Supabase verifies it)
Supabase    ──(3) Supabase session─────────▶ Mobile app
Mobile app  ──(4) Supabase access token────▶ Our backend   POST /auth/google
Our backend ──(5) verify, then issue OUR session + tokens ─▶ Mobile app
```

Google never talks to our backend. The only token our backend sees is the **Supabase access token** (a JWT signed by our Supabase project), and it is used once, in step 4. It is never stored.

### Which tokens exist

| Token                                          | Made by     | Used by us?                           |
| ---------------------------------------------- | ----------- | ------------------------------------- |
| Google ID token                                | Google      | No. Supabase checks it in step 2.     |
| Google access/refresh token (`provider_token`) | Google      | No. Only needed to call Google APIs.  |
| **Supabase access token**                      | Supabase    | **Yes, once, at step 4.**             |
| Supabase refresh token                         | Supabase    | No.                                   |
| Our access JWT + refresh token                 | Our backend | Yes, for every request after sign-in. |

### Verifying the Supabase token (step 5)

Do either of these:

- **Check it locally:**
  - Signature against the project's public keys at `https://<project>.supabase.co/auth/v1/.well-known/jwks.json`, or the project JWT secret on projects using the shared-secret setup.
  - `iss` = `https://<project>.supabase.co/auth/v1`, `aud` = `authenticated`, and `exp` not passed.
- **Ask Supabase:** call `GET /auth/v1/user` with the token. That's one network call per sign-in and needs no key handling.

Then read the claims:

- `sub` is the Supabase user id.
- `email` is the verified email.
- `app_metadata.provider` must be `"google"`.

`.env` needs `SUPABASE_URL`, plus the JWKS URL or the JWT secret, depending on the project's signing setup.

### First sign-in compared with later ones

**First sign-in** (no user with this `auth_subject`):

1. Check `ban_list` for the email, its domain and the phone.
2. If `email_normalized` already belongs to an `EMAIL_PASSWORD` account, don't sign in. The screen shows a generic "We couldn't sign you in with Google", and the account owner gets an email: "You tried to sign in with Google; your account uses a password". Never create a second account for the same email.
3. Create the user from the token (mapping below), then create the session.
4. Send the user to onboarding (section 5).

**Later sign-ins:** find the user by `auth_subject`, check the account is active, not deleted and has no active ban, then create a session. Don't overwrite names from Google, because the user may have edited them in RentTrace.

### Mapping Google details to `users`

| `users` column            | Source                             | Note                                                                                                                                                |
| ------------------------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `auth_subject`            | `sub`                              | Used to look the user up on later sign-ins.                                                                                                         |
| `email`                   | `email`                            |                                                                                                                                                     |
| `email_normalized`        | `email.strip(" ").lower()`         | Use `strip(" ")`, not `strip()`: SQL `TRIM` removes only spaces, so the CHECK would reject tabs or newlines that Python's `strip()` silently drops. |
| `email_verified_at`       | Sign-in time                       | Google already verified the email.                                                                                                                  |
| `auth_method`             | Fixed                              | `GOOGLE`                                                                                                                                            |
| `first_name`, `last_name` | `user_metadata.full_name` / `name` | Prefill only; the user confirms them in onboarding.                                                                                                 |
| `phone_number`            | Not provided by Google             | Stays empty unless the user adds it.                                                                                                                |

## 4. Sessions and tokens (both methods)

- **Access token:** a short-lived JWT signed with `JWT_SIGNING_KEY`. It isn't stored and carries `session_id`. Each protected request checks:
  - the signature and expiry;
  - that the `auth_sessions` row isn't revoked or expired;
  - that the user is active, not deleted and has no active ban.
- **Refresh token:** a random string; only `sha256(token)` goes in `refresh_tokens`. Each refresh, done under a row lock (`select_for_update`):
  1. Marks the presented token `used_at`.
  2. Issues a new token in the same session.
  3. If an **already used** token is presented, treat it as stolen and set `revoked_at` on the whole session.
- **Revoking sessions:**
  - Sign-out revokes that session.
  - Suspension or an account ban revokes all of the user's sessions.
  - Password change or reset: the user chooses with a "Sign out other devices" checkbox. The session the change is made in stays signed in. The checkbox is ticked by default on a reset (a forgotten password may mean someone else had access) and unticked on a change.

### Token lifetimes and claims

| Item                                        | Tenant / Landlord                 | Admin / super admin                                     |
| ------------------------------------------- | --------------------------------- | ------------------------------------------------------- |
| Access token                                | 15 minutes                        | 15 minutes                                              |
| Refresh token                               | 30 days, replaced on each refresh | Up to the session end                                   |
| Session length (`auth_sessions.expires_at`) | 90 days from sign-in              | **30 minutes from sign-in**; refreshing can't extend it |
| After the session ends                      | Sign in again                     | Sign in again, **including MFA**                        |

- **Claims:** `sub` = user id, `sid` = `session_id`, `iss` = `renttrace-api`, `aud` = `renttrace-mobile` or `renttrace-admin`, plus `iat` and `exp`. Reject a token whose `aud` doesn't match the app calling, so a mobile token can't be used on the admin panel.
- **Signing:** HS256 with `JWT_SIGNING_KEY`. Put a `kid` in the token header; when rotating, keep the previous key valid for 15 minutes (one access-token lifetime).
- **Library:** PyJWT directly. `djangorestframework-simplejwt` brings its own token tables, which would duplicate `auth_sessions` and `refresh_tokens`.

### Where clients keep tokens

- **Mobile (Expo):** `expo-secure-store`, which uses the iOS Keychain and Android Keystore. Never AsyncStorage.
- **Admin panel (Next.js):**
  - Both tokens go in httpOnly, Secure, `SameSite=Strict` cookies, never readable by JavaScript. The refresh cookie is scoped to `/auth/refresh`.
  - Write requests carry a CSRF token.
  - Backend CORS allows only the admin panel's domain.
- **Cleanup:** delete expired `refresh_tokens` and `auth_sessions` rows on a schedule. They are not business records.

### Devices

`auth_sessions` stores what a "Your devices" screen and support need:

- `last_used_at`, `device_name` (for example "iPhone 15 · RentTrace iOS"), `user_agent`, and `ip_address` at sign-in.
- Update `last_used_at` on **refresh**, not on every request, so a busy user doesn't cause a database write per call.
- "Sign out everywhere" sets `revoked_at` on all of the user's open sessions. "Sign out this device" sets it on one.
- `ip_address` is personal data: show it only to the account owner and to Admins handling the account.

## 5. Onboarding after first sign-in

Google can't supply two things, so a short onboarding screen asks for them:

1. **First and last name:** confirm or correct the values prefilled from the full name. Automatic splitting ("Mary Anne Smith") is unreliable, and both fields are required.
2. **Tenant or landlord:** creates the `user_role_bridge` row. Admin can never be chosen at sign-up; Admin access is granted separately.

Email/password users enter names and role in the sign-up form instead.

### Tenant invitations (`tenancy_invitations`)

A landlord can add a tenant who has no account yet:

1. The landlord invites an email to a tenancy (optionally as primary tenant). The row stores `email_normalized`, `sha256(token)` and `expires_at`; the raw token goes in the emailed link.
2. Signing up or signing in from the link: the account's `email_normalized` must **equal** the invited email, so a forwarded link can't be used by someone else.
3. Accepting sets `accepted_at` and `accepted_by`, and creates the `tenancy_parties` row, in one transaction. The landlord can revoke a pending invite (`revoked_at`).
4. On sign-up, look up pending invites by `email_normalized` (indexed) and offer them.

Rules the database enforces:

- one pending invite per tenancy and email;
- accepted and revoked are mutually exclusive;
- `accepted_at` and `accepted_by` are set together.

Inviting creates no relationship: the invitee becomes a tenant only on acceptance, and the usual tenancy rules (exactly one primary tenant) apply then.

## 6. Email/password flows

- **Sign-up:**
  1. Check `ban_list`.
  2. Create the user (`auth_method = EMAIL_PASSWORD`) and a `user_credentials` row with a hash from Django `make_password`.
  3. Email a verification link (an `auth_tokens` row with `EMAIL_VERIFICATION`).
  4. The account can't be used until `email_verified_at` is set.
- **Unverified accounts don't block an email forever.** `email_normalized` is reserved permanently, so someone could sign up with another person's email and never verify it. Rule:
  - Signing up again with an email whose account is **unverified**:
    - within 7 days of the first sign-up, resend the verification email;
    - after 7 days, **reclaim** the account: reuse the same `users` row, replace the names, the `user_credentials` hash and the role, invalidate old `auth_tokens`, and send a new verification link. Record the reclaim in `account_access_history`.
  - An unverified account can't have business data (it can't use the app), so reclaiming the row loses nothing.
  - Once `email_verified_at` is set, the email is reserved forever.
  - Google accounts are always verified (CHECK `ck_users_google_verified`).
  - The reply is the same in every case ("Check your email to finish signing up"), so it doesn't reveal whether the email is taken.
- **Verification and reset:** look the token up by `sha256(raw)`, and check it isn't expired or used. In one transaction, set `used_at` and apply the effect: verify the email, or replace the hash and set `password_changed_at`. When a new reset link is issued, invalidate the user's older unused ones.
- **Wrong method:** a password sign-in for a `GOOGLE` account finds no credential row. The screen shows the normal "Email or password is incorrect" message, and the account owner gets an email: "You tried to sign in with a password; your account uses Google". Never create a second account.
- **Hashing:** Django `make_password` / `check_password` work without `django.contrib.auth` installed. Consider `argon2-cffi` with the Argon2 hasher first in `PASSWORD_HASHERS`. When switching hashers, pass a setter to `check_password` so older hashes upgrade the next time the user signs in.

### Password rules

Following current NIST guidance:

- **Length:** 10 to 128 characters.
- **No character rules:** no forced symbols or digits, and no forced periodic changes.
- **Rejected** by Django's password validators (configured in `AUTH_PASSWORD_VALIDATORS`):
  - common passwords;
  - all-numeric passwords;
  - passwords too similar to the user's name or email.
- **Optional:** check against known breached passwords with the "Have I Been Pwned" range API. Only a short prefix of the password's hash is sent.
- **Changing a password** requires the current password; signing out other devices is the user's choice (section 4).

### Not revealing which emails exist

No screen may reveal whether an email has an account. Every case gets the same reply:

| Screen                                                              | Reply                                           |
| ------------------------------------------------------------------- | ----------------------------------------------- |
| Sign-in fails (wrong password, unknown email, wrong method, locked) | "Email or password is incorrect"                |
| Sign-up (new, already registered, unverified, reclaim)              | "Check your email to finish signing up"         |
| Forgot password                                                     | "If an account exists, we've sent a reset link" |

The email itself tells the real owner what happened (new account, "you already have an account", reset link, or "your account uses Google"). Response timing should match too: hash a dummy password when the email is unknown, so a fast reply doesn't give the answer away.

**Rate limits** (DRF throttling, per email and per IP):

| Action                           | Limit                    |
| -------------------------------- | ------------------------ |
| Resend verification              | 1 per minute, 5 per hour |
| Forgot password                  | 1 per minute, 5 per hour |
| Sign-up                          | 10 per hour per IP       |
| Invitations sent by one landlord | 20 per hour              |

DRF stores throttle counts in Django's cache, which is **Redis** (`CACHES` in `config/settings.py`, address in `REDIS_URL`). All backend processes share it, so a limit holds no matter which process answers.

### Sending auth emails

Verification, reset, invitation and wrong-method emails don't use the notification queue, because its stored events may not contain credentials and these links are credentials.

1. In one transaction: create the token and store only its hash.
2. Commit.
3. Then, in the same request, send through the email provider's HTTP API.

If sending fails, the action stays committed and the screen offers "Resend", which creates a new token and invalidates the old one. No raw token is ever stored. A background worker can replace step 3 later if lost emails become a problem.

### Sign-in throttling (`sign_in_throttles`)

One row per `email_normalized`, keyed by email rather than user. Unknown emails get the same treatment, so the sign-in screen doesn't reveal which emails are registered.

- Wrong guesses 1–4: counted, no lock.
- From the 5th wrong guess: lock for 10 minutes, and each further wrong guess doubles it (20, 40, 80 … minutes).
- Successful sign-in: reset `failed_count`, `last_failed_at` and `locked_until`.
- While locked: reject without checking the password, and don't count the attempt.
- Increment under a row lock. Log each individual attempt to the security log, not this table.
- The numbers (5, 10 minutes, doubling) live in the sign-in service, not the table.

## 7. Bans (`ban_list`)

| `ban_type`     | Target column | Blocks                              |
| -------------- | ------------- | ----------------------------------- |
| `EMAIL`        | `value`       | That email signing up or signing in |
| `EMAIL_DOMAIN` | `value`       | Every email at that domain          |
| `PHONE`        | `value`       | That phone number                   |
| `ACCOUNT`      | `user`        | That existing account               |

- `value` is stored trimmed and lowercased. Store phones in one format, for example `+61400000000`, both here and in `users.phone_number`.
- `reason` is required. `expires_at` is optional; empty means permanent.
- Lifting a ban keeps the row and sets `lifted_at`, `lifted_by` and `lift_reason`.
- One current ban per identity or account. To extend an expired ban, update `expires_at` on the existing row, or lift it before adding a new one.
- Record account bans in `account_access_history`.

## 8. Roles and permissions

- **Roles** come through `user_role_bridge` → `role_permission_bridge` → `permissions`. Every link has `is_active`: revoke by setting it to false, and reactivate the same row.
- **Individual grants** (`user_permission_bridge`) are special cases added to one user on top of their roles, with a required `reason`. Granting a role does **not** copy its permissions into grants.
- **Effective permissions:**
  - the user is active, not deleted and has no active ban;
  - and the code comes from an active role path or an active individual grant.
- **Super admin** is `users.is_top_level_admin`, not a role. Super admins also hold ADMIN.
  - They may do every action, including party actions such as creating a property for a landlord.
  - Records show the super admin as the actor. The person they acted for goes in `on_behalf_of` on `business_change_history`, `review_status_history` and `maintenance_status_history`.
  - Only a super admin may set `is_top_level_admin` or `on_behalf_of`.
- **`access.view_hidden_records`** never comes from a role or from super admin status alone. It needs `access_policy` ≠ `DENY_ALL`, plus `is_top_level_admin`, plus an active individual grant.
- **Permission codes:** see `accounts/seeds/permissions.py` (draft, pending review).

## 9. MFA for Admin and super admin

Required for every user with an active ADMIN role or `is_top_level_admin`. A super admin can do everything, so a stolen password alone must not be enough.

- **Enrol:**
  1. Generate a TOTP secret.
  2. Store it **encrypted** in `user_mfa.secret_encrypted`, using an app-level key (for example Fernet with `MFA_ENCRYPTION_KEY` in `.env`). It has to be encrypted, not hashed, because the code check needs the original secret.
  3. Show the QR code.
  4. Set `confirmed_at` once the first code is entered correctly.
  5. Generate about 10 backup codes, show them once, and store each with `make_password`.
- **Sign in:**
  1. After the password or Google step, ask for a code.
  2. Accept it only if its time step is newer than `last_used_step`, so a code can't be replayed, then update `last_used_step`.
  3. Set `auth_sessions.mfa_verified_at`.
  4. A backup code works once (`used_at`).
- **Enforcement:** admin routes require `mfa_verified_at` on the current session. An Admin without confirmed MFA can only reach the enrolment screen.
- **Google admins too:** Google's own 2-step verification isn't visible to us, so Google-signed-in admins also use our MFA.
- **Reset:** a lost device is reset by a super admin. That deletes the `user_mfa` and backup-code rows (they are credentials, not business records), revokes the user's sessions, and is recorded in `account_access_history`.

## 10. Deferred

- **Changing email:** not allowed for now. Revisit after other parts are in place. When it's built, it needs:
  - an `EMAIL_CHANGE` purpose and a `new_email` column on `auth_tokens`;
  - verifying the new address before the switch;
  - a notice to the old address.

  Google accounts can never change email in RentTrace; their email comes from Google.

## 11. Open items

- [ ] Profile photo: Google sends `avatar_url` / `picture`, but `users` has no column for it yet.
- [ ] Cap on the sign-in lock? Doubling has no limit: guess 15 locks about 3.5 days, guess 20 about 227 days. Suggested cap: 24 hours.
- [ ] Confirm the Supabase project's signing setup (JWKS or JWT secret) and add the Supabase keys to `.env`.
- [ ] Update spec v3 §3 and §14, which still say we store no credentials.
- [ ] Add `MFA_ENCRYPTION_KEY` to `.env` and the `cryptography` package to `requirements.txt` when MFA is built.
- [ ] Add `PyJWT` to `requirements.txt` and `expo-secure-store` to the mobile app when auth is built.
- [ ] Run a Redis server for local development and provision one for production; set `REDIS_URL` for each.
- [ ] Recovery path for users who lose access to their Google account (Admin-assisted).
- [ ] App Store review guideline 4.8: check whether offering Google sign-in requires Sign in with Apple or another privacy-focused option.
