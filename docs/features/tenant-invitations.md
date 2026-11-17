# Tenant invitations

## Status — 15 November 2026

Shipped in the back end, 12 November 2026. 35 tenancy tests and the full suite
(365) pass; Ruff, `manage.py check` and the OpenAPI schema validate.

Walked through end to end against the real Gmail backend on 15 November 2026: an admin invited
a real address, resent it (fresh link, old one correctly dead), and the invitee received the
email, accepted it themselves (`invitee_accepted_at` set, joined as primary tenant), and the
admin then started the tenancy. A second invitation, created and revoked without being
accepted, correctly stopped offering Resend/Revoke/Approve once revoked. The admin app does
have screens for this after all (`components/tenancies/invitations-section.tsx`, shared with
the landlord tenancy page) — see the correction in
[Admin tenancies](admin-tenancies.md).

## Goal

A landlord (or an admin on their behalf) invites a tenant by email to a tenancy.
The tenant follows the link, signs in or signs up, and joins the tenancy.

An invite belongs to a tenancy, and no tenancy API existed, so this also adds the
smallest tenancy API the invites need: create one and read one.

Builds on the `tenancy_invitations` table and the rules in
`back-end/docs/authentication.md` §5.

## How it works

### Tenancies (minimal)

- Create a tenancy on a unit: `property_unit_id`, `start_date`, optional
  `end_date` (after the start) and `notes`. It starts as `DRAFT` and
  `WHOLE_UNIT`. A landlord can only use units of properties they currently own;
  anything else is a 404. `reference_no` is generated.
- Read one tenancy with its unit, property, current tenants and invitations.
- Not here yet: list, edit, activate, end, rent, bond, area-based tenancies.

### Inviting

- Invite an email, optionally as the primary tenant. Needs
  `tenancies.manage_parties` (landlords) or `tenancies.admin_manage` (admins).
- The email is trimmed and lowercased. The invite lasts **7 days**.
- Refused (400): the tenancy is `ENDED` or `CANCELLED`; that email already has a
  pending invite here (resend it instead); that email is already a current tenant
  of the tenancy; `is_primary` is set but the tenancy already has a primary tenant.
- The raw token is only in the emailed link
  (`WEB_APP_URL/invitations/accept?token=…`); the database keeps `sha256(token)`.
  The email goes out after commit, and a failed email never undoes the invite.
  The same email goes to people with and without an account.
- **Resend** gives a pending or expired invite a new token and a new 7 days and
  emails it again. The old link stops working. This is also how an expired invite
  is renewed.
- **Revoke** ends a pending or expired invite. Accepted and revoked invites can't
  be resent or revoked (404). A revoked email can be invited again.
- An invite's status is `PENDING`, `ACCEPTED`, `REVOKED` or `EXPIRED`. Responses
  never include the token.

### Accepting (the tenant)

- The tenant's **Tenancies** page lists these with an **Accept invitation** button (accept by id),
  and a verified tenant account with the invited email gets an in-app notification, so the email
  link is not the only way in. See [Notifications](notifications.md).
- `GET /api/tenant/invitations/`: pending, unexpired invites for the signed-in
  tenant's email, with property, unit, who invited and when it expires.
- `POST /api/tenant/invitations/accept/` with `token`, or
  `POST /api/tenant/invitations/<id>/accept/` for one from that list.
- Accepting needs a signed-in **tenant** whose **verified** email equals the
  invited email. A forwarded link can't be used by anyone else.
- Accepting sets `accepted_at` and `accepted_by` and creates the tenancy party
  (joined today, primary if invited as primary) in one transaction.
- Refused: invite not pending or expired (400, "This invitation is invalid or has
  expired."), a different email (the same 400, so it doesn't reveal who was
  invited), already a tenant here, or primary requested while a primary exists
  (409).
- Inviting creates no relationship; the invitee is a tenant only after accepting.

### Who can call what

| Who      | Path                       | Permissions                                                      |
| -------- | -------------------------- | ---------------------------------------------------------------- |
| Landlord | `/api/landlord/tenancies/` | `tenancies.create`, `tenancies.view`, `tenancies.manage_parties` |
| Admin    | `/api/tenancies/`          | `tenancies.admin_manage` (change), `tenancies.admin_view` (read) |
| Tenant   | `/api/tenant/invitations/` | `tenancies.accept_invitation`                                    |

`tenancies.admin_view`, `tenancies.admin_manage` (admin only) and
`tenancies.accept_invitation` (tenant) are new, added by a seed migration.

| Method and path (under the base above)          | Does                         |
| ----------------------------------------------- | ---------------------------- |
| `POST /`                                        | Create a tenancy             |
| `GET <id>/`                                     | Read one                     |
| `POST <id>/invitations/`                        | Invite `email`, `is_primary` |
| `POST <id>/invitations/<invitation_id>/resend/` | New token and expiry         |
| `POST <id>/invitations/<invitation_id>/revoke/` | Revoke                       |

## Source locations

- `back-end/tenancies/`: `views.py` (admin; the landlord views subclass them and only
  narrow the scope), `landlord_views.py`, `tenant_views.py`,
  `urls.py`, `landlord_urls.py`, `tenant_urls.py`, `dtos/`, `resources/`, `services/`,
  `integrations/emails.py`, `tests/`.
- `back-end/accounts/migrations/0007_seed_tenancy_permissions.py`,
  `accounts/seeds/permissions.py`.
- `back-end/config/urls.py`, `settings.py`.
- `back-end/README.md`: endpoint tables.

## Not done

- The admin and landlord screens and the tenant accept page (`/invitations/accept`) are
  built; see [Admin tenancies](admin-tenancies.md) and
  [Landlord tenancies](landlord-tenancies.md).
- Offering pending invites right after sign-up (the list endpoint exists for it).
- Rate limit on invites per landlord, and a cap on pending invites per tenancy.
- No overlap check between tenancies on the same unit.
- Area-based tenancies. List, start, end, cancel, editing, rent and bond are built.
