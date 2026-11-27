# Maintenance

## Status — 17 November 2026 (phase 2: super admin acts for the landlord)

Built; **not yet walked through in a browser** (needs a signed-in super admin). 10 new back-end
tests pass, and so do all 67 in maintenance and notifications; admin typecheck and lint pass.

- **Who:** only a super admin (`is_top_level_admin`). A normal admin stays read-only.
- **What (first cut):** the landlord's status moves only: **acknowledge**, **start work**, and
  **close directly** when no tenant lives there. Closing proposals, booking a tradesperson and
  marking a visit done stay with the parties.
- **Acting for:** automatic. The admin acts for the property's **primary owner**; there is nothing
  to pick. If the property has no current primary owner the action is refused. A super admin who
  is themselves the landlord of the issue just acts as the landlord, with nobody recorded as
  acted for.
- **Record:** the status history row shows the admin as `actor` and the owner as `on_behalf_of`
  (the only history table with that column in this feature). The timeline shows it as
  "Admin name, for Owner name". The issue's `updated_by` is the admin. The usual notifications
  go out as they do for the landlord.
- **API:** `POST /api/admin/maintenance/<id>/acknowledge/`, `/start/` and `/close/` (outcome and
  reason, as the landlord's). Non-super admins, landlords and tenants get 403. The same rules
  apply as for the landlord: right status, no open closing proposal, vacant for `/close/`.
- **Screens:** on `/admin/maintenance/<id>` a super admin sees the same Acknowledge, Start work
  and Close buttons the landlord would; everyone else sees none. The detail's `actions` list is
  what drives this.
- Acceptance: a super admin acknowledges and starts an issue and the history rows carry
  `on_behalf_of`; a normal admin, landlord of another property or tenant is refused; a property
  with no primary owner is refused; a super admin who owns the property records no
  `on_behalf_of`.

## Status — 16 November 2026

Admin read-only view: **built and walked through** in Chrome as an admin on 16 Nov 2026: the list
shows issues from every landlord, search narrows it (`q=hallway` returned only that issue), the
detail shows the timeline (including "Closing rejected") with no action buttons. 6 back-end tests
pass. Acting for a party (`on_behalf_of`) is phase 2 and not started.

### Admin view (phase 1, read-only)

- Admins with `maintenance.admin_view` list and open every issue across all landlords, at
  `/api/admin/maintenance/` and `/api/admin/maintenance/<id>/` (the unprefixed path is the party
  endpoint, so the admin one is under `admin/`). Landlords, tenants and admin-side people without
  the code get 403.
- The list filters by status and searches title, property name and suburb. The detail is the
  same as the party detail (timeline, closing proposal, tradesperson) but never offers an action:
  an admin is on neither side, so `actions` and `provider_options` are empty and `my_side` is null.
- Admin screens: `/admin/maintenance` and `/admin/maintenance/<id>`, linked from the admin menu and
  sidebar for anyone holding `maintenance.admin_view`.
- Acceptance: an admin sees issues from two landlords; a landlord or tenant calling the admin
  endpoint gets 403; the detail has no actions; the screens show no action buttons.

## Status — 15 November 2026

A rejected closing now leaves a trace on the issue itself: the timeline shows a "Closing
rejected" entry (who rejected it and the original proposal's reason), not just a notification
to the proposer. Verified live in Chrome against real historical data from the 13 November
walkthrough (`maintenance/resources/issue_detail.py`, `_rejected_closure_entries`; built from
`MaintenanceClosureResponse` rows, same pattern as the tradesperson-visit entries — no
migration needed).

## Status — 12 November 2026

Built, not yet seen in a browser. Back end: 29 tests (reporting, scoping, the workflow, every closure path, a stale proposal, closing when nobody is left, notifications) and the full suite pass. Admin: type-check, lint and a production build pass. The new migrations (`maintenance/0003`, `notifications/0007`) have **not** been applied to the dev database yet, so the screens can't be opened until they are.

## Goal

A tenant reports something that needs fixing; the landlord sees it, says they have, starts work and
says when it is done. Closing an issue needs the **other side's agreement**: if the landlord says it
is fixed, the tenant confirms; if the tenant says it is no longer a problem, the landlord confirms.
Both sides can see where an issue stands without email.

## How it works

### Who can do what

One API, `/api/maintenance/`, scoped by who is asking: a tenant sees issues on the units of tenancies
they are a **current tenant** of; a landlord sees issues on properties they **currently own**. Anything
else is a 404. Admins are not included yet (see "Not done"). Permissions already seeded:

| Action                         | Permission                    | Who                                                   |
| ------------------------------ | ----------------------------- | ----------------------------------------------------- |
| Read, list                     | `maintenance.view`            | the two scoped groups above                           |
| Report                         | `maintenance.report`          | a current tenant of an **active** tenancy             |
| Acknowledge, start work        | `maintenance.confirm_start`   | landlord side only (checked in the service)           |
| Propose a closure, withdraw it | `maintenance.propose_closure` | either side                                           |
| Approve or reject a closure    | `maintenance.review_closure`  | the **other** side                                    |
| Close with nobody to approve   | `maintenance.close_vacant`    | landlord, only when the tenancy has no current tenant |

### An issue

- Has a title, a description, a priority (`LOW`, `MEDIUM`, `HIGH`, `URGENT`), the unit and tenancy it
  belongs to, who reported it and when.
- Status: **Reported** to **Acknowledged** to **In progress** to **Closed**. Every move is written to a
  history in the same transaction (a sequence number, who, the trigger, a reason), shown as a
  timeline on the issue. The timeline also lists when a tradesperson was booked and when the
  visit was marked done ([Service providers](service-providers.md)). Those two are read from the
  assignments at display time, not stored as status history, because they don't change the
  status. Each history entry has a `kind`: `STATUS`, `PROVIDER_BOOKED` or `VISIT_DONE`.
- **Acknowledge** is an explicit button, not a side effect of opening the issue (the "reads" table
  stays unused for now). **Start work** moves an acknowledged issue to in progress.
- **Closing** can be proposed from any open status, by either side, with an outcome (`FIXED` or
  `NOT_FIXED_NO_ACTION`) and a reason. The proposal is open until it gets an answer:
  - **Who approves:** if a tenant proposed, **any current owner** of the property; if a landlord
    proposed, **any current tenant** of the tenancy. Nobody can approve their own proposal.
  - **Approve** closes the issue with that outcome. **Reject** keeps it open and tells the proposer,
    who can propose again. The proposer can **withdraw** it.
  - One proposal is open at a time: the issue points at its open proposal, so the database enforces it.
  - While a proposal is open the issue can't be moved along; the proposal is answered first.
  - Approving checks the issue hasn't changed since the proposal (`row_version`) and is still open;
    a stale proposal is refused, not applied.
- **Nobody to approve:** when the tenancy has ended or has no current tenant, the landlord can close
  an issue directly with an outcome and a reason (`maintenance.close_vacant`).
- A tenant whose tenancy has ended can still read their old issues but can't change them.

### Notifications

The landlord is told when an issue is reported; the reporter when it is acknowledged or work starts;
the other side when a closure is proposed; the proposer when it is approved or rejected. Messages
carry the issue title, never contact details.

### Not in the first version

Comments, recurring issues, and receipts shown inside the issue (receipts are documents linked to the
issue; see below). Photos are built (below).

### Photos on an issue

Decided and built 28 November 2026 (API only; screens to follow). Anyone who can see an issue (the
tenants of its tenancy, past ones included, and the property's owners) can add photos to show what is
wrong, while the issue is not closed.

- `POST /api/maintenance/<id>/photos/` (multipart `file`, optional `caption`; permission
  `maintenance.report`): JPEG or PNG up to 10 MB, at most 10 per issue (400 beyond that or for other
  file types). Closed issues refuse new photos.
- `GET /api/maintenance/<id>/photos/<file_id>/` downloads one (`maintenance.view`); admins use
  `GET /api/admin/maintenance/<id>/photos/<file_id>/` (`maintenance.admin_view`). Anyone who cannot see
  the issue gets a 404.
- `DELETE /api/maintenance/<id>/photos/<file_id>/` removes a photo, only the person who added it and only
  while the issue is open (the file is hidden, not deleted).
- The issue detail lists `photos` (id, name, caption, who added it, when, and whether it is yours).
- **Receipts** are documents: a landlord publishes a `RECEIPT` document linked to the issue with
  `maintenance_issue_id` (see [Documents](documents.md)); tenants see it on their tenancy's documents.

### Trade and tradesperson

A tenant can say what kind of problem it is when reporting (optional, from the same list of
trades the landlord's tradespeople use). The landlord can book one of their tradespeople linked to
the property, with a date, and later mark the visit done. The tenant is told and sees the
tradesperson's contact details on the issue. Booking does not change the issue's status. See
[Service providers](service-providers.md).

## Source locations

- Back end: `back-end/maintenance/` (models exist; `services/`, `views.py`, `dtos/`, `resources/`,
  `tests/` are new), `/api/maintenance/…`.
- Schema (see `back-end/docs/schema-changes-for-diagram.md`): `maintenance_closure_proposals.review_request`
  becomes optional, because the review engine isn't built; a new `maintenance_closure_responses` table
  records each proposal's answer (approved, rejected or withdrawn), keeping proposals append-only; and
  `maintenance_issues.open_closure_proposal` points at the proposal waiting for an answer.
- Admin acting (super admin): `AdminAcknowledgeIssueView`, `AdminStartWorkView`,
  `AdminCloseVacantView` in the same file; `acting_landlord` in `services/shared/rules.py`;
  `accounts/security/super_admin_permission.py`.
- Admin read-only: `back-end/maintenance/admin_views.py`, `admin_urls.py`, `services/list_all_issues.py`,
  `get_any_issue.py`; `admin/app/(app)/admin/maintenance/` (shares `admin/components/maintenance/`).
- Admin: `admin/app/tenant/maintenance/`, `admin/app/(app)/landlord/maintenance/`,
  `admin/components/maintenance/`, `admin/hooks/form/useIssueActions.ts`, `admin/api/services/maintenance/`.

## Not done

- Everything under "Not in the first version" above.
- Super admins can acknowledge, start and close-when-vacant for the primary owner (above). They
  cannot propose or answer a closing, book a tradesperson or mark a visit done. Normal admins
  cannot act at all.
- Landlords reporting issues themselves (for a vacant unit or an inspection).
