# Admin tenancies

## Status — 15 November 2026

Built. Walked through in Chrome on 12 November 2026 as the super admin: the list,
new tenancy (property search, unit, start date) and detail page all work, and the
new tenancy shows on the list and the dashboard. Not tried: sending, resending and
revoking an invite, and the accept page. The local back end sends mail through
Gmail, so an invite sends a real email. The date fields use the new custom calendar; start date, end-date limits and keyboard use were checked in Chrome. Back end: 42 tenancy tests pass.

Walked through again on 15 November 2026 as the regular admin (`kimlongly53@gmail.com`,
not the super admin): detail page gates **Edit tenancy** correctly (404s for
`ENDED`/`CANCELLED`, by design — see `components/tenancies/edit-tenancy.tsx`), and
**Start tenancy** correctly refuses with "Add a tenant first" when no tenant has
joined. Still not tried: inviting a tenant to the point of starting a tenancy, since
that needs a real email send (see `docs/todo.md` item 3). There is no "on behalf of"
field to check here — tenancies have no such column; only
`maintenance_status_history` and the (unbuilt) reviews tables carry one. Admin
actions on a tenancy are tracked only as `updated_by`, which correctly showed the
admin after ending one.

## Goal

An admin finds every tenancy, sets one up on any unit, and invites tenants to it
by email. A tenant who gets the email can accept from a page in the app.

## How it works

- **List** (`/admin/tenancies`, needs `tenancies.admin_view`): every tenancy,
  newest first, with reference, property and unit, status, dates, number of
  current tenants and number of pending invites. Filter by search (reference,
  property name or address, unit, tenant name or email) and status.
- **New** (`/admin/tenancies/new`, needs `tenancies.admin_manage`): choose a
  property, a unit, a start date (chosen on our own calendar; the end date can't be on or before the start) and optionally an end date and notes. The
  tenancy starts as a draft. Rules are in [Tenant invitations](tenant-invitations.md).
- **Detail** (`/admin/tenancies/<id>`): the tenancy, its current tenants and its
  invitations. Needs `tenancies.admin_manage` to **invite**, **resend** or
  **revoke**. Errors from the back end (already invited, already a tenant, a
  primary tenant already exists, tenancy ended) show on the form.
- **Accept** (`/invitations/accept?token=…`): the page the invite email links to.
  The tenant signs in (or signs up) as the invited email, then accepts. See
  [Tenant invitations](tenant-invitations.md) for who may accept.

## Source locations

- Back end: `back-end/tenancies/`. `GET /api/tenancies/` (and the landlord
  copy, `GET /api/landlord/tenancies/`, needs `tenancies.view`) is new:
  `services/list_tenancies.py`, `resources/tenancy_summary.py`, `TenancyQuerySet.search`.
- Navigation: a Tenancies item under Rentals in `admin/constants/navigation.ts`.
- Admin: `admin/app/(app)/admin/tenancies/` (thin pages over `admin/components/tenancies/`,
  shared with the landlord area), `admin/app/(app)/invitations/accept/`,
  `admin/api/services/tenancies/`, `admin/types/tenancies/`.

## Not done

- A tenant who has no account yet must sign up and verify first; the sign-up flow
  does not carry them back to the accept link, so they open the email link again.
- No preview of the invitation before accepting; the page only asks to accept.
- Start, end and cancel are built ([Tenancy lifecycle](tenancy-lifecycle.md)), and so are editing
  dates, notes, rent and bond ([Tenancy terms](tenancy-terms.md)).
