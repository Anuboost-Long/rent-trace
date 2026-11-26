# Admin overview

## Status — 25 November 2026 (Figma layout)

Laid out as the Figma Overview (see [Admin design alignment](admin-design-alignment.md)).
Type-checked and linted; **not seen in a browser yet.** The API is unchanged.

- `/admin` now opens straight on the dashboard. The menu grid and its `?view=` toggle are gone.
- At the top is a greeting: "Good morning / afternoon / evening, {first name}". It shows
  "Welcome" until the browser knows the time of day.
- **Four stat cards**, each linking to its list. A card is left out when its block is `null`.
  - Admin: Suspended accounts (out of all accounts), Active bans, Invitations waiting (with the
    expired count) and Tenancies ending soon (next 60 days).
  - Landlord: Properties (with units), Active tenancies, Invitations waiting and Tenancies ending
    soon.
- **Tenancies** card: the active count and the bar of all statuses, with "See all". The users,
  properties and units totals no longer have a row of their own; they appear inside the cards.
- **Recent Admin actions**: the activity entries as a timeline (who did what to whom, and when).
- Not shown, because the API has nothing for it yet: the Figma "Needs you" queue (cases,
  removal requests) and "Email delivery".

## Status — 16 November 2026

Landlord overview added 16 Nov 2026: back end has 2 new tests (pass), admin typecheck and
lint pass. Walked through in Chrome the same day as the test landlord: figures matched the
database and "See all" opened the landlord tenancy list. Non-zero "needs attention" counts were
not seen in the browser (the test data has none).

Built. Back end: 8 tests pass (`back-end/overview/tests/`). Walked through in
Chrome on 12 November 2026 as the super admin: the blocks render with real figures
and match the lists (a new draft tenancy raised the total, a lifted ban left the
active-bans count at 0).

## Goal

An admin opens `/admin` and sees how the platform is doing from
real numbers, and what needs a follow-up.

## How it works

- `GET /api/overview/` is open to any admin (not landlords or tenants). Each block
  comes back only if the person holds the permission that shows it; otherwise it is
  `null` and the screen leaves it out.
- **Tenancies** (`tenancies.admin_view`): count per status (draft, pending, active,
  ended, cancelled); active tenancies ending in the next 60 days; invitations still
  waiting for an answer; invitations that expired without one. Revoked and
  accepted invitations are not counted.
- **People** (`accounts.view`): users, and how many are suspended. Deleted accounts
  are not counted.
- **Properties** (`properties.admin_view`): properties and units, not counting
  deleted ones.
- **Bans** (`bans.view`): bans that are in force now.
- **Recent activity** (`accounts.view`): the latest six entries in the account
  history: who changed which account and when.
- The headline number is the count of active tenancies; the bar shows all
  statuses.

## Landlord overview

- `/landlord` shows the same dashboard, limited to the landlord's own properties, with its own
  four cards (see the status above).
- `GET /api/landlord/overview/` is for landlords only (admins and tenants get 403).
  It returns the same shape as the admin endpoint. **Properties** (`properties.view`)
  and **Tenancies** (`tenancies.view`) are filled in for the landlord's own properties;
  people, bans and activity are always `null`, so the screen leaves them out.
- Invitation counts cover only invitations on the landlord's own tenancies.
- "See all" links to the landlord's tenancy list.

## Source locations

- Back end: `back-end/overview/` (`GET /api/overview/`); named queries in
  `TenancyQuerySet`, `TenancyInvitationQuerySet` and `AccountAccessHistoryQuerySet`.
- Landlord: `back-end/overview/landlord_urls.py`, `LandlordOverviewView` in `views.py`,
  `get_landlord_overview` in `services/get_overview.py`; page `admin/app/(app)/landlord/page.tsx`.
- Admin: `admin/components/overview/dashboard.tsx` (shared by both areas), `greeting.tsx`, `admin/api/services/overview/`,
  `admin/types/overview/models.ts`, `admin/constants/overview.ts`.

## Not done

- Maintenance, landlord verification and disputed rent figures: those modules have
  no data yet, so the old sample counts were removed instead of faked.
- Activity covers account history only. Property and tenancy changes are not
  written to a history table yet.
- Month-on-month change and any chart over time.
