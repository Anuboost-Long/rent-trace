# Admin design alignment

## Status — 25 November 2026

In progress. Planned in phases, using only APIs that already exist (no back-end changes):

1. Foundations: Figma design tokens, the Inter font and restyled shared components (whole app)
2. Admin shell: navy sidebar, top bar, new menu
3. Sign-in and MFA screens (Figma A1)
4. Accounts list and detail (A4)
5. Team and permissions (A5)
6. Overview (A2, partial)
7. No access and Session ended (A8)
8. Sweep of the Operations, tenant and landlord pages

Nothing has been seen in a browser yet.

## Goal

The admin area of the web app matches the RentTrace Figma file (`iOHqEujF6MB5mDn1J01Q1i`,
"ADMIN SCREENS") wherever the API already gives the data the screen needs. Tenant and landlord
pages keep their layouts but share the new look, since they stay as API test pages.

## How it works

- **Look:** colours, spacing, radius and type come from the Figma variables, defined once as
  `--rt-*` tokens in `admin/app/globals.css` and exposed as Tailwind colours (`text-fg-secondary`,
  `border-default`, `bg-subtle`, `bg-brand`, `text-error` and so on). The font is Inter.
- **Admin menu:** Overview, Accounts (`/admin/users`), Team and permissions (`/admin/access`).
  The admin screens that are not in Figma sit under **Operations**: Properties, Tenancies,
  Contact requests, Tradespeople, Maintenance, Bans, Access tokens and Notifications. Cases,
  Removal requests and Audit log are hidden until their APIs exist.
- **Reasons:** suspending, banning and changing an admin's permissions all ask for a reason,
  as Figma does.

## Source locations

- Admin: `admin/app/globals.css`, `admin/app/layout.tsx`, `admin/components/common/`,
  `admin/components/layout/`, `admin/constants/navigation.ts`
- Admin pages: `admin/app/auth/`, `admin/app/(app)/admin/users/`, `admin/app/(app)/admin/access/`,
  `admin/app/(app)/admin/page.tsx`, `admin/components/overview/`

## Not done

Figma shows things the API can't give yet:

- **Accounts list:** no sign-in method, linked tenancy or properties, or banned state per row.
- **Account detail:** no suspension reason or who suspended, no per-account activity, no open items.
- **Sign-in:** locked, wrong sign-in method and suspended all get the same "Email or password is
  incorrect." error, by design, so the separate Figma states are not shown.
- **Overview:** no "Needs you" queue (cases), removal requests or email delivery failures.
- **Not built at all:** Cases (A3), Removal requests (A6) and Audit log (A7) have no API.
- **Permission codes** differ from Figma (`reviews.decide` rather than `cases.decide`); the real
  codes are shown.
- **Dark mode:** Figma has no dark theme, so the app is light only for now.
