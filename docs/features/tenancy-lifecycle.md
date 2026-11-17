# Tenancy lifecycle

## Status — 15 November 2026

Built. Back end: 17 tests (rules, dates, overlap, notifications, permissions); the full suite
(472 tests) passes. Admin: type-check, lint and a production build pass. In Chrome as a landlord
on 12 November 2026: the Start and Cancel buttons show on a draft tenancy and the Start dialog
reads correctly. No tenancy was actually started, ended or cancelled in the browser, because the
test tenancy starts on 1 December 2026 and an active one can't be ended or cancelled before then.

Walked through from the **admin side** in Chrome on 15 November 2026 as the regular admin: ended
an active tenancy (confirmation dialog read correctly, status moved to `ENDED`, end date set to
the server's today, the unit's occupancy correctly dropped back to `VACANT`, `updated_by` recorded
the admin); created a new draft tenancy and cancelled it (status moved to `CANCELLED`, unit stayed
`VACANT` since it never started). Tried **Start** on a draft with no tenant yet: correctly refused
with "Add a tenant first. Invite someone and wait for them to accept." Starting a tenancy all the
way to `ACTIVE` still needs an invited-and-accepted tenant, which needs a real email send — not
done yet (see `docs/todo.md` item 3).

## Goal

A landlord, or an admin on their behalf, moves a tenancy from set-up to started to
finished, and the tenants and the dashboard follow.

## How it works

Statuses are `DRAFT` (set up, invitations out), `ACTIVE`, `ENDED` and `CANCELLED`.
(`PENDING` exists in the database but nothing sets it yet.)

| Action                              | From     | To          | Rules                                                                                                                                                                                                 |
| ----------------------------------- | -------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Start** (`POST …/<id>/activate/`) | `DRAFT`  | `ACTIVE`    | At least one current tenant. No other `ACTIVE` tenancy on the same unit may overlap its dates.                                                                                                        |
| **End** (`POST …/<id>/end/`)        | `ACTIVE` | `ENDED`     | It must already have started (after its start date, otherwise cancel it). The end date becomes today when it was open-ended or later than today. Every current tenant is marked as having left today. |
| **Cancel** (`POST …/<id>/cancel/`)  | `DRAFT`  | `CANCELLED` | For a tenancy that never started. Any tenant who already joined is marked as having left.                                                                                                             |

- Any other move is a 400 that names the current status. Another landlord's tenancy is
  a 404.
- Permissions: a landlord needs `tenancies.update` and acts on their own properties; an
  admin needs `tenancies.admin_manage` and can act on any. Paths are `/api/tenancies/…` for
  admins and `/api/landlord/tenancies/…` for landlords.
- **Unit occupancy follows the tenancy.** Starting a tenancy sets its unit to `OCCUPIED`; ending
  it sets the unit back to `VACANT` unless another tenancy on the unit is still `ACTIVE`. A unit
  marked `UNAVAILABLE` is never changed. So an occupied unit drops out of public listings
  ([Public listings](public-listings.md)). Occupancy of units whose tenancy started before this
  rule existed was corrected once by hand in the dev database.
- **Manually setting occupancy** (`VACANT`, `PARTIALLY_OCCUPIED` or `UNAVAILABLE` — see
  [Properties](properties.md)) is refused while the unit has an `ACTIVE` tenancy, so a landlord or
  admin can never make an occupied unit look available. This is the only guard: starting a tenancy
  does not check or clear occupancy first, so a unit left manually marked `UNAVAILABLE` and then
  given a new active tenancy anyway keeps showing `UNAVAILABLE` (the existing skip above) until
  someone clears it by hand — a known gap, not fixed here.
- An ended or cancelled tenancy takes no new invitations or joiners (already enforced).
- The tenants are told in the app when their tenancy starts, ends or is cancelled
  ([Notifications](notifications.md)); the message has no contact details.
- **Screens:** the tenancy page (admin and landlord) shows **Start tenancy**, **End
  tenancy** or **Cancel tenancy** for its current status, each with a confirmation and the
  back end's error if the move is refused.

## Source locations

- Back end: `back-end/tenancies/services/activate_tenancy.py`, `end_tenancy.py`,
  `cancel_tenancy.py`, `services/shared/transitions.py`, `views.py`, `landlord_views.py`,
  `urls.py`, `landlord_urls.py`, `TenancyQuerySet.overlapping`; notification kinds in
  `back-end/notifications/models.py`.
- Admin: `admin/components/tenancies/tenancy-actions.tsx`, `admin/hooks/form/useTenancyActions.ts`.

## Not done

- `PENDING` ("starting soon") is not used; a future-dated active tenancy simply shows as
  current from the day it is started.
- Editing a tenancy's dates, notes, rent and bond is built; see [Tenancy terms](tenancy-terms.md).
- Tenants leaving on their own, or a landlord removing one tenant from a running tenancy.
- Starting a tenancy never checks or clears a unit's manually set occupancy first — see the gap
  noted above.
