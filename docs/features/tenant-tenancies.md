# Tenant tenancies and rental history

## Status — 12 November 2026

Built, not yet walked through in a browser. Back end: 11 tests (own tenancies only, history,
housemates, no landlord contact, fixed query count) and the 61 tenancy tests pass. Admin:
type-check, lint and a production build pass.

## Goal

A tenant sees the places they rent now and the places they rented before, in the same
site layout they browse in (see [Tenant area](tenant-area.md)), instead of an empty page.

## How it works

- `GET /api/tenant/tenancies/` lists every tenancy the signed-in tenant has joined,
  newest start first. It includes tenancies they have left and tenancies that ended or
  were cancelled, so it is also their rental history. Needs a tenant and `tenancies.view`.
- Each row has: reference, status, start and end dates, the property (name, suburb,
  state) and unit, the landlord's **name** (the primary owner; no email or phone), the
  tenant's own join date, leave date and whether they are the primary tenant, and rent
  and bond when the landlord has set them.
- **Current** means the tenant has not left and the tenancy is not `ENDED` or
  `CANCELLED`. Everything else is **history**.
- `GET /api/tenant/tenancies/<id>/` is one of the tenant's own tenancies, plus the names of
  the other current tenants. Another person's tenancy, or a deleted one, is a 404.
- Screens (`/tenant`):
  - **Overview**: current tenancies, invitations waiting for an answer, and a prompt to
    browse rentals when there is nothing yet.
  - **Tenancies** (`/tenant/tenancies`): invitations waiting, then **Current**, then
    **Rental history**, each tenancy linking to its page.
  - **A tenancy** (`/tenant/tenancies/<id>`): dates, place, landlord, rent and bond,
    housemates.

## Source locations

- Back end: `back-end/tenancies/tenant_views.py`, `tenant_tenancy_urls.py`,
  `services/list_my_tenancies.py`, `services/get_my_tenancy.py`,
  `resources/my_tenancy.py`, `TenancyQuerySet.for_tenant`.
- Admin: `admin/app/tenant/`, `admin/components/tenancies/`.

## Not done

- Rent payments, bond records and condition reports: no tables are in use yet.
- Ending a tenancy or leaving one (see [Admin tenancies](admin-tenancies.md)).
