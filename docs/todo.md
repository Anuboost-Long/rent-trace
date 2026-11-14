# To do

Written 14 November 2026 at the end of a long walkthrough session, so a fresh session can pick
up without the history. Everything here is work still to do. Done work is in the feature
documents and `git log` (latest commits: `a420f8b` occupancy, `8771fdc` maintenance timeline,
`166a080` closed-tenancy wording, `cae89d7` schema enum names).

## Context a new session needs

- Branch `feat/database-models`. Back end on :8000, admin on :3000, Postgres and Redis in Docker.
  All were already running.
- The back end sends **real email through the Gmail API** (`config/.env`). Never trigger a send to
  a made-up address from the screens. For tests in the browser, call the service with
  `mock.patch` on the email function (for example `tenancies.integrations.emails.send_invitation`,
  `communications.integrations.emails._send`) and capture the link, then use the link in the browser.
- Local test accounts (verified, same throwaway password, kept outside the repo): landlord
  **`kimlongly57+landlord@gmail.com`** (was `test.landlord@renttrace.test` until 15 Nov 2026, when
  its email was swapped to a real address to test outbound mail — see item 3), tenant
  **`kimlongly57+tenant@gmail.com`** (was `test.tenant1@renttrace.test`, same reason), tenant
  `test.tenant2@renttrace.test` (unchanged). Also new since 15 Nov: `kimlongly57+housemate@gmail.com`
  (TENANT, pre-verified) and `kimlongly57@gmail.com` itself, now a real signed-up TENANT account.
  The password file was in the session scratchpad and will be gone; to get back in, set a new
  password with `make_password` on their `UserCredential` in `manage.py shell` — except
  `kimlongly57@gmail.com`, which the user signed up themselves and whose password is theirs, not
  ours to reset.
- Test data left in the dev database: property 3 "Walkthrough house" (unit 4) is now **OCCUPIED**
  (tenancy 6, Active, `kimlongly57@gmail.com` as primary tenant plus `kimlongly57+housemate@gmail.com`
  as an approved housemate) — it dropped out of public listings as a result, which is correct
  behaviour, not a bug. Tenancies 1 (ended 15 Nov, was Active), 2 (ended), 3 (cancelled), 4 (ended),
  5 (cancelled), 6 (Active, see above), 7 (revoked invitation only, never started) exist. Maintenance
  issues 1 (closed) and 2 (open, Reported), contact request 2 (revoked) and 3 (accepted, 15 Nov),
  tradesperson "Spark Electrical". Delete or reuse as needed.
- Browser checks use Claude in Chrome. Signing in as another user means signing out first, because
  all roles share one cookie on localhost.

## 1. Admin-side walkthrough (needs the user to log in first) — done 15 Nov 2026

Walked through in Chrome as the regular admin (`kimlongly53@gmail.com`, logged in by the user).
Results are in `docs/features/admin-tenancies.md`, `tenancy-lifecycle.md`, `properties.md` and the
"Known issues" list in `docs/features/README.md`. Summary:

- `admin/constants/navigation.ts` and `admin/app/(app)/admin/` confirmed: the admin app has
  **no Maintenance, Contact requests or Tradespeople screens at all** — not unlinked, not built.
  Only Overview, Users, Access, Properties, Tenancies, Bans, Access tokens exist.
- Overview dashboard: numbers matched actions taken during the walkthrough.
- Tenancies: viewed the list and detail pages; Edit correctly 404s for `ENDED`/`CANCELLED`
  (by design); Start correctly refuses with "Add a tenant first" when no tenant has joined;
  created a draft and cancelled it (worked); ended an active one (worked, unit went back to
  `VACANT`, `updated_by` recorded the admin).
- **The `on_behalf_of` check doesn't apply to tenancies at all** — only
  `maintenance_status_history` and the unbuilt reviews tables have that column (confirmed against
  the super-admin memory note). Since there's no admin maintenance screen, that check can't be
  exercised from the UI anywhere right now.
- Properties/units: viewed and confirmed (again) that there's no occupancy field anywhere in the
  unit edit form — ties to decision item 2 below.
- Not done: starting a tenancy all the way to `ACTIVE` from the admin side, because that needs an
  invited-and-accepted tenant, which needs a real email send — see item 3.

## 2. Decisions to put to the user, then do

- **Declined rent proposal is missing from the tenant's "Rent and bond history".** Only applied
  changes show. Decide whether declined and withdrawn proposals should show too.
- **A rejected maintenance closing leaves no trace on the issue** (the banner disappears; the
  landlord only gets a notification). Decide whether the timeline should show "Closing rejected".
- **"Visit done" shows the landlord who booked the tradesperson**, because marking a visit done
  does not store who did it. Fine while only the landlord can do it; add a `completed_by` column
  (new migration) if that changes.
- **`PARTIALLY_OCCUPIED` and `UNAVAILABLE` have no screen.** A unit is only ever set
  `OCCUPIED`/`VACANT` (by starting and ending a tenancy). There is no way in the unit form to mark
  one unavailable or partly occupied. Decide whether rooms and shared units need this.

## 3. Test the emails for real — done 15 Nov 2026

Used `kimlongly57@gmail.com` (user-owned). All four real sends confirmed arriving with correct
wording and working links: tenant invitation (+ resend, + revoke-without-accepting), housemate
request (to the landlord and to the housemate, plus the landlord's in-app notification fired
correctly alongside the email — no gap there), contact request received and answered. Full
results in `docs/features/tenant-invitations.md`, `housemate-invitations.md`,
`contact-requests.md`, `admin-tenancies.md`.

Account/email changes made to run this (dev database only, not committed):

- `test.landlord@renttrace.test` → `kimlongly57+landlord@gmail.com`
- `test.tenant1@renttrace.test` → `kimlongly57+tenant@gmail.com`
- New account created directly via shell (pre-verified, skipping the signup email loop):
  `kimlongly57+housemate@gmail.com`, role TENANT
- All three share a throwaway password, recorded in the session scratchpad, not here or in the
  repo (same convention as the original test accounts).
- `kimlongly57@gmail.com` itself (no alias) is now a real TENANT account, primary tenant and
  Active on tenancy 6 ("Walkthrough house", unit 4) — a new, real piece of test data distinct
  from the property-3/unit-4 state described below, which is unaffected.

## 4. Screens not tried from the browser — done 15 Nov 2026

All tried for real in Chrome: sending a contact request from the listing page (as `Tom Tenant`,
swapped to `kimlongly57+tenant@gmail.com`) and accepting it as the landlord; the tenant's
"Invite housemate" form; Resend and Revoke on a tenancy invitation. Declining/cancelling a
contact request was not tried (the one sent was accepted, to also test the "answered" email) —
still open if wanted.

## 5. Small fixes found during the walkthrough

- Landlord overview page (`admin/app/(app)/landlord/page.tsx`) is only a header: a placeholder.
- Empty properties list says "No properties match these filters" when no filter is set. It should
  invite adding a property (the tradespeople list already does this well).
- The invitation accept page says "Join a tenancy" without naming the property until after
  accepting. Show the place and who invited them.
- Dates show in UTC ("13 Nov 2026" late in the evening local time). Decide on local time or label
  the zone everywhere, not only on the maintenance timeline.
- Tenant maintenance list: the Filter button stretches across the whole row.
- Tradespeople list with zero results still renders a Next link to `?page=2`.
- `docs/features/README.md` table rows were rewritten by script and no longer align in columns;
  run Prettier on it.

## 6. Housekeeping

- Run `python manage.py migrate` on any other database. `notifications/0008` was not applied in
  the dev database until this session, which made booking a tradesperson fail with
  "Something went wrong". The generic error text hid the cause: consider a clearer message for
  a 500 on that action.
- Units that already had an active tenancy before the occupancy fix were corrected by hand once in
  the dev database. If real data exists elsewhere, run `sync_occupancy` over active tenancies.
- Before finishing any back-end change run the checklist in `back-end/AGENTS.md` section 7
  (all of it passes as of `cae89d7`).
