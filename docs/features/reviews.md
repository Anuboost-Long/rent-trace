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

Decided 26 November 2026; built 26 November 2026. Back end: 772 tests pass in the full suite. Walked through in Chrome the
same day with a throwaway test admin (`test.admin@renttrace.test`, regular admin): the tenant asked
an admin to decide on a rejected report (reason box needs text; the report then read "With an
admin"), the admin saw it in Review cases, approved it with a reason, the Waiting list emptied and
the Approved tab showed it with both reasons; the inbox link opened Review cases; the database held
the accepted version, an `ADMIN_APPROVED` resolution and the notifications. Also seen later the same day: the landlord escalated a rejected report from the screen (it then read "With an admin"), the landlord's tenancy page showed "Approved by an admin" with the admin's reason, and an expired report showed "Expired" with the button. Also seen on 26 Nov 2026: the tenant escalated an expired report (reason required; it then read "With an admin"); the admin queue showed "Never answered" for it and named the landlord as the asker on the other case; the admin rejected a case with a reason (it moved to Rejected, the report was rejected, the record kept no accepted version, an `ADMIN_REJECTED` resolution was recorded). **Not seen:** the tenant's and landlord's screens after an admin _rejection_, and narrow screens (the browser window would not resize). Escalation is manual: a person presses **Ask an admin to
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

## Evidence photos

Decided 26 November 2026; built 26 November 2026. A tenant can attach up to 5 photos (JPEG or PNG, up to 10 MB
each) to a condition report while it is waiting for an answer. The landlord who answers it and an
admin who decides an escalated case can open them; nobody else can (404).

- **Adding:** `POST /api/tenant/tenancies/<id>/condition-evidence/<request_id>/photos/` (multipart,
  one `file`), permission `reviews.submit`. Only the report's author, only while it is waiting and
  not expired. A sixth photo, a non-image or an oversized file is a 400. After the report is answered,
  withdrawn or expired, photos cannot be added.
- **Viewing:** `GET .../condition-evidence/photos/<file_id>/` for the author (tenant), the landlord
  owner (`/api/landlord/condition-evidence/photos/<file_id>/`) and an admin
  (`/api/admin/review-cases/photos/<file_id>/`, `reviews.admin_review`).
- **Stored as:** a `files` row plus a `review_submission_files` link to the report's current
  submission (the table already existed). The report and case responses list each photo's `id` and
  `name`.
- **Screens:** the tenant's report form takes photos; thumbnails show on the tenant's list, the
  landlord's list and the admin's Review cases. A photo opens full size in a new tab.
- **Seen in Chrome (production build):** the tenant's report listing two thumbnails that load through
  the app's proxy, the report form with its Photos picker and limit hint, and the same photos on the
  admin's Review cases. **Not seen:** choosing files in the browser's file chooser and uploading them
  from the form (the photos were added through the service layer), the landlord's list with photos,
  and phone width. Back end: 42 `reviews` tests pass (7 new in `test_evidence_photos.py`).
- **Not in this slice:** removing a photo (withdraw and send a new report instead), PDFs, and photos
  on anything but condition reports.

## Asking for more information — API built 27 November 2026

Back end only for now: 56 `reviews` tests pass (14 new in `test_request_information.py` and
`test_respond_to_information.py`). The screens come later; the tenant and landlord lists still treat
`NEEDS_INFORMATION` as an unknown status until they are built. Instead of approving or rejecting at
once, the landlord can ask the tenant for more, and the tenant answers.

- **Ask:** `POST /api/landlord/condition-evidence/<id>/request-information/` with a `reason` and an
  `idempotency_key` (permission `reviews.decide`). Only while the report is waiting (not expired). The
  report moves to `NEEDS_INFORMATION`, a `REQUEST_INFORMATION` decision is recorded, and the tenant is
  told. Landlords can ask more than once.
- **Answer:** `POST /api/tenant/tenancies/<id>/condition-evidence/<request_id>/respond/` with a
  required `message` and optional `title`, `description` and `observed_at` changes (permission
  `reviews.submit`). Only while `NEEDS_INFORMATION`. It adds a new numbered submission and a new
  condition version that supersedes the old one; photos carry over, and the tenant can add more
  photos first. The report returns to `PENDING_REVIEW` with a fresh 14-day window, and the owners
  are told. Old submissions are never edited.
- **Meanwhile:** the landlord cannot approve, reject or escalate it (400, "Waiting for the tenant's
  reply."). The tenant can withdraw it or add photos. It does not expire while it waits for the tenant
  (assumption: the tenant can always withdraw).
- **Responses** gain `revision_no` and `information_request` (the landlord's latest question, or
  null). The status shows as `NEEDS_INFORMATION`.
- **Notifications:** `CONDITION_EVIDENCE_INFO_REQUESTED` (tenant) and `CONDITION_EVIDENCE_INFO_PROVIDED`
  (owners), migration `notifications/0011`; both link to the tenancy.

## Locked corrections — API built 27 November 2026

Back end only for now: 73 `reviews` tests pass (17 new, in `test_request_correction.py`,
`test_decide_correction.py` and `test_list_corrections.py`). No screens yet. A note people rely on is not changed by one side alone: either side asks an
admin to correct it, and the admin decides.

- **What can be corrected** (assumption, change if wrong): a _shown_ landlord note on the tenant's own
  unit (the tenant asks), and an _approved_ tenant condition report on a property the landlord owns
  (the landlord asks). Landlords still edit their own baseline notes directly through
  `/api/landlord/conditions/`; that behaviour is unchanged.
- **Ask:** `POST /api/tenant/tenancies/<id>/condition-corrections/` (tenant) or
  `POST /api/landlord/condition-corrections/` (landlord), body `record_id`, `what_is_incorrect`,
  `proposed_replacement` (the new description), `why_change_needed`, optional `title`. Permission
  `reviews.submit`. It creates a `LOCKED_CORRECTION` request on the Admin route, waiting for a
  decision. Only one correction can wait per note (400). Nothing about the note changes yet; the
  proposed wording is kept in the submission, not as a condition version, so the landlord can still edit
  meanwhile.
- **List and withdraw:** `GET .../condition-corrections/` (tenant: their tenancy's; landlord:
  `?unit_id=`), `POST .../<id>/cancel/` by whoever asked, while it is waiting. `reviews.view` and
  `reviews.submit`.
- **Admin:** `GET /api/admin/condition-corrections/?status=` (paged, default waiting) and
  `POST .../<id>/approve/` or `.../reject/` with a `reason` (required both ways) and an
  `idempotency_key`; permission `reviews.admin_review`. Approving writes a new condition version that
  supersedes the accepted one, makes it the accepted version and writes `business_change_history` with the
  old and new version numbers. Rejecting changes nothing.
- **Stale:** if the note changed after the request was written (row version differs), deciding marks the
  request `STALE` instead of applying it, and the requester must ask again.
- **Told:** admins who can decide when one is asked; the requester and the property's owners when it is
  decided. Notification kinds `CONDITION_CORRECTION_REQUESTED` and `CONDITION_CORRECTION_DECIDED`
  (migration `notifications/0012`).

## A super admin acting for someone — API built 27 November 2026

Back end only for now: 80 `reviews` tests pass (7 new, in `test_super_admin_acts.py`). No screens. A super admin (`is_top_level_admin`) can do a party's action on a condition
report. The records show the super admin as the actor, and the person they acted for goes in
`on_behalf_of` (the rule in the project notes: only on `review_status_history` and
`business_change_history`, and never the same person as the actor).

- **Endpoints** (super admin only, plus the permission the action needs):
  `GET /api/admin/condition-evidence/?unit_id=` (any admin with `reviews.admin_review`), and
  `POST /api/admin/condition-evidence/<id>/` followed by `approve`, `reject` or `request-information`
  (acting as the property's **primary owner**; body as for the landlord), and `cancel` or `respond`
  (acting as the report's **author**; body as for the tenant).
- **Recorded as:** the admin is `reviewer` on the decision (side `LANDLORD`) and `actor` on the status
  history; `on_behalf_of` is the primary owner or the author. Approving also sets `on_behalf_of` on
  the change history. A regular admin gets 403.
- **Same rules apply:** an expired, answered or withdrawn report is refused the same way; retrying an
  answer with the same `idempotency_key` changes nothing.
- **Not covered:** escalating for a party (a super admin can already decide the case in Review cases),
  adding photos for a tenant, and submitting a report for a tenant.

## Data removal — API built 27 November 2026

Back end only for now: 96 `reviews` tests pass (16 new, in `test_request_removal.py`,
`test_decide_removal.py` and `test_list_removals.py`). No screens. Nothing is deleted: an approved removal **hides** records and files.

- **What can be removed (first version):** condition records. A tenant can ask to remove their **own**
  condition reports; a landlord can ask to remove any condition record on a property they own.
  Hiding a record also hides records related to it and the photos attached to its submissions
  (`include_descendants`, on by default). Other targets (properties, units, maintenance issues,
  documents) are for later.
- **Ask:** `POST /api/tenant/tenancies/<id>/removal-requests/` or `POST /api/landlord/removal-requests/`,
  body `record_ids` (1 to 20), `reason`, optional `include_descendants`; permission
  `reviews.request_removal`. It creates a `DATA_REMOVAL` request on the Admin route with one
  `removal_request_items` row per record. A record with a waiting removal cannot be asked again (400);
  records you cannot remove are a 404.
- **List and withdraw:** `GET` on both (tenant by tenancy, landlord `?unit_id=`), `POST .../<id>/cancel/`
  by whoever asked while it is waiting.
- **Admin:** `GET /api/admin/removal-requests/?status=` (paged) and `POST .../<id>/approve/` or
  `.../reject/` with a required `reason` and an `idempotency_key`; permission `reviews.review_removal`.
  Approving sets `deleted_at` and `deleted_by` on each record and its descendants and writes
  `removal_effects` rows (`HIDE_RECORD`, `HIDE_DESCENDANTS`, `HIDE_FILE`) and change history. Hidden
  records disappear from reports, lists and photo downloads (404). Rejecting changes nothing.
- **Told:** admins who can decide when one is asked; the asker and the owners when it is decided
  (kinds `DATA_REMOVAL_REQUESTED`, `DATA_REMOVAL_DECIDED`; migration `notifications/0013`).

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
4. ~~**Evidence files.**~~ Decided 26 Nov 2026: photos on condition reports; see "Evidence photos".

## Removal requests screen — built 28 November 2026

Admin screen at `/admin/removal-requests` (nav item "Removal requests", permission
`reviews.review_removal`), following design A6 in the Figma export: filter chips (Pending, Approved,
Rejected), a table, and a detail page with the records, reason, effect and a Decision card (**Approve and
hide** or **Reject**, reason required). Added `GET /api/admin/removal-requests/<id>/` for the detail page
(1 new test). Typecheck, lint and the production build pass. **Not yet seen in a browser** (needs a signed-in
admin). Left out because the API has no matching action: the design's "New removal request" (an admin
recording a request for someone) and "Restore records", and the chip counts and photo thumbnails (items
carry only a record id and title). Parties ask for removal from their own screens, which are not built yet.

## Corrections screen — built 28 November 2026

Admin screen at `/admin/corrections` (nav item "Corrections", permission `reviews.admin_review`), following
the dispute-case design A3: filter chips (Waiting, Approved, Rejected), a table, and a detail page with
what the party says (what is incorrect, the proposed replacement, why), a Before and after comparison and a
Decision card (**Approve correction** or **Reject**, reason required). Added
`GET /api/admin/condition-corrections/<id>/` for the detail page (1 new test). Typecheck, lint and the
production build pass; **not yet seen in a browser**. Left out because the API has no matching action:
"Request more information" on a correction, the Parties list, photo proof and "Add on behalf of a party".

## Not done

The screens for everything built after the first slice (asking for information, corrections, removal,
the super admin acting for someone). Reviews of providers are not planned. Documents are in
[Documents](documents.md).
