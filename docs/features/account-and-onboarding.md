# Account and onboarding

## Status — 12 November 2026

Shipped 11 November 2026. Not re-verified when this was written.

## Goal

A new Google user finishes setting up (names and role), and anyone signed in can
manage their own profile and password.

## How it works

- **Onboarding** (`/auth/onboarding`, `POST /api/auth/onboarding/`): shown after a
  first Google sign-in. Asks for first and last name (prefilled from Google's full
  name, both required) and whether the person is a **tenant** or a **landlord**.
  Admin can never be chosen. Email/password users give the same details in the
  sign-up form instead.
- **Where people land:** `homePathFor` sends a member to `/admin`, `/landlord` or
  `/tenant` by role, or to onboarding when they have none.
- **Account page** (`/account`):
  - **Profile:** edit first name, last name and phone number (blank clears it).
    Email can't be changed. Needs `accounts.update_profile`; admins must have
    finished two-step verification. Recorded in `account_access_history`.
  - **Security:** change password, with the option to sign out other devices.

## Source locations

- `back-end/accounts/`: onboarding and profile views and services.
- `admin/app/(app)/account/`: `page.tsx`, `profile-section.tsx`, `security-section.tsx`.
- `admin/app/auth/onboarding/`.
- `admin/hooks/form/useOnboarding.ts`, `useUpdateProfile.ts`, `useChangePassword.ts`.
- `admin/constants/audience.ts`: `homePathFor`.

## Not done

- Email change (see [Authentication](authentication.md)).
