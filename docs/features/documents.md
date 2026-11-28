# Documents

## Status — 28 November 2026

API built, no screens. The first 21 tests covered publish, adding a version, confirm or flag, listing
and opening files. Added on 28 November 2026: expiry and escalation (19 tests) and tenant uploads
(11 tests). The full back-end suite passes (918); ruff, the migration check and OpenAPI validation are
clean. Notification kinds `DOCUMENT_ESCALATED`, `DOCUMENT_SENT_TO_ADMIN` and `DOCUMENT_DECIDED` need
`notifications/0015` and `accounts/0016` applied (`manage.py migrate`). The screens come later.

## Goal

Landlords keep the papers of a tenancy in one place: the tenancy agreement and other contracts,
condition reports, notices, and receipts for repairs. Tenants see the papers on their tenancy, and
confirm the ones that need their consent.

## How it works

Decided 27 November 2026.

- **A document is a record about a file.** The bytes live in `files` (PDF, JPEG or PNG, up to 10 MB,
  type checked from the contents). A `documents` row has a type, belongs to a unit and optionally a
  tenancy or a maintenance issue, and keeps numbered `document_versions` so an earlier wording is never
  lost. This does not replace the loose PDFs a property already holds as `DOCUMENT` files; those stay
  as they are.
- **Types:** `TENANCY_AGREEMENT` (the contract), `CONDITION_REPORT`, `NOTICE`, `RECEIPT`, `OTHER`.
- **Receipts** are documents linked to a maintenance issue (a nullable `maintenance_issue` on
  `documents`). The issue must be on the same unit.
- **Who does what** (permissions already seeded): a landlord who owns the property **publishes** and
  adds versions (`documents.publish`); a tenant of the tenancy **views** and **confirms or flags**
  (`documents.confirm`); anyone can view what they are allowed to see (`documents.view`). Tenants do
  upload only the papers listed below (`documents.upload`, added 28 November 2026).
- **Needs both sides' consent:** tenancy agreements and other contracts. Publishing a version of one
  creates a `DOCUMENT_CONFIRMATION` review request for the tenants; one current tenant of the tenancy
  confirms it or flags it with a reason (the engine's "one eligible opposite-side party" rule). A
  confirmed version becomes the document's `current_version`. A flagged version stays unconfirmed and
  the landlord publishes a corrected version. A tenancy agreement must name a tenancy.
- **No consent needed:** condition reports, notices, receipts and other papers. The new version is
  current at once and the tenants are told.
- **Tenant uploads** (added 28 November 2026): a current tenant can upload a `NOTICE`, `RECEIPT` or
  `OTHER` paper on their tenancy (`documents.upload`, migration `accounts/0016`), optionally linked to a
  maintenance issue on the same tenancy. It is current at once and needs no consent; the owners are told
  (`DOCUMENT_ADDED`, the tenants are not). Tenancy agreements and condition reports stay landlord-only
  because they need consent. A tenant cannot add a new version to a paper afterwards.
  `POST /api/tenant/tenancies/<id>/documents/` (multipart: `document_type`, `title`, `description`,
  `document_date`, `maintenance_issue_id`, `file`). Housemates, the landlord and admins see it like any
  other document.
- **Seeing them:** a landlord sees every document on their units; a tenant sees the documents on their
  own tenancy (including all versions, so they can confirm a pending one). Admins can read any
  document. Anyone else gets a 404.

## API

- Landlord (`documents.publish` to write, `documents.view` to read): `POST /api/landlord/documents/`
  (multipart: `unit_id`, `document_type`, `title`, optional `description`, `document_date`, `tenancy_id`,
  `maintenance_issue_id`, and the `file`), `GET /api/landlord/documents/?unit_id=`,
  `GET .../<id>/`, `POST .../<id>/versions/` (multipart: `title`, `file`, ...), and
  `GET .../files/<file_id>/` to download.
- Tenant (`documents.view`; `documents.confirm` for the answer): `GET /api/tenant/tenancies/<id>/documents/`,
  `GET .../<document_id>/`, `GET .../files/<file_id>/`, and
  `POST .../versions/<version_id>/confirm/` or `.../flag/` (an `idempotency_key`; flagging also needs a
  `reason`).
- Admin (`documents.admin_view`, a new admin-only permission, seeded by `accounts/0014`):
  `GET /api/admin/documents/?unit_id=`, `GET .../<id>/`, `GET .../files/<file_id>/`.
- Each version shows `confirmation`: null (no consent needed), `WAITING`, `CONFIRMED`, `FLAGGED`,
  `EXPIRED`, `ESCALATED` or `SUPERSEDED` (a newer version replaced it before it was answered), plus the
  `flag_reason`.
- **Expiry** (added 28 November 2026): a version nobody answered for 14 days reads `EXPIRED`. It is worked
  out when read, like condition reports; nothing is stored or scheduled, and nobody is told. An expired
  version can no longer be confirmed or flagged. The landlord publishes it again as a new version.
- **Escalation** (added 28 November 2026): when a version is `FLAGGED` or `EXPIRED`, the tenant or the
  landlord can press a button to ask an admin to decide, with a required reason
  (`reviews.escalate`, which both roles already hold). Only the newest version can be sent, and only
  once. The version then reads `ESCALATED`, and the admins who hold `reviews.admin_review` get a
  notification (`DOCUMENT_ESCALATED`) and the other side gets `DOCUMENT_SENT_TO_ADMIN`. The admin
  **confirms** it (it becomes the current version, written to `business_change_history` as
  `ADMIN_CONFIRM_DOCUMENT_VERSION`) or **upholds the flag** (nothing becomes current, and it cannot be
  sent again). Both need a reason. Everyone on the tenancy and the owners get `DOCUMENT_DECIDED`.
  Publishing a newer version closes an open case. The case is a `DISPUTE` request on the admin route,
  kept apart from condition cases: `admin_cases()` now returns condition cases only, so the existing
  Review cases queue is unchanged.
- Routes: tenant `POST /api/tenant/tenancies/<id>/documents/versions/<version_id>/escalate/`; landlord
  `POST /api/landlord/documents/<id>/versions/<version_id>/escalate/` (both `{reason}`); admin
  `GET /api/admin/documents/cases/?status=` (default waiting; paged) and
  `POST /api/admin/documents/cases/<case_id>/approve/` or `/reject/` (`{idempotency_key, reason}`),
  all under `reviews.admin_review`.
- Notification kinds `DOCUMENT_ADDED`, `DOCUMENT_CONFIRMATION_REQUESTED` and
  `DOCUMENT_CONFIRMATION_ANSWERED` (migration `notifications/0014`) link to the tenancy.

## Source locations

- Back end: `back-end/documents/` (`services/` one use case per file, `views.py`, `file_views.py`,
  `landlord_urls.py`, `tenant_urls.py`, `admin_urls.py`, `tests/`); migration `documents/0003`
  (maintenance link). Confirmation uses the review engine (`DOCUMENT_CONFIRMATION` requests; see
  [Reviews](reviews.md)).
- Admin app: none yet.

## Not done

No screens. Also: a tenant adding a version to their own paper, and every screen. A super admin deciding a document case is the
same as any admin; nobody acts for a party on documents yet.
