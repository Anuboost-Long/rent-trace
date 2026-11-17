# Rent and bond change approval

## Status — 15 November 2026

The tenant's "Rent and bond history" was only showing `APPLIED` changes — a declined or
withdrawn proposal just vanished from the tenant's view once answered, even though the
landlord's own tenancy page always showed it. Fixed: the tenant-side prefetch
(`tenancies/services/shared/my_tenancies.py`) and `MyTenancyDetailResource.get_term_history`
now include `DECLINED` and `WITHDRAWN` alongside `APPLIED`, matching what the landlord/admin
side already showed. No front-end change needed — `components/tenancies/term-history.tsx` is
shared with the landlord side and already had labels for every status. Verified live in Chrome:
raised the rent on an active tenancy, declined it as a housemate, and it shows as "Declined" in
the tenant's own history. `SUPERSEDED` and `CLOSED` proposals are still left out of the tenant's
history (the landlord/admin side shows them) — deliberate, not an oversight; not asked for.

## Status — 12 November 2026

Built. Back end: 28 new tests (what needs approval, exact rent comparison, every approval and decline path, stale and expired proposals, ending and cancelling, who is allowed, no amounts in messages, a history row for every change) and the existing edit tests updated for the new rule. Admin: type-check, lint and a production build pass. In Chrome as the landlord on 12 November 2026: raising the rent on the test tenancy from $450 to $500 a week created a proposal, the page showed it waiting with the tenant's answer, and the rent stayed at $450. The tenant's side (the review panel, the notification, approving) has not been seen yet.

## Goal

A landlord (or an admin on their behalf) can't raise what tenants pay without the tenants
agreeing. The change waits until they approve; if they decline, nothing changes.

## How it works

### What needs approval

- When the tenancy has **current tenants**, a change to rent or bond that makes tenants pay **more**
  is held as a **proposal** instead of being applied. Rent is compared per week (fortnightly is
  halved, monthly is times 12 over 52), so moving the same money to a different frequency is
  judged on what it really costs. Setting a rent or bond that was empty counts as an increase.
- These apply **at once** and tell the tenants afterwards: a lower or equal rent and bond, and any
  change to dates or notes. A tenancy with **no current tenants** applies everything at once.
- If one edit mixes a rise and a fall, the whole money change (rent and bond together) is one
  proposal.

### The proposal

- Needs **every current tenant** to approve. If **one declines**, it ends and nothing changes. The
  landlord can propose again.
- Lasts **14 days**. After that it can't be approved and the landlord has to propose again.
- Only one is open per tenancy. A new proposal replaces the open one (which is marked superseded). A
  lower or equal change that is applied at once also replaces it.
- The landlord or admin can **withdraw** it. A tenancy that ends or is cancelled can't be approved.
- When the last tenant approves, the new rent and bond are applied and recorded with who proposed
  them, who approved and when. Each proposal keeps the old and new amounts, so there is now a
  history of rent and bond changes.
- A tenant who joins while a proposal is open also has to approve it.

### What people see

- **Tenant** (tenancy page): a notice at the top of the tenancy with the current and proposed rent and
  bond, who has approved, and **Approve** and **Decline**. After responding it shows their answer.
- **Landlord and admin** (tenancy page): the open proposal with each tenant's answer, when it
  expires, and **Withdraw**. The edit form says increases wait for tenants.
- **Notifications:** tenants are told when a change is proposed; the landlord when it is approved
  and applied, or declined. Messages carry no amounts.

### Permissions

A new permission, `tenancies.approve_terms`, goes to tenants. Landlords and admins propose through the
edit they already have (`tenancies.update`, `tenancies.admin_manage`) and withdraw with the same.

## Source locations

- Back end: `back-end/tenancies/` (`TenancyTermChange` and `TenancyTermDecision` models,
  `services/shared/terms.py`, `services/update_tenancy.py`, `respond_to_term_change.py`,
  `withdraw_term_change.py`), `back-end/accounts/migrations/0010_…`.
- Admin: `admin/components/tenancies/` (term change panel for tenants, landlords and admins).

## Not done

- Rent increase notice periods required by law (this is approval, not a statutory notice).
- Nothing writes history rows for the rent and bond a tenancy was created with; the history starts at the first edit.
- Changing the length of the approval window.
- Asking for approval of date changes.
