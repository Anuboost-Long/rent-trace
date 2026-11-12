# Admin app shell

## Status — 12 November 2026

Shipped 11 November 2026; the `(site)` route group was added after it and is in
progress (see [Public listings](public-listings.md)).

## Goal

One Next.js app serves tenants, landlords and admins, each with its own area,
navigation and permissions, built from shared components.

## How it works

- **Three audiences:** `/tenant`, `/landlord`, `/admin`. Each has its own layout
  (`audience-layout`) with a sidebar, navbar, breadcrumbs and page header. Routes
  and nav items live in `constants/web-routes.ts` and `constants/navigation.ts`.
- **Detail pages** put a plain "Back" link on its own line, with the breadcrumb trail beneath it,
  rather than a boxed button beside the trail.
- **Permissions in the UI:** the `Can` component shows or hides controls from the
  signed-in user's effective permissions. The back end still enforces them.
- **Shared components** (`components/common/`): button, text, select, check,
  radio, text-area, combobox and date inputs (the date input is our own month
  calendar, not the browser's; it keeps its value in a hidden field and takes a
  `min` date), data table with pagination, confirm
  dialog, loading host, modal, spinner and skeletons.
- **Loading:** a global loading state (`useLoading`, `api/services/loading/`)
  plus route-level `loading.tsx` skeletons.
- **API layer:** `api/api-config.ts`, `api-helper.ts` and one `serve-action.ts`
  per area; the API key and tokens stay on the server. Server-side errors are
  normalised in `utils/server-side-error-handler.ts`, and an invalid API key is
  handled in `utils/api-key-failure.ts`.
- **Tools:** `/tools/random`, a random value generator.
- The tenant and landlord home, tenancies and maintenance pages are placeholders
  for now.

## Source locations

- `admin/components/layout/`, `admin/components/common/`.
- `admin/constants/`: `web-routes.ts`, `navigation.ts`, `audience.ts`, `roles.ts`.
- `admin/api/`: `api-config.ts`, `api-helper.ts`, `services/`.
- `admin/app/`: `layout.tsx`, `loading.tsx`, `tenant/`, `landlord/`, `admin/`, `tools/`.
- `admin/hooks/`, `admin/types/`, `admin/utils/`.

## Not done

- Tenant and landlord dashboards, tenancies and maintenance screens have no real
  content yet. The admin overview dashboard is real; see [Admin overview](admin-overview.md).
