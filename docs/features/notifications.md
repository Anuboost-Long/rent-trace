# Notifications

## Status — 12 November 2026

Built, not yet walked through in a browser. Back end: 91 tests pass across notifications,
communications and tenancies (inbox API, every event above, and the cases that must not
notify: unknown or unverified email, a non-tenant account, a refused action). Admin:
type-check, lint and a production build pass.

The bell, inbox page and the tenant's "Invitations waiting for you" list have not been seen in
a browser.

## Goal

Tenants, landlords and admins see what needs their attention inside the web app, and act
on it there, instead of relying on email. An email can still go out, but it is no longer
the only place to find out.

## How it works

- Every signed-in person has an **inbox**. A **bell** with the number of unread items
  sits in the header (the site header for tenants, the top bar for landlords and admins).
  It refreshes about once a minute while the tab is open and on every page change.
- The inbox page (`/tenant/notifications`, `/landlord/notifications`,
  `/admin/notifications`) lists notifications newest first, with unread ones marked.
  Opening one marks it read and goes to the page where the person acts on it.
  **Mark all as read** clears the count. A filter shows unread only.
- Notifications are created in the same transaction as the action, so one never exists for
  an action that was rolled back.
- A notification says what happened and who did it. It never holds contact details or
  invitation links, so nothing leaks after a contact request is revoked.
- Only the recipient can see or change their notifications; another person's id is a 404.

### What creates a notification

| Event                                             | Who is told                                                                             | Where it leads                           |
| ------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------- |
| Tenant sends a contact request                    | Every current owner of the property                                                     | Landlord: Contact requests               |
| Tenant cancels a waiting request                  | Every current owner                                                                     | Landlord: Contact requests               |
| Landlord accepts, declines or revokes a request   | The tenant                                                                              | Tenant: Contact requests                 |
| Tenancy invitation sent or sent again             | The invited person, only if they already have a verified tenant account with that email | Tenant: Tenancies, where they can accept |
| Invitation accepted                               | Whoever sent it (a landlord or an admin)                                                | The tenancy                              |
| Tenant reports a condition                        | Every current owner of the property                                                     | Landlord: the tenancy                    |
| Landlord approves or rejects a reported condition | The tenant who reported it (a rejection includes the reason)                            | Tenant: the tenancy                      |

An invite to an address with no account, or an unverified one, makes no notification, and
the inviter's screen doesn't change either way. A person who signs up later sees the
invitation in their Tenancies page too, because that list is built from their email.

Two more kinds, `REVIEW_CASE_ESCALATED` (admins who can decide; leads to Review cases) and
`REVIEW_CASE_DECIDED` (the tenant and every current owner; leads to the tenancy), are written when
someone asks an admin to decide and when an admin decides (migration `notifications/0010`). Not seen
in a browser.

The three condition-evidence rows are the kinds `CONDITION_EVIDENCE_SUBMITTED`,
`CONDITION_EVIDENCE_APPROVED` and `CONDITION_EVIDENCE_REJECTED` (migration `notifications/0009`).
Their `subject_id` is the tenancy id. See [Reviews](reviews.md). Seen in Chrome 25 Nov 2026 for
the two tenant-side kinds (rejected one opened the tenant tenancy page); the landlord-side link
was not clicked.

### Where the link goes

The back end stores a `kind` and the id of the thing it is about. The admin app turns
that into a page for the person's area (a landlord and an admin open different pages for
the same tenancy).

## Source locations

- Back end: `back-end/notifications/` (`/api/notifications/`); events are written from
  `communications/services/` and `tenancies/services/`.
- Table: `notifications` gains a nullable `event`, a `kind` and a `subject_id`; see
  `back-end/docs/schema-changes-for-diagram.md`.
- Admin: `admin/components/notifications/`, the bell in the site header and navbar, and the
  three notifications pages.

## Not done

- Admin events: nothing needs an admin's action yet (disputes and removals are not built; the
  dispute case a rejection opens has no admin notice).
  Admins currently get "invitation accepted" for tenancies they set up. Say which events
  admins should be told about.
- Delivery by email through this inbox: emails are still sent directly by each action.
- Instant updates (the bell polls); settings to mute a kind of notification; deleting a
  notification.
