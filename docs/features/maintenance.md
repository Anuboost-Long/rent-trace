# Maintenance

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
  timeline on the issue.
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

Photos on an issue, comments, assigning a provider, recurring issues, and service categories (the
fields exist and stay empty).

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
- Admin: `admin/app/tenant/maintenance/`, `admin/app/(app)/landlord/maintenance/`,
  `admin/components/maintenance/`, `admin/hooks/form/useIssueActions.ts`, `admin/api/services/maintenance/`.

## Not done

- Everything under "Not in the first version" above.
- Admins: no list or detail yet. It needs its own endpoint and tests rather than a half version.
- Landlords reporting issues themselves (for a vacant unit or an inspection).
