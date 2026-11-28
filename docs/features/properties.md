# Properties, units, photos and files

## Status — 15 November 2026

Shipped 11 November 2026 (back end and admin screens). Unit rent and listing
status were added afterwards: see [Unit rent](unit-rent.md) and
[Listing status](listing-status.md). Not re-verified when this was written.

Admin property and unit detail/edit screens walked through in Chrome on
15 November 2026 as the regular admin: both render and match the data. At that point the unit
edit form had no field for occupancy at all — occupancy was entirely a side effect of
starting/ending a tenancy ([Tenancy lifecycle](tenancy-lifecycle.md)).

Done 15 November 2026: a manual occupancy control (`VACANT`, `PARTIALLY_OCCUPIED`,
`UNAVAILABLE`) for the unit, requested so a landlord or admin can take a unit off the market
(maintenance, renovation) or mark part of it taken without an `AREA_BASED` tenancy (none exist
yet — `tenancy_type` is hardcoded to `WHOLE_UNIT`, see
[Tenancy lifecycle](tenancy-lifecycle.md)). `OCCUPIED` is never an input — it only ever comes from
an active tenancy. The change is refused while the unit has an `ACTIVE` tenancy (see
[Tenancy lifecycle](tenancy-lifecycle.md) for the exact rule and its one known gap). Verified live
in Chrome as a landlord: a vacant test unit took "Unavailable" and kept it after reload; the
existing occupied unit showed "Set automatically while this unit has a current tenant." and no
control, as intended. The admin side uses the same service and permission pattern as every other
unit edit, so it was not separately walked through in the browser.
`PARTIALLY_OCCUPIED` stays in `AVAILABLE_OCCUPANCY`
(`back-end/listings/services/shared/queries.py`), so a unit set to it keeps showing in public
listings and stays contactable — a deliberate choice, not a side effect.

## Goal

Admins and landlords manage properties and their units, with photos and PDF
documents.

## How it works

- **Two audiences.** Admins (`/api/properties/`, `/admin/properties`) read with
  `properties.admin_view` and change with `properties.admin_manage`. Landlords
  (`/api/landlord/properties/`, `/landlord/properties`) only see properties they
  currently own, as primary or co-owner; anyone else's property answers 404.
  Reading needs `properties.view`, creating `properties.create`.
- **Create:** an admin picks an active landlord as owner (`owner-options/`); a
  landlord becomes the owner themselves. The owner is the primary owner with 100%.
  `property_type` comes from `properties/catalogue.py`. The address uses the
  [locations lookup](locations.md).
- **Edit:** any field and `property_status`; only fields sent change. The owner
  can't change here.
- **Remove:** admins soft-delete a property and its units (409 while a unit has
  a tenancy). Landlords archive (`ARCHIVED`) instead; they can't delete.
- **Units:** add, edit, remove (409 while it has a tenancy). A unit has a name,
  type, optional number and description, and `is_public`.
- **Occupancy** (`POST …/units/<id>/occupancy/`, separate from the unit edit endpoint, same
  pattern as the listing-status action): sets `occupancy_status` to `VACANT`,
  `PARTIALLY_OCCUPIED` or `UNAVAILABLE`. 400 if the unit has an `ACTIVE` tenancy — occupancy for
  a tenanted unit is only ever set automatically ([Tenancy lifecycle](tenancy-lifecycle.md)).
  Same permissions as editing the unit (`properties.update` for a landlord's own unit,
  `properties.admin_manage` for an admin).
- **Photos and files:** upload one file at a time, `PHOTO` (JPEG or PNG) or
  `DOCUMENT` (PDF), up to 10 MB, type checked from the contents. Edit the
  caption, make a photo the cover, delete (marked deleted; the next photo becomes
  cover). A file belongs to the property or one unit, never both. File bytes are
  fetched on the server by the admin app (`app/property-files/`).
- Changes are stamped with `created_by`, `updated_by` and `row_version`. They are
  not written to `business_change_history` yet.

## Source locations

- `back-end/properties/`: `views.py`, `landlord_views.py`, `file_views.py`,
  `models.py`, `services/`, `catalogue.py`.
- `back-end/files/`: uploaded file metadata.
- `admin/app/(app)/admin/properties/`, `admin/app/(app)/landlord/properties/`.
- `admin/app/property-files/`: file download route handlers.
- `admin/components/properties/`: list, filter, forms, detail, units, files,
  photo tiles, dropzone.
- `admin/hooks/form/`: `useSaveProperty`, `useDeleteProperty`, `useUnitActions`,
  `usePropertyFiles`, `useStagedFiles`.
- `admin/api/services/properties/serve-action.ts`, `admin/types/properties/models.ts`.

## Not done

- Nothing: `business_change_history` is now written for property, unit, listing and occupancy edits and removals (see Change history below).

## Change history

Added 28 November 2026. Every edit to a property or unit writes one `business_change_history` row on that
record's review target (created the first time): the actions `UPDATE_PROPERTY`, `UPDATE_UNIT`,
`CHANGE_LISTING_STATUS`, `CHANGE_OCCUPANCY`, `DELETE_UNIT` and `DELETE_PROPERTY`. A row holds the
`before_values` and `after_values` of only the fields that changed (decimals and dates as plain JSON),
the person who did it, and a numbered sequence per record. A save that changes nothing writes nothing.
Tenancy edits are recorded the same way (`UPDATE_TENANCY`: dates, notes and any rent or bond change that
applied at once; `APPLY_TERM_CHANGE` when every tenant approves a rise); see
[Tenancy terms](tenancy-terms.md). There is no API to read the history yet. Tests:
`back-end/history/tests/test_business_change_history.py`, helper `back-end/history/recording.py`.
