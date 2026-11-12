# Tenancy terms: rent, bond and editing

## Status — 12 November 2026

Built. Back end: 20 tests, and the full suite (537) passes (every edit rule by status, rent and bond validation, creating with terms, who is told and that no amounts are in the text, permissions). Admin: type-check, lint and a production build pass. In Chrome as a landlord on 12 November 2026: the Rent and Bond rows and the Edit tenancy button show, and setting rent 450 weekly and bond 1800 on the test tenancy saved and displayed as "$450 per week" and "$1,800"; the tenant was told, with no amounts in the message.

## Goal

A landlord, or an admin on their behalf, sets what the tenants pay and for how long, and can
correct it later. Tenants see the terms on their tenancy page and are told when they change.

## How it works

- A tenancy has **rent** (an amount and how often it is paid: weekly, fortnightly or monthly),
  an optional **bond**, a **start date**, an optional **end date** and private **notes**. Amounts are
  in Australian dollars.
- **Setting them up:** the new-tenancy form takes rent and bond. When the unit has a rent, the form
  fills it in as a starting point and it can be changed; the tenancy keeps its own copy, so later
  changes to the unit's advertised rent don't alter existing tenancies.
- **Editing:** `PATCH /api/tenancies/<id>/` (admin, `tenancies.admin_manage`) and
  `PATCH /api/landlord/tenancies/<id>/` (landlord, `tenancies.update`, own properties only). Any of
  start date, end date, notes, rent amount, rent frequency and bond amount may be sent.
- Rules:
  - Rent needs both an amount and a frequency, or neither. Rent and bond must be more than zero when
    set. Send `null` to clear one.
  - The end date must be after the start date.
  - A `DRAFT` tenancy can change anything. An `ACTIVE` one can change everything except its start
    date (it has already started), its end date must be in the future (to finish it now, use End
    tenancy), and a changed period must not overlap another active tenancy on the same unit.
  - An `ENDED` or `CANCELLED` tenancy can't be edited.
  - Notes are private to the landlord and admins; tenants never see them.
- When the **dates, rent or bond** change and the tenancy has current tenants, they are told in the
  app ("The terms of your tenancy at … changed"). The text carries no amounts. A notes-only change
  tells nobody.
- **Screens:** the landlord and admin tenancy page shows rent and bond and an **Edit tenancy**
  button (for a tenancy that isn't ended or cancelled) that opens a form; the tenant's tenancy
  page already shows rent and bond, or "Not set yet".

## Source locations

- Back end: `back-end/tenancies/services/update_tenancy.py`, `services/shared/terms.py`,
  `dtos/update_tenancy.py`, `dtos/create_tenancy.py`, `views.py`, `landlord_views.py`,
  `resources/tenancy_detail.py`; notification kind in `back-end/notifications/models.py`.
- Admin: `admin/components/tenancies/edit-tenancy.tsx`, `tenancy-terms-fields.tsx`,
  `create-tenancy-form.tsx`, `admin/app/*/tenancies/[id]/edit/`.

## Not done

- A history of who changed the rent and when (the project does not write its change-history table
  yet).
- Rent increases with a notice period, rent payments and bond lodgement records.
- Currencies other than Australian dollars.
