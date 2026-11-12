# Bans and sessions

## Status — 12 November 2026

Shipped 11 November 2026. Not re-verified when this was written.

## Goal

Admins see who is banned and which sessions are live, and can create or lift a
ban, or end a session.

## How it works

- **Bans** (`/admin/bans`, needs `bans.view`): every ban, newest first, with
  status `ACTIVE`, `EXPIRED` or `LIFTED`. Filter by search, status and type.
  **Lift** (needs `bans.manage`) requires a reason, kept on the ban. Lifting an
  account ban also writes the person's history.
- **Sessions** (`/admin/tokens`, needs `tokens.view`): every signed-in session
  with person, device, IP, last used, expiry, status `ACTIVE`, `REVOKED` or
  `EXPIRED`, and whether it is the current one. **Revoke** (needs `tokens.revoke`)
  stops the access token on the next request and the refresh token from being
  used, with an optional reason. You can't revoke your own session.
- **Create a ban** (the Ban button on `/admin/bans`, needs `bans.manage`): ban an
  email, an email domain or an account, with a required reason and a duration
  (never, 1, 7, 30 or 90 days). Emails and domains are trimmed and lowercased; a
  leading `@` on a domain is dropped. Banning an account ends all of that person's
  sessions and writes `ADMIN_BANNED_ACCOUNT` to their history. Refused (400): a
  target that is already banned, an expiry in the past, a malformed email or
  domain, your own account. The super admin account can't be banned (403), and the
  same "can't act on someone who can do more than you" rule applies.
- Acting on an admin's bans or sessions follows the access rule: you can't act on
  someone who can do more than you can.

## Source locations

- `back-end/bans/`, `back-end/tokens/`: `/api/bans/`, `/api/tokens/`. Create: `bans/services/create_ban.py`, `bans/dtos/create_ban.py`.
- `admin/app/admin/bans/` (`create-ban-button.tsx`), `admin/app/admin/tokens/`, `admin/hooks/form/useCreateBan.ts`.
- `admin/api/services/bans/`, `admin/api/services/tokens/`, `admin/types/security/models.ts`.

## Not done

- Phone bans can't be created: nothing checks a phone number at sign-in yet, so the ban
  would do nothing.
- Create-ban was added 12 November 2026: 9 back-end tests pass (`bans/tests/test_create_ban.py`),
  the admin dialog was walked through in Chrome on 12 November 2026: an email ban was
  created, a duplicate showed "This is already banned.", and it was lifted. Account
  and domain bans were not tried in the browser.
