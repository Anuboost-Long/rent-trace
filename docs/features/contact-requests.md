# Contact requests

## Status — 16 November 2026

Admin read-only view: **built and walked through** in Chrome as an admin on 16 Nov 2026: three
requests across two landlords, accepted ones show no email or phone, search (`q=walkthrough`)
and the status filter narrow the list. 6 back-end tests pass.

### Admin view (read-only)

- Admins with `contact_requests.admin_view` list and open every contact request, across all
  landlords: `/api/admin/contact-requests/` and `/<id>/`. Landlords, tenants and admin-side people
  without the code get 403.
- Each row shows the property and unit, who asked, the property's primary owner, the message, the
  status and when it was decided. **No tenant or landlord contact details**: those stay hidden
  until a request is accepted and are only for the two parties. An admin finds a person's contact
  details on their account page.
- The list filters by status and searches the property name, suburb and the tenant's name.
- Admin screen: `/admin/contact-requests` (a list only, like the other two sides; the detail
  endpoint exists but has no screen). An admin cannot accept, decline or cancel; that stays with
  the two parties.
- Acceptance: an admin sees requests across two landlords; the response never contains contact
  details, even for an accepted request; landlords and tenants get 403.

## Status — 15 November 2026

Walked through end to end against the real Gmail backend on 15 November 2026: signed in as a
tenant, sent a contact request from a public listing page (`properties/1`) to a real landlord
address, the landlord received the "new contact request" email and accepted it from their
Contact requests screen, and the tenant received the "request answered" email. Both emails'
wording and links confirmed correct.

## Status — 12 November 2026

Update 12 November 2026: an accepted request now also shows the tenant's email and phone to
the landlord (`tenant_contact`), and the request form tells the tenant so. 26 communications
tests pass; the landlord screen change is type-checked and linted, not yet seen in a browser.

Shipped, 12 November 2026 (back end first, then the screens). 23 back-end tests pass and the
full suite (392) did before the screens; Ruff, `manage.py check` and the OpenAPI schema
validate. The screens pass `tsc`, ESLint and Prettier but haven't been tried in a
browser, and the emails haven't been sent through a real mail server.

## Goal

A tenant who likes a listing asks to be put in touch with the landlord. The
landlord accepts or declines. On accept, each side sees the other's contact
details. Chat is a possible later step built on an accepted request; it is not
part of this feature.

Contact details stay private until a landlord accepts. The tenant is told on the form
that accepting shares their details too.

## How it works

### Tenant (`/api/tenant/contact-requests/`, needs `contact_requests.send`)

- **Send a request:** `listing_id` (the property's id, as on the public listings),
  optional `unit_id`, and a `message` of 1 to 1000 characters.
  - The property must be publicly listed. The unit, if given, must be one of its
    available public units. Otherwise 400.
  - One open request per tenant and property: if one is `PENDING` or `ACCEPTED`,
    sending another fails (400, "You already have a request for this property.").
  - At most 10 `PENDING` requests per tenant at once (400).
  - The primary owner is emailed that a request is waiting. The email holds no
    tenant details beyond their name and no contact info.
- **List and read my requests.** Each shows its status, message, listing, unit and
  when it was decided.
- **Cancel** a `PENDING` request (`POST <id>/cancel/`).
- **Landlord contact:** an `ACCEPTED` request includes `landlord` with the primary
  owner's name, email and phone (phone is empty if they haven't set one). It is
  `null` in every other status.

### Landlord (`/api/landlord/contact-requests/`, needs `contact_requests.respond`)

- **List** requests for properties they currently own (`status` filter, paginated,
  newest first) and **read** one. A landlord sees the tenant's name and message. Once the
  request is `ACCEPTED` the tenant's `contact` (email and phone, empty if not set) is
  included; it is `null` in every other status, including after a revoke. Requests for other people's properties are 404.
- **Accept** or **decline** a `PENDING` request (`POST <id>/accept/`, `…/decline/`).
- **Revoke** an `ACCEPTED` request (`POST <id>/revoke/`): the tenant stops seeing
  the contact details.
- Any other change is 400, naming the current status. Any current owner of the
  property can respond; the contact shown is always the primary owner's.
- Revoking takes the tenant's contact details away from the landlord's screen as well as
  the landlord's from the tenant's.
- The tenant is emailed when the request is accepted or declined. The email holds
  no contact info; they sign in to see it.

### Statuses

`PENDING` → `ACCEPTED` (→ `REVOKED`), `DECLINED`, or `CANCELLED` by the tenant.
After `DECLINED`, `CANCELLED` or `REVOKED` the tenant may send a new request.

### Permissions

New, added by a seed migration: `contact_requests.send` (tenant) and
`contact_requests.respond` (landlord). Neither is admin-only. Both sides also check
the role, as the other tenant and landlord routes do.

### Screens (admin app)

- **Listing page** (`/properties/<id>`), for a signed-in tenant: a "Request contact"
  box in place of "Messaging landlords is coming soon". It has an optional unit
  picker and a message. Once the tenant has an open request for that property the box
  shows its state instead: waiting, or the landlord's name, email and phone once
  accepted. Signed-out visitors still see "Sign in to get in touch".
- **Request form** says: "The landlord sees your name and message. If they accept, they also
  see your email and phone, and you see theirs."
- **Tenant: Contact requests** (`/tenant/requests`): the tenant's requests with status,
  the landlord's details when accepted, and **Cancel request** while waiting.
- **Notifications:** the landlord is told when a request arrives or is cancelled, and the tenant when it
  is accepted, declined or revoked; see [Notifications](notifications.md).
- **Landlord: Contact requests** (`/landlord/requests`): requests for their properties
  with a status filter, the tenant's email and phone once accepted, **Accept** and **Decline** while waiting, and **Revoke** once
  accepted. Each asks for confirmation. Both pages are in the sidebar.

## Source locations

- Admin read-only: `back-end/communications/admin_views.py`, `admin_urls.py`,
  `services/list_all_contact_requests.py`, `get_any_contact_request.py`;
  `admin/app/(app)/admin/contact-requests/page.tsx`.
- `back-end/communications/`: `models.py` (`ContactRequest`, table
  `contact_requests`), `tenant_views.py`, `landlord_views.py`, `tenant_urls.py`,
  `landlord_urls.py`, `dtos/`, `resources/`, `services/`,
  `integrations/emails.py`, `tests/`, migration `0003_contact_requests`.
- `back-end/accounts/migrations/0008_seed_contact_request_permissions.py`,
  `accounts/seeds/permissions.py`.
- `back-end/config/urls.py`, `back-end/README.md`.
- `admin/app/tenant/requests/`, `admin/app/(app)/landlord/requests/`,
  `admin/app/(site)/properties/[id]/page.tsx` (the request box).
- `admin/components/contact-requests/`: request form, action buttons, contact card,
  status filter.
- `admin/hooks/form/useSendContactRequest.ts`, `useContactRequestAction.ts`.
- `admin/api/services/contact-requests/serve-action.ts`,
  `admin/types/contact-requests/models.ts`, `admin/constants/contact-requests.ts`.

## Not done

- Admins can read contact requests but not act on them.

- Chat or messaging on an accepted request.
- Admin view of requests, and a cooldown after a decline.
- Two requests sent at the same instant could hit the database's one-open-request
  rule and answer 500 instead of 400.
