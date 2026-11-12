# Tenant tenancies and rental history

## Status — 13 November 2026

Built, not yet walked through in a browser. The redesigned Overview (13 November) is
type-checked and linted but not yet seen in a browser. Back end: 11 tests (own tenancies only, history,
housemates, no landlord contact, fixed query count) and the 61 tenancy tests pass. Admin:
type-check, lint and a production build pass.

## Goal

A tenant sees the places they rent now and the places they rented before, in the same
site layout they browse in (see [Tenant area](tenant-area.md)), instead of an empty page.

## How it works

- `GET /api/tenant/tenancies/` lists every tenancy the signed-in tenant has joined,
  newest start first. It includes tenancies they have left and tenancies that ended or
  were cancelled, so it is also their rental history. Needs a tenant and `tenancies.view`.
- Each row has: reference, status, start and end dates, the property (name, street
  address, suburb, state, postcode) and unit (name, type, description), the landlord's **name** (the primary owner; no email or phone), the
  tenant's own join date, leave date and whether they are the primary tenant, and rent
  and bond when the landlord has set them.
- **Current** means the tenant has not left and the tenancy is not `ENDED` or
  `CANCELLED`. Everything else is **history**.
- `GET /api/tenant/tenancies/<id>/` is one of the tenant's own tenancies, plus the names of
  the other current tenants. Another person's tenancy, or a deleted one, is a 404.
- Screens (`/tenant`):
  - **Overview**: a greeting by first name, invitations waiting for an answer, then one
    panel per current tenancy: the property, full address, what is rented (unit name and
    type), a strip with rent, bond, landlord and move-in date, **View tenancy**, and
    **Report an issue** when the tenancy is active. With no current tenancy it invites the
    tenant to browse rentals. A link to rental history shows when there is any.
  - **Tenancies** (`/tenant/tenancies`): invitations waiting, then **Current**, then
    **Rental history**, each tenancy linking to its page.
  - **A tenancy** (`/tenant/tenancies/<id>`): property, full address, what is being rented
    (unit name and type, plus its description when it has one), dates, landlord, rent and
    bond, housemates.

## Source locations

- Back end: `back-end/tenancies/tenant_views.py`, `tenant_tenancy_urls.py`,
  `services/list_my_tenancies.py`, `services/get_my_tenancy.py`,
  `resources/my_tenancy.py`, `TenancyQuerySet.for_tenant`.
- Admin: `admin/app/tenant/`, `admin/components/tenancies/` (Overview panels:
  `tenant-home.tsx`).

## Not done

- Overview has no property photo: tenants have no endpoint for a property's photos (only the
  public listings feed and the landlord and admin routes serve them).
- Overview does not show a waiting rent or bond increase; the tenancy list has no such field.
- Rent payments, bond lodgement and condition reports: no tables are in use yet. The rent and
  bond shown are the terms the landlord set ([Tenancy terms](tenancy-terms.md)).
- Ending a tenancy or leaving one (see [Admin tenancies](admin-tenancies.md)).
