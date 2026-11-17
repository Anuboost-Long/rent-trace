# Features

Every feature has a document here. See `CLAUDE.md` for the rule.

| Feature                                              | Status                                                                                                                                                                                                                         |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Authentication and sessions](authentication.md)     | Shipped; forgot/reset and change password with an authenticator code for admins added 18 Nov 2026 (code step not seen in a browser)                                                                                            |
| [Account and onboarding](account-and-onboarding.md)  | Shipped                                                                                                                                                                                                                        |
| [Admin app shell](admin-app-shell.md)                | Shipped; tenant and landlord pages are placeholders                                                                                                                                                                            |
| [Admin users](admin-users.md)                        | Shipped; super admin can reset a person's authenticator (built 18 Nov 2026, not yet seen in a browser)                                                                                                                        |
| [Access control](access-control.md)                  | Shipped                                                                                                                                                                                                                        |
| [Bans and sessions](bans-and-sessions.md)            | Shipped                                                                                                                                                                                                                        |
| [Locations lookup](locations.md)                     | Shipped                                                                                                                                                                                                                        |
| [Properties, units, photos and files](properties.md) | Shipped; admin property/unit screens walked through 15 Nov 2026; manual unit occupancy control added 15 Nov 2026                                                                                                               |
| [Unit rent](unit-rent.md)                            | Walked through 14 Nov 2026 (landlord and tenant)                                                                                                                                                                               |
| [Listing status](listing-status.md)                  | Walked through 14 Nov 2026; see known issues                                                                                                                                                                                   |
| [Public listings](public-listings.md)                | Walked through 14 Nov 2026; occupied units drop out (fixed and re-checked 14 Nov 2026)                                                                                                                                         |
| [Tenant invitations](tenant-invitations.md)          | Shipped; full invite/resend/revoke/accept loop walked through against real Gmail 15 Nov 2026                                                                                                                                   |
| [Admin tenancies](admin-tenancies.md)                | Built; invites and accept page walked through 14 Nov 2026 (landlord side); admin-side view/edit-gating/start/cancel/invite walked through 15 Nov 2026                                                                          |
| [Admin overview](admin-overview.md)                  | Built and walked through; landlord version added 16 Nov 2026, not yet walked through                                                                                                                                           |
| [Tenant area](tenant-area.md)                        | Walked through 14 Nov 2026                                                                                                                                                                                                     |
| [Landlord tenancies](landlord-tenancies.md)          | Walked through 14 Nov 2026; overview page built and walked through 16 Nov 2026                                                                                                                                                 |
| [Contact requests](contact-requests.md)              | Walked through 14 Nov 2026; received/answered emails confirmed against real Gmail 15 Nov 2026; admin read-only list and linking from a property walked through 16 Nov 2026                                                     |
| [Notifications](notifications.md)                    | Walked through 14 Nov 2026                                                                                                                                                                                                     |
| [Tenant tenancies](tenant-tenancies.md)              | Walked through 14 Nov 2026                                                                                                                                                                                                     |
| [Tenancy lifecycle](tenancy-lifecycle.md)            | Start, end and cancel walked through 14 Nov 2026 (landlord); end and cancel walked through from the admin side 15 Nov 2026                                                                                                     |
| [Housemate invitations](housemate-invitations.md)    | Walked through 14 Nov 2026 (request, approve, decline, accept); real-email + in-app notification loop confirmed 15 Nov 2026                                                                                                    |
| [Tenancy terms](tenancy-terms.md)                    | Walked through 14 Nov 2026 (both sides)                                                                                                                                                                                        |
| [Rent change approval](rent-change-approval.md)      | Approve and decline walked through 14 Nov 2026; declined/withdrawn now show in tenant history 15 Nov 2026                                                                                                                      |
| [Maintenance](maintenance.md)                        | Walked through 14 Nov 2026, report to close and reject; rejected-closing timeline trace added 15 Nov 2026; admin read-only view walked through 16 Nov 2026; super admin status moves built 17 Nov 2026, not yet walked through |
| [Unit conditions](unit-conditions.md)                | Walked through 14 Nov 2026 (both sides)                                                                                                                                                                                        |
| [Service providers](service-providers.md)            | Walked through 14 Nov 2026 (landlord and tenant); admin read-only list and linking from a property walked through 16 Nov 2026                                                                                                  |
| [Date display](date-display.md)                      | In progress; nothing verified yet                                                                                                                                                                                              |

"Shipped" docs were written from the code and the back-end README on
12 November 2026 and were not re-tested then.

Not yet built: reviews and documents. Their tables exist in the back end but they have
no API or screens.
Known issues from the 14 November 2026 walkthrough (test landlord and tenants, local
database):

- ~~A declined rent proposal does not appear in the tenant's rent and bond history.~~ Fixed
  15 Nov 2026: see [Rent change approval](rent-change-approval.md).
- ~~A rejected maintenance closing leaves no trace on the issue~~ Fixed 15 Nov 2026: see
  [Maintenance](maintenance.md).
- Not tried: the admin side of any of these, and sending, declining or cancelling a contact
  request from the screens. Housemate and contact requests were made, and the contact request
  was accepted and revoked, through the service layer with email suppressed, because the server
  sends real mail; the screens were checked for what each side sees.

Known issues from the 15 November 2026 admin walkthrough (regular admin, `kimlongly53@gmail.com`,
local database):

- ~~The admin app has no Maintenance, Contact requests or Tradespeople screens.~~ Read-only lists
  for all three were added 16 Nov 2026. Admins still cannot act on any of them, so the
  `on_behalf_of` recording on `maintenance_status_history` (the only tenancy-adjacent history table
  that has it) can't yet be exercised from the admin UI. Phase 2 (super admin status moves, recording `on_behalf_of`) was built 17 Nov 2026 and is not yet walked through.
- Tenancies have no `on_behalf_of` concept to check in the first place — only
  `maintenance_status_history` and the unbuilt reviews tables carry that column. Admin actions on
  a tenancy are tracked only as `updated_by`, confirmed correct when an admin ended one.
- Starting a tenancy to `ACTIVE` from the admin side needs an invited-and-accepted tenant; this
  was completed later the same session with a real email send — see `docs/todo.md` item 3 and
  [Tenant invitations](tenant-invitations.md).
- ~~Confirmed by walkthrough: unit occupancy (`PARTIALLY_OCCUPIED`/`UNAVAILABLE`) has no admin UI
  control anywhere — the unit edit form has no occupancy field at all.~~ Fixed 15 Nov 2026: see
  [Properties](properties.md).
