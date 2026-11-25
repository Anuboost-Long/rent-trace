# Reviews

## Status — 25 November 2026

Slice 1 (tenant condition evidence) is built, back end and admin screens, on branch `feat/reviews`.
Back end: 13 new tests pass, and so does the full suite (750), with ruff, the migration check and
the OpenAPI validation. Admin: typecheck and lint pass. Walked through in Chrome on 25 November
2026 with the `+housemate` tenant and `+landlord` accounts on tenancy 6: the tenant sent a
report and saw it waiting; the landlord saw it, rejected it with a reason (the report showed
"Rejected" with the reason, the request went to `DISPUTED`, and a linked dispute case and both
notifications were written); a second report was approved from the screen. Also seen: the tenant's
view of approved, rejected (with the reason) and withdrawn reports together; Withdraw; both
inbox notifications, and the rejection one opening the tenant tenancy page; the list and the
report form at 390px wide with no sideways scroll. The Next.js dev overlay shows one
"Blocking Route" warning (`Date.now()` while prerendering). It appears on every signed-in page,
not just notifications (the stack points at the shared `SiteHeader`, and nothing in the project
calls `Date.now()` there). `next build` passes with no such warning, so it is a dev-mode
check and not from this feature. The landlord's notification link
(to the landlord tenancy page) was not clicked. Everything beyond slice 1 is still planned.

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

## First slice — tenant condition evidence

Reading spec v3 (`RentTrace_Database_Structure_and_Processes_v3.md`, §6 "Review routing and
lifecycle") changed the first slice. A landlord's accepted condition note is locked, and only an
admin can correct it. So the first slice is not "a tenant corrects a landlord's note". It is the
route the spec gives to **new evidence**:

1. A tenant of a unit adds their own condition account (a `DISCREPANCY` record, source
   `TENANT`: title, description, date observed). It starts `PENDING_REVIEW`.
2. One current owner of the property approves or rejects it. This is the "one eligible
   opposite-side party" rule. Approving sets the record's accepted version. Rejecting needs a
   reason and marks the request `DISPUTED`.
3. The tenant can cancel it while it is pending.
4. Only a current tenant of that unit can add one; only a current owner can answer. Anyone else
   gets a 404.

Statuses used: `PENDING_REVIEW`, `APPROVED`, `DISPUTED`, `CANCELLED`. Not in this slice:
`NEEDS_INFORMATION`, the admin route, `STALE`, attachments, settling or escalating a dispute.

Assumptions (the spec does not say; change them if wrong):

- A rejection creates the linked dispute case the spec requires (`disputes` row plus a `DISPUTE`
  request, opposite-side route, status `PENDING_REVIEW`, parent = the rejected request). Nothing
  can act on that dispute yet.
- A pending account is invisible to everyone but its author and the owners. An approved one is
  not shown to other tenants unless the landlord later chooses to.
- Retrying the same decision (same idempotency key) returns the original result.

## Expiry

Decided 26 November 2026. A tenant's condition report that nobody has answered after **14 days**
shows as `EXPIRED`. Like rent change proposals, it is worked out when read: the stored status
stays `PENDING_REVIEW` and nothing runs on a schedule. An expired report cannot be approved,
rejected or withdrawn (400, "This report expired after 14 days. The tenant can send a new one."),
and the tenant sends a new report. Nobody is notified when it expires. Built and tested (15 tests
in `reviews`); the admin screens show "Expired" and hide the buttons, not yet seen in a browser.

## Escalation and the admin queue — phase 2a

Decided 26 November 2026; built 26 November 2026 (back end tested, admin screens typecheck and lint
clean, **not yet seen in a browser**). Escalation is manual: a person presses **Ask an admin to
decide**, which calls an API. Nothing escalates on a timer.

Rules:

- **What can be escalated:** a rejected report (`DISPUTED`) or an expired one. Pending, approved,
  withdrawn and already-escalated reports are refused (400).
- **Reason:** required every time (a blank or whitespace-only reason is a 400).
- **Who:** the report's author, or a current owner of the property. Anyone else gets a 404.
  Permission `reviews.escalate`.
- **What happens:** the report's dispute case moves to the Admin route. A rejected report already
  has its dispute case, so it is re-routed. An expired report has none, so escalating creates it
  and moves the report to `DISPUTED`. Each step writes a status history row with the reason.
- **Admin queue:** admins holding `reviews.admin_review` see Admin-routed dispute cases waiting for a
  decision, oldest first, with the report, the landlord's rejection reason (if any) and the
  escalation reason.
- **Admin decision:** approve or reject, with a reason in both cases. The decision sits on the
  dispute case. Approve makes the tenant's account the accepted version and writes
  `business_change_history`; reject leaves the record as it was. Either way a
  `dispute_resolutions` row records the outcome (`ADMIN_APPROVED` / `ADMIN_REJECTED`). A case can be
  decided once; a retry with the same idempotency key returns the same result.
- **Who is told (assumption):** admins who can decide when a case is escalated; the tenant and the
  landlord when an admin decides.

Assumptions to change if wrong: `DisputeResolution.resolution_request` points at the dispute case
itself; the escalation reason lives in the status history row, not in a new column.

Endpoints (built):

- Parties: `POST /api/tenant/tenancies/<id>/condition-evidence/<request_id>/escalate/` and
  `POST /api/landlord/condition-evidence/<request_id>/escalate/` (body `reason`).
- Admin: `GET /api/admin/review-cases/` (paged) and
  `POST /api/admin/review-cases/<id>/approve/` and `.../reject/` (body `reason`, `idempotency_key`).
  Permission `reviews.admin_review`. Regular admins can decide, not only super admins.

Acceptance: either party escalates a rejected report; the tenant escalates an expired one; blank
reasons, pending, approved, withdrawn and repeat escalations are refused; strangers get 404; an admin
without the permission is refused; admin approve and reject work once; the right people are
notified. Admin screens: a Review cases list in the admin area (Waiting / Approved / Rejected filters, approve
and reject with a reason), plus an "Ask an admin to decide" button on the tenant and landlord
screens. The report shows "With an admin" until decided, then "Approved by an admin" or "Rejected by
an admin" with the admin's reason.

Source: `back-end/reviews/services/escalate_evidence.py`, `approve_dispute.py`, `reject_dispute.py`,
`list_review_cases.py`, `services/shared/{cases,disputes,acceptance,admins}.py`, `admin_views.py`;
admin `components/reviews/`, `components/conditions/escalate-dialog.tsx`,
`app/(app)/admin/review-cases/`. Tests: `test_escalate_evidence.py`, `test_approve_dispute.py`,
`test_reject_dispute.py`, `test_list_review_cases.py`.

Not in 2a: `NEEDS_INFORMATION`, locked corrections, a super admin acting with `on_behalf_of`,
settlements.

## Build order

Each phase ships on its own, with tests and a browser walkthrough, and updates this document.

1. **Tenant condition evidence** (the slice above): back end, then tenant and landlord screens.
2. **Disputes and the admin queue.** 2a (above) ships first; the rest follows: settle the disputes slice 1 creates, locked
   corrections, `NEEDS_INFORMATION`, admin screens, a super admin acting with `on_behalf_of`.
3. **Data removal.**
4. **Move existing flows onto the engine** only if wanted (maintenance closure, rent change).
5. **Documents.**

## Source locations

Shipped (slice 1):

- API, tenant: `GET/POST /api/tenant/tenancies/<id>/condition-evidence/` (list yours, add one),
  `POST .../<request_id>/cancel/`. Permissions `reviews.view`, `reviews.submit`.
- API, landlord: `GET /api/landlord/condition-evidence/?unit_id=`,
  `POST .../<request_id>/approve/` and `.../reject/` (a reason and an `idempotency_key`, a fresh
  UUID per click). Permissions `reviews.view`, `reviews.decide`.
- Back end: `back-end/reviews/` (`services/` one use case per file, `tenant_views.py`,
  `landlord_views.py`, `tests/test_condition_evidence.py`); three new notification kinds
  (`CONDITION_EVIDENCE_SUBMITTED/APPROVED/REJECTED`, migration `notifications/0009`).

Existing:

- Back end: `back-end/reviews/models/` (`requests.py`, `targets.py`, `disputes.py`,
  `removals.py`), `back-end/history/models.py` (`BusinessChangeHistory`),
  `back-end/accounts/seeds/permissions.py` (the `reviews.*` codes)

- Admin: tenant "Conditions you reported" section (`admin/components/conditions/tenant-evidence.tsx`,
  `evidence-dialog.tsx`) on the tenant tenancy page; landlord "Conditions reported by tenants"
  (`landlord-evidence.tsx`) on the landlord tenancy page; `hooks/form/useEvidenceActions.ts`,
  `api/services/evidence/`; the three notification kinds link to the tenancy page. Notification
  `subject_id` is the tenancy id.

## Open questions

1. **Existing flows.** Move maintenance closure and rent change approval onto the engine, or
   leave them as they are? Moving makes one history and one inbox, but changes working,
   walked-through behaviour.
2. **Admin review of party changes.** Which kinds go to an admin by default, rather than the
   opposite side?
3. ~~**Expiry.**~~ Decided 26 Nov 2026: a request waiting on the other side expires after 14 days, as
   rent change proposals do. See "Expiry" above.
4. **Evidence files.** Reuse `files` uploads as maintenance does?

## Not done

Everything above. Also outside this feature: documents have no API, `business_change_history`
is not written for property and unit edits, and reviews of providers are not planned.
