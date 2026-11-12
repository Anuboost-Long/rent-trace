# Housemate invitations

## Status — 12 November 2026

Built, not yet walked through in a browser. Back end: 40 new tests (both orders of approval,
decline, withdraw, expiry, an account that goes bad in between, the unit limit at invite and at
join time, the request limits, privacy, notifications) and the 212 existing tenancy, notification,
communications and properties tests pass; the full back-end suite (517 tests) passes. Admin: type-check, lint and a production build pass.
The migrations were tried on a database that already had invitations; that found, and fixed, two
problems (a PostgreSQL "pending trigger events" error, and a CHECK that let a NULL decision through).

## Goal

A tenant invites another person to join their tenancy. The person only joins when **both**
the landlord and the invited person have said yes. A unit can have a maximum number of
people, and nobody can be added past it.

## How it works

### Who can ask

- Any **current tenant** of a tenancy that is `DRAFT` or `ACTIVE` can ask (permission
  `tenancies.invite_housemate`, given to tenants). They enter an email. They can't ask for a
  primary tenant and can't invite themselves.
- Same checks as a landlord's invitation: the person isn't already a tenant, doesn't
  already have an open invitation, and the unit has room.
- Limits, because the invitation email goes to any address the tenant types: at most **5 open
  tenant requests** per tenancy, and at most **10 requests per person in 24 hours** whatever
  happened to them (withdrawing and re-asking still counts). Both answer 400.
- Only current tenants count: someone who has left a tenancy can't ask, withdraw or see its
  requests. A tenant sees only their own requests, with the email they typed; other housemates'
  requests, and the invitee's email, stay hidden from them.

### Two approvals, in any order

1. When the tenant asks, **two things go out at once**: the invited person gets the usual
   invitation email (and an in-app notification if they already have a verified tenant
   account with that email), and the landlord gets an email and an in-app notification to
   review the request.
2. The **invited person** accepts as they do today (emailed link, or the Accept button on
   their Tenancies page). If the landlord hasn't answered yet they are told they are waiting.
3. The **landlord** (any current owner of the property) or an admin sees the request on the
   tenancy page with **Approve** and **Decline**.
4. The person **joins the moment both have said yes**, whichever came first. Joining adds
   them as a current tenant from that day.
5. **Decline** by the landlord ends the request (status `DECLINED`). The requesting tenant and the invited
   person are told. The tenant can also **withdraw** their own request, and the landlord or
   admin can revoke it, as with any invitation.
6. The invitation still lasts **7 days**. If it expires with one side missing, nobody joins;
   a new request is needed. A landlord can't re-send a request the invited person has already
   accepted.
7. At the moment of joining everything is checked again, because the second yes can come days
   later: the tenancy is still open, the invitation isn't expired or revoked, the invited account
   is still active, not banned and a tenant, they aren't already a current tenant, a primary
   tenant isn't taken, and the unit still has room.

A landlord's or admin's own invitation is unchanged: the landlord's approval is implied, so
the invited person joins when they accept.

### Maximum people per unit

- Each unit has an optional **maximum number of people** (1 or more; empty means no limit),
  set on the unit form by the landlord or admin.
- The limit is checked when someone is **invited** (landlord or tenant) and again at the
  moment they would **join**, so two people accepting at once can't go over. A full unit
  answers 400, "This unit is full (up to N people)." The count is the current tenants of the
  tenancy; people who have only been invited don't count until they join.
- Lowering the limit below the number already living there is allowed. Nobody is removed; no
  one more can be added.

### What people see

- **Tenant** (tenancy page): an **Invite a housemate** form, and their requests with who is
  still to answer ("Waiting for the landlord", "Waiting for them to accept"). The tenancy shows
  "People: 2 of 4" when the unit has a limit.
- **Invited person** (Tenancies page, and the emailed link): the invitation with Accept. After
  accepting they are told whether they have **joined** or are **waiting for the landlord**; the
  page never says "joined" before both have said yes.
- **Landlord and admin** (tenancy page): tenant requests are marked as asked by a tenant,
  show what is still pending, and have Approve and Decline.
- **The tenant's People section** (on their tenancy page) is a light list with hairlines and no box:
  you, your housemates, then an "Invites" group of pending and finished invitations. Each person has
  a monogram; a **dashed** outline means invited but not yet a member. The count ("2 of 4") sits in
  the header beside a filled **Invite housemate** button, which is disabled with "This place is
  full" when the unit is at its limit and hidden for a tenancy that has ended. When you live alone
  with no invites, one plain sentence explains how to add someone (no second button). The button
  opens a small dialog with one field; sending closes it and shows "Invite sent to … We've told your
  landlord too." Each open invite shows its two approvals as two marked steps, "Landlord approved /
  Waiting for your landlord" and "They accepted / Waiting for them", and when it expires; finished
  ones show a single status.
- Notifications carry no email addresses or links. The landlord opens the tenancy to see who
  was asked. The invited person's notifications open their Tenancies list, because they aren't a
  member of the tenancy yet.

## Source locations

- Back end: `back-end/tenancies/` (`services/request_housemate.py`, `approve_housemate.py`,
  `decline_housemate.py`, `withdraw_housemate.py`, `accept_invitation.py`,
  `services/shared/joining.py`), `back-end/properties/` (`PropertyUnit.max_occupants`),
  `back-end/accounts/migrations/0009_…`, `back-end/notifications/models.py`.
- Admin: `admin/components/tenancies/` and `admin/components/properties/unit-form.tsx`.

## Not done

- Counting people who are only invited toward the limit.
- A landlord asking a tenant to leave, or a tenant leaving.
