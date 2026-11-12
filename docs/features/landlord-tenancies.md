# Landlord tenancies

## Status — 12 November 2026

Built, not yet walked through in a browser. Typecheck, lint and a production build
pass. The back end needed no change; its landlord tests (create, list, invite, resend,
revoke, another landlord's unit) already cover this.

## Goal

A landlord sets up a tenancy on one of their own units and invites a tenant into it
by email, from their own area. The tenant accepts from the emailed link
(see [Tenant invitations](tenant-invitations.md)).

## How it works

- The landlord area uses the same tenancy screens as the admin area, limited to the
  landlord's own properties. The back end already enforces that: another landlord's
  unit or tenancy answers 404.
- **List** (`/landlord/tenancies`, needs `tenancies.view`): the landlord's tenancies,
  newest first, with search and a status filter.
- **New** (`/landlord/tenancies/new`, needs `tenancies.create`): choose one of their
  properties and a unit, a start date and optionally an end date and notes. It
  starts as a draft. `?property=<id>` pre-selects the property.
- **Property page** has a **New tenancy** button (needs `tenancies.create`) that
  opens the form for that property.
- **Detail** (`/landlord/tenancies/<id>`): the tenancy, its tenants and invitations.
  **Invite**, **resend** and **revoke** need `tenancies.manage_parties`. Rules and
  errors are the same as for admins.

## Source locations

- Shared screens: `admin/components/tenancies/`.
- Pages: `admin/app/landlord/tenancies/`, `admin/app/admin/tenancies/`.
- Back end: `GET/POST /api/landlord/tenancies/` and the invitation paths under it
  (`back-end/tenancies/landlord_views.py`); no back-end change was needed.

## Not done

- Start, end and cancel are built ([Tenancy lifecycle](tenancy-lifecycle.md)), and so are editing
  dates, notes, rent and bond ([Tenancy terms](tenancy-terms.md)).
- Removing a tenant who has already joined.
