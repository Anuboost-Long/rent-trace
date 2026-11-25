# Reviews

## Status — 25 November 2026

Planned. The tables exist (`back-end/reviews/`, migration `0001_initial`) and the permission
codes are seeded. There is no API, no service and no screen. Nothing here is verified.

## Goal

One shared way for a change that needs the other party's agreement, or an admin's, to be
proposed, answered and recorded. A landlord or tenant can propose a correction, the other side
approves, rejects, asks for more information or disputes it, and an admin settles what the two
sides cannot. Every step is kept, so either party can later show what was agreed and why.

This is an approval engine, not star ratings.

## How it works

Intended behaviour, taken from the existing models. Rules marked "decide" need an answer first
(see Open questions).

- **Target.** A request is about one thing: a property, unit, area, tenancy, condition record,
  maintenance issue, document, communication log, provider link, user, file or access policy.
  `review_targets` holds exactly one of those. A target is created the first time something is
  reviewed.
- **Request.** Has a `kind` (evidence review, shared change, locked correction, contract
  change, dispute, settlement, maintenance closure, document confirmation, data removal), the
  requester's side, and a route: opposite side, admin, or owner direct.
- **Submission.** Each request holds numbered submissions (revision 1, 2, ...). A submission
  stores the before and proposed values, a reason, optional attachments, and the row version it
  was based on. Resubmitting after "needs information" adds a revision; it never edits an old one.
- **Decision.** The reviewer approves, rejects, disputes or asks for information. Only one
  approve, reject or dispute is allowed per request. A reason is required for everything except
  an approval by a landlord or tenant. Every decision carries an idempotency key, so a double
  click cannot decide twice.
- **Status.** Draft, waiting for reviewer, pending review, under review, needs information,
  approved, rejected, disputed, cancelled, stale. Every move writes a `review_status_history`
  row. When a super admin acts for someone, the admin is the actor and the person goes in
  `on_behalf_of`.
- **Stale.** If the target changed after the submission was written (row version differs), the
  request goes stale and must be resubmitted. Same idea as the rent change approval today.
- **Applying.** An approved request changes the real record and writes `business_change_history`
  with before and after values. Nothing changes before approval.
- **Disputes.** A disputed request opens a dispute that goes to an admin. The admin approves,
  rejects, or records a settlement, which can produce a new condition or document version.
- **Removals.** A data removal request lists targets. An admin approves it, which hides the
  records and files and their descendants. Nothing is deleted.
- **Notifications.** Each status move notifies the other side or the admin queue, through the
  existing `notifications` inbox.
- **Permissions (seeded):** `reviews.view` (everyone), `reviews.submit`, `reviews.decide`,
  `reviews.escalate`, `reviews.request_removal` (parties), `reviews.admin_review`,
  `reviews.review_removal` (admins).

## Build order

Each phase ships on its own, with tests and a browser walkthrough, and updates this document.

1. **Engine core.** Targets, create and submit a request, decide, status history, stale check,
   notifications. No UI; covered by tests. First user: unit conditions.
2. **Condition corrections (first screens).** A tenant questions a landlord's condition note,
   the landlord answers; a landlord corrects a locked note. Landlord and tenant screens.
3. **Admin queue and disputes.** Admin list of requests waiting on an admin, escalate,
   resolve, super admin acting with `on_behalf_of`. Admin screens.
4. **Data removal.** Request, admin decision, hiding.
5. **Move existing flows onto the engine.** Maintenance closure and rent change approval were
   built without it. Decide whether to move them or leave them (see Open questions).
6. **Documents.** Confirmation and contract changes, once documents have an API.

## Source locations

Existing:

- Back end: `back-end/reviews/models/` (`requests.py`, `targets.py`, `disputes.py`,
  `removals.py`), `back-end/history/models.py` (`BusinessChangeHistory`),
  `back-end/accounts/seeds/permissions.py` (the `reviews.*` codes)

To add:

- Back end: `back-end/reviews/` services (one use case per file), resources, views, urls, tests
- Admin: `admin/` landlord and tenant review panels, and an admin queue

## Open questions

1. **Scope of the first release.** Condition corrections (phase 2) is the smallest useful
   screen. Is that the right first user?
2. **Existing flows.** Move maintenance closure and rent change approval onto the engine, or
   leave them as they are? Moving makes one history and one inbox, but changes working,
   walked-through behaviour.
3. **Admin review of party changes.** Which kinds go to an admin by default, rather than the
   opposite side?
4. **Expiry.** Does a request waiting on the other side expire? Rent change proposals already do.
5. **Evidence files.** Reuse `files` uploads as maintenance does?

## Not done

Everything above. Also outside this feature: documents have no API, `business_change_history`
is not written for property and unit edits, and reviews of providers are not planned.
