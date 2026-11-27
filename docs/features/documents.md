# Documents

## Status — 27 November 2026

API built, no screens. Back end: 21 tests pass in `documents` (publish, add a version, confirm or flag,
list and open files), and the accounts and notifications suites still pass; ruff, migration check and
OpenAPI validation are clean. The screens come later (the project is working API first).

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
  not upload (assumption; changing it needs a new permission code).
- **Needs both sides' consent:** tenancy agreements and other contracts. Publishing a version of one
  creates a `DOCUMENT_CONFIRMATION` review request for the tenants; one current tenant of the tenancy
  confirms it or flags it with a reason (the engine's "one eligible opposite-side party" rule). A
  confirmed version becomes the document's `current_version`. A flagged version stays unconfirmed and
  the landlord publishes a corrected version. A tenancy agreement must name a tenancy.
- **No consent needed:** condition reports, notices, receipts and other papers. The new version is
  current at once and the tenants are told.
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
- Each version shows `confirmation`: null (no consent needed), `WAITING`, `CONFIRMED`, `FLAGGED` or
  `SUPERSEDED` (a newer version replaced it before it was answered), plus the `flag_reason`.
- Notification kinds `DOCUMENT_ADDED`, `DOCUMENT_CONFIRMATION_REQUESTED` and
  `DOCUMENT_CONFIRMATION_ANSWERED` (migration `notifications/0014`) link to the tenancy.

## Source locations

- Back end: `back-end/documents/` (`services/` one use case per file, `views.py`, `file_views.py`,
  `landlord_urls.py`, `tenant_urls.py`, `admin_urls.py`, `tests/`); migration `documents/0003`
  (maintenance link). Confirmation uses the review engine (`DOCUMENT_CONFIRMATION` requests; see
  [Reviews](reviews.md)).
- Admin app: none yet.

## Not done

No screens. Also: tenants uploading, escalating a flagged document to an admin, expiry of a
confirmation request, and every screen.
