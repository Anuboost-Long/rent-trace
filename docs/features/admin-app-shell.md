# Admin app shell

## Status — 13 November 2026

Shipped 11 November 2026; the `(site)` route group was added after it and is in
progress (see [Public listings](public-listings.md)). On 13 November the four sidebar
layouts became one shared layout (below); that change is type-checked but not yet clicked through.

## Goal

One Next.js app serves tenants, landlords and admins, each with its own area,
navigation and permissions, built from shared components.

## How it works

- **Three audiences:** `/tenant` (site header and tabs), `/landlord` and `/admin` (sidebar
  shell). Routes and nav items live in `constants/web-routes.ts` and `constants/navigation.ts`.
- **One sidebar shell for the whole signed-in app.** `/admin`, `/landlord`, `/account` and
  `/invitations` live in the route group `app/(app)/` (the group does not change any URL). Its one
  layout (`audience-layout`) checks the person is signed in and renders the sidebar and navbar
  **once**. The shell stays mounted as you move between those sections, so collapsing the sidebar
  holds on every page; the collapsed choice is also kept in the `sidebar_collapsed` cookie for the
  next visit. The nav items follow the section in the URL (`/admin` shows the admin nav,
  `/landlord` the landlord nav; `/account` and `/invitations` show the nav for the person's own
  audience). `/admin` and `/landlord` each have a small layout that only checks the person belongs
  there and sends them home if not (`components/layout/require-audience.tsx`); it renders no
  shell. No page renders the sidebar itself.
- **Detail pages** put a bordered **Back** button on its own line with the breadcrumb trail beneath
  it, so the control and the trail can be told apart at a glance.
- **Permissions in the UI:** the `Can` component shows or hides controls from the
  signed-in user's effective permissions. The back end still enforces them.
- **Shared components** (`components/common/`): button, text, select, check,
  radio, text-area, combobox and date inputs (the date input is our own month
  calendar, not the browser's; it keeps its value in a hidden field and takes a
  `min` date), data table with pagination, confirm
  dialog, loading host, modal, spinner and skeletons.
- **Loading:** a global loading state (`useLoading`, `api/services/loading/`)
  plus route-level `loading.tsx` skeletons.
- **Loading skeletons** match the page they stand in for (`components/layout/page-skeletons.tsx`):
  `ListSkeleton` (filter bar and rows), `DetailSkeleton` (breadcrumb, title, label/value rows, a
  people section), `FormSkeleton` (labelled fields and a button), `DashboardSkeleton`,
  `CardsSkeleton` and `HomePanelSkeleton` (tenant pages). Where a page already shows its title
  outside the loading boundary the skeleton has no title of its own; pages that load whole
  (detail and edit pages) include one. The generic `ContentSkeleton` is only for route-level
  `loading.tsx` files, where the page shape is not known. Public site skeletons live in
  `components/site/skeletons.tsx` (home, results grid, listing detail).
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
- `admin/app/`: `layout.tsx`, `loading.tsx`, `tenant/`, `(site)/`, `tools/`, and `(app)/` with
  `layout.tsx`, `landlord/`, `admin/`, `account/`, `invitations/`.
- `admin/hooks/`, `admin/types/`, `admin/utils/`.

## Not done

- Tenant and landlord dashboards, tenancies and maintenance screens have no real
  content yet. The admin overview dashboard is real; see [Admin overview](admin-overview.md).
