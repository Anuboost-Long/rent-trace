# To do

Updated 26 November 2026. Kept so a fresh session can pick up on what's left without re-deriving
context. Older done-item detail lives in `git log` and the feature docs, not here.

## What's left

Next big piece: [Reviews](features/reviews.md), phase 2 (disputes and the admin queue). Slice 1,
tenant condition evidence, is built and walked through (25 Nov 2026). The build order and open
questions are in that document; the open questions need answers before phase 2.

Smaller gaps:

- Not yet walked through: the landlord overview (16 Nov), super admin maintenance status moves
  (17 Nov), and the landlord's notification link for condition evidence.
- The authenticator reset email has never been seen arriving (the Gmail token has expired).
- The new tab animation (sliding underline and content, `components/common/tab-bar.tsx`,
  `tab-content.tsx`) has not been seen move; the dev server served stale CSS. Restart `npm run
dev` and look.
- The dev overlay's "Date.now()" blocking-route warning shows on every signed-in page. `next
build` is clean, so it is dev-only; cause not found.
- `npm audit` reports 7 moderate vulnerabilities in admin.
- Documents have no API; `business_change_history` is not written for property and unit edits.

(Done items D and E, local-time dates and the landlord overview, are in their feature documents:
[Date display](features/date-display.md), [Admin overview](features/admin-overview.md).)

## Context a new session needs

- Branch `feat/reviews` (merged work from `feat/database-models`). Back end on :8000, admin on :3000, Postgres and Redis in Docker.
- The back end sends **real email through the Gmail API** (`config/.env`). Never trigger a send to
  a made-up address from the screens. For automated tests, `mock.patch` the email function (e.g.
  `tenancies.integrations.emails.send_invitation`, `communications.integrations.emails._send`).
- Local test accounts (same throwaway password, recorded outside the repo in the session
  scratchpad — gone between sessions; reset with `make_password` on `UserCredential` via
  `manage.py shell` if needed): landlord `kimlongly57+landlord@gmail.com`, tenant
  `kimlongly57+tenant@gmail.com`, tenant `kimlongly57+housemate@gmail.com`, tenant
  `test.tenant2@renttrace.test`. **Never** sign into `kimlongly57@gmail.com` (bare, no alias) or
  the regular admin account (`kimlongly53@gmail.com`) — those are the user's own real accounts;
  the user logs into those themselves.
- Test data in the dev database: property 3 "Walkthrough house" (unit 4) is **OCCUPIED** (tenancy
  6, Active, `kimlongly57@gmail.com` primary tenant + `kimlongly57+housemate@gmail.com` approved
  housemate) — correctly dropped out of public listings. It also has a DECLINED rent change in
  its history ($650/week → $700/week) from verifying item A — rent is still $650. Tenancies 1–5
  and 7 are ended/cancelled/revoked test data. Maintenance issues 1 (closed) and 2 (open), contact
  requests 2 (revoked) and 3 (accepted), tradesperson "Spark Electrical". Tenancy 6 also holds test condition
  reports from the reviews walkthrough (approved, rejected, withdrawn) and one dispute case. Delete or reuse as
  needed.
- Browser checks use Claude in Chrome. Signing in as another user means signing out first — all
  roles share one cookie on localhost.

## Done this session (15 Nov 2026)

- **Admin walkthrough** (tenancies, properties, occupancy) — `docs/features/admin-tenancies.md`,
  `tenancy-lifecycle.md`, `properties.md`, README "Known issues".
- **Real-email tests**: tenant invitation + resend + revoke, housemate request (+ in-app
  notification), contact request — all confirmed against real Gmail. See
  `tenant-invitations.md`, `housemate-invitations.md`, `contact-requests.md`.
- **A — declined/withdrawn rent proposals** now show in the tenant's rent history (`4c5a627`). See
  [Rent change approval](features/rent-change-approval.md).
- **B — rejected maintenance closing** shows "Closing rejected" in the issue timeline (`1c1dee9`).
  See [Maintenance](features/maintenance.md).
- **C — manual unit occupancy control** (Vacant/Partly occupied/Unavailable), refused while a
  tenancy is active (`d3e5211`). See [Properties](features/properties.md).
- **G — invitation preview**: accept page now names the property/unit before accepting
  (`f0f62f7`).
- **F, H — small UI fixes**: empty-properties state, maintenance filter button layout (`f0f62f7`).
- **I — tradespeople pagination**: checked, not reproducible, no change needed.
- **Decided, not building now**: `completed_by` on maintenance visits — only the landlord can mark
  a visit done today, so current behaviour is already accurate; revisit only if that changes.

Full detail, code locations and live-verification notes for all of the above are in the commits
and the linked feature docs — not duplicated here.

## Housekeeping

- Run `python manage.py migrate` on any other database — `notifications/0008` was missing in dev
  until this session and caused a generic 500 when booking a tradesperson. Consider a clearer
  error message for that case.
- Before finishing any back-end change, run the checklist in `back-end/AGENTS.md` section 7.
