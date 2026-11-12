# Listing status

## Status — 12 November 2026

Built. Its tests (`test_unit_rent_and_listing_api.py`) pass in the full back-end run of
12 November 2026 (444 tests). The status control on the property page has not been
walked through in a browser.

## Goal

A landlord controls whether their property appears publicly. Admins can lock a
listing.

## How it works

- `PUT/PATCH …/landlord/properties/<id>/listing/` changes a property's
  `listing_status` (`LandlordListingStatusView`).
- **Public** statuses are `AVAILABLE` and `PARTIALLY_AVAILABLE`. To set one, the
  property must be `ACTIVE` ("Only active properties can be listed.") and have
  at least one public, non-deleted unit ("Make at least one unit public before
  listing the property.").
- `SUSPENDED` and `ARCHIVED` are admin-only. A landlord cannot set them
  ("Only an admin can set this status."), and cannot change a listing an admin
  has set to either ("An admin has locked this listing. Contact support to
  change it.").
- Admins use `POST /api/properties/<id>/listing/` (needs `properties.admin_manage`, any
  property). They skip the landlord checks (a landlord can't set `SUSPENDED` or `ARCHIVED`, or
  undo an admin's lock) but not the listing checks (an active property with a public unit).
  The landlord copy is `PUT/PATCH …/landlord/properties/<id>/listing/`.
- The change runs in one transaction on the locked row and is recorded through
  `save_changes`, so the actor is kept in history.
- The property page has a listing section with a status control
  (`useListingStatus`).

## Source locations

- `back-end/properties/services/change_listing_status.py`.
- `back-end/properties/dtos/change_listing.py`.
- `back-end/properties/landlord_views.py`, `landlord_urls.py`; `back-end/properties/file_views.py`
  (`ListingStatusView`, the admin one) and `urls.py`.
- `admin/components/properties/listing-section.tsx`, `property-detail.tsx`.
- `admin/hooks/form/useListingStatus.ts`.
- `admin/api/services/properties/serve-action.ts`.

## Not done

- Walk through the status control in a browser, as a landlord and as an admin.
