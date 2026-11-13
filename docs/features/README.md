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
| [Notifications](notifications.md)                    | Walked through 14 Nov 2026                                                             |
| [Tenant tenancies](tenant-tenancies.md)              | Walked through 14 Nov 2026                                                             |
| [Tenancy lifecycle](tenancy-lifecycle.md) | Start and end walked through 14 Nov 2026; cancel not tried |
| [Housemate invitations](housemate-invitations.md) | Walked through 14 Nov 2026 (request, approve, decline, accept) |
| [Tenancy terms](tenancy-terms.md)                    | Walked through 14 Nov 2026 (both sides)                                                |
| [Rent change approval](rent-change-approval.md) | Approve and decline walked through 14 Nov 2026 |
| [Maintenance](maintenance.md)                        | Walked through 14 Nov 2026, report to close                                            |
| [Unit conditions](unit-conditions.md)                | Walked through 14 Nov 2026 (both sides)                                                |
| [Service providers](service-providers.md)            | Walked through 14 Nov 2026 (landlord and tenant)                                       |

"Shipped" docs were written from the code and the back-end README on
12 November 2026 and were not re-tested then.

Not yet built: reviews and documents. Their tables exist in the back end but they have
no API or screens.
Known issues from the 14 November 2026 walkthrough (test landlord and tenants, local
database):

- Maintenance history does not record the tradesperson being booked or the visit being done.
- A declined rent proposal does not appear in the tenant's rent and bond history.
- Not tried: cancelling a tenancy, declining a maintenance closing, contact requests, and the
  admin side of any of these. Housemate requests were made through the service layer so no email
  was sent; the approve, decline and accept steps were done in the browser.
