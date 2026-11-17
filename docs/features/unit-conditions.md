# Unit conditions

## Status — 12 November 2026

Built. Back end: 11 tests (versions, scoping, visibility, tenant view) pass. Admin: type-check and lint pass, and the landlord section was seen working in a browser (add note, shown switch). The tenant list has **not** been seen in a browser yet. Migration `conditions/0003` is applied to the dev database.

## Goal

A landlord writes down what condition a unit is in (for example "Kitchen benchtop: small chip near
the sink") and **chooses which notes tenants can see**. A tenant sees only the notes the landlord
chose to show, on the page of their own tenancy.

## How it works

- A condition note has a title, a description and the date it was checked. It belongs to one unit.
- Each note has a **Shown to tenants** switch. New notes start hidden. Tenants never see hidden notes
  or learn that they exist.
- Editing a note's text keeps the earlier wording: it adds a new version to the existing
  `condition_versions` table (version 1, 2, ...) and the newest version is the one shown.
- Deleting a note hides it everywhere (soft delete).
- **Landlord**: on the unit page, a "Condition" section lists every note with the switch, and adds,
  edits and deletes notes. Only landlords who currently own the property can do this; anyone else
  gets a 404.
- **Tenant**: on the tenancy page, a "Condition of the unit" section lists the shown notes, read only.
  It is shown for the unit of any tenancy the person has joined, past ones included.
- Back-end API (landlord): `/api/landlord/conditions/?unit_id=` (list, create) and
  `/api/landlord/conditions/<id>/` (edit, delete). Tenants get the shown notes inside
  `GET /api/tenant/tenancies/<id>/` as `unit_conditions`.
- Permissions already seeded: `conditions.view`, `conditions.submit_baseline` (landlord). Creating,
  editing, switching and deleting all use `conditions.submit_baseline`.
- Notes are saved as `BASELINE` records, with source `LANDLORD`.

## Source locations

- Back end: `back-end/conditions/` (model field, services, API) and the `unit_conditions` field in
  `back-end/tenancies/resources/my_tenancy_detail.py`
- Admin: `admin/components/conditions/` (landlord section, tenant list), used by the unit page and the
  tenant tenancy page

## Not done

- Photos on a note, rooms or areas (`unit_areas`), a tenant response or dispute, move-in and move-out
  checks, comparing versions on screen, and the admin view.
