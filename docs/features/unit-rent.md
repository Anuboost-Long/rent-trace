# Unit rent

## Status — 12 November 2026

Built. Migration `0004_unit_rent` applies (every test database is built from the migrations)
and its tests pass in the full back-end run of 12 November 2026 (444 tests). The rent fields
have not been checked on screen in a browser.

## Goal

A landlord or admin sets what a unit costs and how often it is paid, so
listings can show and filter by rent.

## How it works

- A unit has an optional `rent_amount` (decimal, up to 10 digits, 2 places)
  and `rent_frequency` (`WEEKLY`, `FORTNIGHTLY`, `MONTHLY`).
- The two go together: set both or neither. Amount without a frequency fails
  with "Choose how often the rent is paid."; frequency without an amount fails
  with "Enter the rent amount."
- The database enforces the same rules: amount must be above zero, frequency
  must be one of the three, and the pair must be both set or both empty.
- The unit form in the admin app has the rent fields; `admin/utils/rent.ts`
  formats them.

## Source locations

- `back-end/properties/migrations/0004_unit_rent.py`: columns and constraints.
- `back-end/properties/models.py`: `PropertyUnit` fields.
- `back-end/properties/services/shared/rent.py`: `check_rent`.
- `back-end/properties/services/create_unit.py`, `update_unit.py`: use `check_rent`.
- `back-end/properties/dtos/unit_fields.py`, `resources/unit.py`: request and response.
- `admin/components/properties/unit-form.tsx`, `unit-panel.tsx`, `units-section.tsx`.
- `admin/utils/rent.ts`.
- `back-end/properties/tests/test_unit_rent_and_listing_api.py`.

## Not done

- Check the rent fields on the unit screens in a browser.
