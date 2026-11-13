# Properties, units, photos and files

## Status — 12 November 2026

Shipped 11 November 2026 (back end and admin screens). Unit rent and listing
status were added afterwards: see [Unit rent](unit-rent.md) and
[Listing status](listing-status.md). Not re-verified when this was written.

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

- Writing to `business_change_history`.
