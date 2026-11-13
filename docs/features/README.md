# Features

Every feature has a document here. See `CLAUDE.md` for the rule.

| Feature                                              | Status                                                                                 |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------- |
| [Authentication and sessions](authentication.md)     | Shipped                                                                                |
| [Account and onboarding](account-and-onboarding.md)  | Shipped                                                                                |
| [Admin app shell](admin-app-shell.md)                | Shipped; tenant and landlord pages are placeholders                                    |
| [Admin users](admin-users.md)                        | Shipped                                                                                |
| [Access control](access-control.md)                  | Shipped                                                                                |
| [Bans and sessions](bans-and-sessions.md)            | Shipped                                                                                |
| [Locations lookup](locations.md)                     | Shipped                                                                                |
| [Properties, units, photos and files](properties.md) | Shipped                                                                                |
| [Unit rent](unit-rent.md)                            | Walked through 14 Nov 2026 (landlord and tenant)                                       |
| [Listing status](listing-status.md)                  | Walked through 14 Nov 2026; see known issues                                           |
| [Public listings](public-listings.md)                | Walked through 14 Nov 2026; occupied units drop out (fixed and re-checked 14 Nov 2026) |
| [Admin tenancies](admin-tenancies.md)                | Built; invites and accept page walked through 14 Nov 2026 (landlord side)              |
| [Admin overview](admin-overview.md)                  | Built and walked through                                                               |
| [Tenant area](tenant-area.md)                        | Walked through 14 Nov 2026                                                             |
| [Landlord tenancies](landlord-tenancies.md)          | Walked through 14 Nov 2026; overview page is a placeholder                             |
| [Contact requests](contact-requests.md) | Walked through 14 Nov 2026; emails not sent |
| [Notifications](notifications.md)                    | Walked through 14 Nov 2026                                                             |
| [Tenant tenancies](tenant-tenancies.md)              | Walked through 14 Nov 2026                                                             |
| [Tenancy lifecycle](tenancy-lifecycle.md) | Start, end and cancel walked through 14 Nov 2026 |
| [Housemate invitations](housemate-invitations.md) | Walked through 14 Nov 2026 (request, approve, decline, accept) |
| [Tenancy terms](tenancy-terms.md)                    | Walked through 14 Nov 2026 (both sides)                                                |
| [Rent change approval](rent-change-approval.md) | Approve and decline walked through 14 Nov 2026 |
| [Maintenance](maintenance.md) | Walked through 14 Nov 2026, report to close and reject |
| [Unit conditions](unit-conditions.md)                | Walked through 14 Nov 2026 (both sides)                                                |
| [Service providers](service-providers.md)            | Walked through 14 Nov 2026 (landlord and tenant)                                       |

"Shipped" docs were written from the code and the back-end README on
12 November 2026 and were not re-tested then.

Not yet built: reviews and documents. Their tables exist in the back end but they have
no API or screens.
Known issues from the 14 November 2026 walkthrough (test landlord and tenants, local
database):

- A declined rent proposal does not appear in the tenant's rent and bond history.
- A rejected maintenance closing leaves no trace on the issue: the proposal disappears and the
  landlord only learns from a notification.
- Not tried: the admin side of any of these, and sending, declining or cancelling a contact
  request from the screens. Housemate and contact requests were made, and the contact request
  was accepted and revoked, through the service layer with email suppressed, because the server
  sends real mail; the screens were checked for what each side sees.
