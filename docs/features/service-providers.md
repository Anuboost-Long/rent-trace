# Service providers (preferred tradespeople)

## Status — 13 November 2026

All three steps are built. Back end: 23 provider tests, 8 for the tenant's list, and 12 for the
category and booking (`maintenance/tests/test_assign_provider.py`); lint, the migration check and
the OpenAPI build pass (only the four enum-naming warnings that were already there). Admin:
type-check and lint pass. Seen in Chrome as a landlord: the menu item, the list, the form, and
adding a plumber. **Not seen in a browser yet:** editing and deleting a tradesperson, the trade
on the report form, booking from an issue, and everything on the tenant side (a tenant account
can't be signed in from here). The dev data has the test plumber linked only to "Test house", so
a tenant of "Test Apartment Building" sees none until the landlord links them there.

## Goal

A landlord keeps a list of the tradespeople they use (plumber, electrician, and so on), marks
their preferred ones, and picks one for a maintenance issue with a time. The tenant sees who is
coming and when, without needing to chase the landlord.

## How it works

Build in this order. Each step is usable on its own.

1. **Providers.** A landlord adds, edits and removes tradespeople: business name, contact name,
   phone, email, website (at least one way to reach them), the categories they cover, a
   **preferred** flag, and private notes. Categories are a fixed list: plumbing, electrical,
   appliances, heating and cooling, locks and doors, pests, general. A provider belongs to the
   landlord and is linked to each property it serves, so a plumber is entered once.
2. **Category on an issue.** Whoever reports an issue can say what kind of problem it is. It fills
   the `service_category` field that already exists on a maintenance issue and is optional.
3. **Assign a provider to an issue.** The landlord picks a provider (preferred ones first, then
   those matching the issue's category) and an optional time. Re-assigning keeps the history: each
   assignment supersedes the last (`maintenance_assignments`). The landlord can mark the visit
   done. The tenant sees the booked provider and date on the issue, with the provider's contact
   details, and is notified. The landlord can only pick providers linked to the issue's property;
   the picker lists ones matching the issue's category first, then preferred ones. The date has
   no time of day. Visit notes are not exposed anywhere yet.

Rules:

- A landlord only sees and uses their own providers, and only on properties they currently own;
  anything else is a 404, as for maintenance.
- A provider can only be assigned to an issue on a property the landlord owns.
- **Tenants see a provider's full contact details** (business name, contact name, phone, email,
  website, address, description, categories), because the list is a suggestion to them: the
  provider booked on their issue, and every provider linked to the property they rent, with the
  preferred ones first and marked. Only a tenant who is still in a live tenancy sees the list.
  **Contract notes stay private** to the landlord side and admins and are never sent to tenants.
- Assigning a provider does not change the issue's status. Status keeps its own rules and its
  both-sides-agree closure ([Maintenance](maintenance.md)).

### Decisions made

- **What a tenant sees:** everything about the provider except contract notes (above), so they
  can arrange access.
- **Whose list it is:** the landlord's, linked to properties. Schema change: `service_providers`
  gets an owner (the landlord) instead of a single property; `property_service_providers` stays as
  the link, and carries `is_recommended` and `contract_notes` per property.

## Source locations

- Back end: `back-end/providers/` (`views.py`, `urls.py`, `dtos/`, `resources/`, `services/`,
  `tests/`), mounted at `/api/landlord/providers/`:
  - `GET` and `POST` `/api/landlord/providers/` (filters `q` and `category`, paged).
  - `GET`, `PATCH` and `DELETE` `/api/landlord/providers/<id>/`.
  - `GET /api/landlord/providers/categories/` for the category list.
  - `GET /api/tenant/tenancies/<id>/providers/` for tenants (`tenant_views.py`,
    `tenant_urls.py`, `services/list_my_property_providers.py`): the providers linked to the
    tenancy's property, preferred first, never with contract notes.
  - Maintenance (`back-end/maintenance/`): `category_code` on reporting (optional) and a
    `category` on every issue; `GET /api/maintenance/categories/` for the report form;
    `POST /api/maintenance/<id>/assignment/` (book or change) and
    `POST /api/maintenance/<id>/assignment/complete/`; the issue detail carries `assignment`
    (with the provider's contact details), `provider_options` (landlord only) and the actions
    `ASSIGN_PROVIDER` and `COMPLETE_VISIT`. Notification kind `MAINTENANCE_PROVIDER_ASSIGNED`
    (`notifications/migrations/0008`); its text names the provider and date, never contact details.
  - Permissions `providers.view` and `providers.manage` (landlords) were already seeded.
- Schema: `providers/migrations/0002` (owner on the provider, re-addable links) and `0003`
  (starting categories); see `back-end/docs/schema-changes-for-diagram.md`, section 11.
- Admin: "Tradespeople" item in the landlord menu (`constants/navigation.ts`, needs
  `providers.view`); pages `admin/app/(app)/landlord/providers/` (list, `new`, `[id]`);
  components `admin/components/providers/` (list, filter, form, per-property link fields,
  delete button, editor page, and `tenant-providers.tsx` for the tenant's tenancy page);
  maintenance: `admin/components/maintenance/issue-provider.tsx` (the booked tradesperson), the
  booking dialog in `issue-actions.tsx`, and the trade select in `report-issue-button.tsx`; API in `admin/api/services/providers/serve-action.ts`; types in
  `admin/types/providers/models.ts`; hooks `useSaveProvider` and `useDeleteProvider`.

## Not done

Not planned yet: ratings or reviews of providers, quotes and invoices,
providers signing in themselves, and the landlord's own preferred contact details for tenants.
