# Tenant area

## Status — 12 November 2026

In progress, not verified. Written before the code; updated when it lands.

## Goal

A signed-in tenant stays inside the same site they browse as a visitor: the same
header and footer, with their own sections for tenancies, contact requests and
maintenance. It should feel like the rental site, not like the admin dashboard.

## How it works

- Everything under `/tenant` uses the **site layout** (header with "Browse rentals",
  account menu, footer) instead of the sidebar shell that admins and landlords use.
- A row of tabs under the header switches between the tenant's sections: Overview,
  Tenancies, Contact requests, Maintenance. The tab for the current page is marked.
  Tabs scroll sideways on a narrow screen.
- Page content sits in the same centred column as the public pages.
- Only tenants may open `/tenant`. Anyone else is sent to the home page. A tenant
  who still has to enrol or verify two-step sign-in is sent to that step first.
- The signed-in person is available to client components, so `Can` and the contact
  request buttons work as before.

## Source locations

- `admin/app/tenant/layout.tsx`, `admin/components/layout/tenant-layout.tsx`,
  `admin/components/layout/tenant-nav.tsx`, `admin/components/layout/user-provider.tsx`.
- Tabs come from `Navigation.tenant` in `admin/constants/navigation.ts`.

## Not done

- Overview, Tenancies and Maintenance have no content yet. A tenant's tenancies and
  rental history need a tenant-side API (none exists: the back end only has the
  invitation endpoints and contact requests for tenants).
- Landlords still use the sidebar shell.
