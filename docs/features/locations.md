# Locations lookup

## Status — 12 November 2026

Shipped 11 November 2026. Not re-verified when this was written.

## Goal

Address fields pick an Australian state and suburb instead of free text.

## How it works

- `GET /api/locations/states/` returns the eight states and territories as
  `code` and `name`.
- `GET /api/locations/suburbs/` returns suburbs and postcodes of one state.
  Query: `state` (required), `q` (words in the name; names starting with what was
  typed come first), `limit` (max 100, default 50).
- Needs a signed-in user (admins after two-step verification).
- Data is `locations/data/au_suburbs.csv`, from the community-maintained
  Australian postcodes dataset with PO boxes and large-volume recipients removed.
  The dataset has no stated licence; check before shipping.
- The admin app uses a combobox for suburb search (`combobox-input.tsx`).

## Source locations

- `back-end/locations/`: `catalogue.py`, `data/au_suburbs.csv`.
- `admin/api/services/locations/serve-action.ts`, `admin/constants/locations.ts`,
  `admin/types/locations/models.ts`.
- `admin/components/common/inputs/combobox-input.tsx`.

## Not done

- Confirm the dataset's licence.
