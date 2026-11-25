# Admin design alignment

## Status — 25 November 2026

All eight phases are built, using only APIs that already exist (no back-end changes). Type check,
lint and `npm test` pass. `next build` compiled every route and then stopped at Next.js's
security-version check, which is separate from this work. **Nothing has been seen in a browser
yet**, so every screen below is unverified against Figma.

1. Foundations: Figma design tokens, the Inter font and restyled shared components (whole app)
2. Admin shell: navy sidebar, top bar, new menu
3. Log in and MFA screens (Figma A1). See [Authentication](authentication.md).
4. Accounts list and detail (A4). See [Admin users](admin-users.md).
5. Team and permissions (A5). See [Access control](access-control.md).
6. Overview (A2, partial). See [Admin overview](admin-overview.md).
7. No access and Session ended (A8)
8. Sweep: status badges in the list tables, and headings on the Figma type scale

## Goal

The admin area of the web app matches the RentTrace Figma file (`iOHqEujF6MB5mDn1J01Q1i`,
"ADMIN SCREENS") wherever the API already gives the data the screen needs. Tenant and landlord
pages keep their layouts but share the new look, since they stay as API test pages.

## How it works

- **Look:** colours, radius, shadow and type come from the Figma variables, defined once as
  `--rt-*` tokens in `admin/app/globals.css` and exposed as Tailwind classes:
  - text colours: `text-fg-primary`, `-secondary`, `-tertiary`, `text-fg-brand`, `text-on-brand`
  - backgrounds: `bg-subtle`, `bg-muted`, `bg-brand`, `bg-brand-subtle`, `bg-admin`, `bg-admin-active`
  - borders: `border-default`, `border-strong`, `border-brand-border`
  - status colours: `text-error` / `-success` / `-warning` / `-attention` / `-neutral`, each with
    `-background`, `-border` and `-accent`
  - type scale: `text-display`, `text-heading`, `text-section`, `text-body`, `text-body-sm`,
    `text-caption`

  The font is Inter. The old `text-foreground/70`-style classes were rewritten to these across the
  app.
- **Shared components:**
  - Buttons: `primary` (brand), `secondary` (outlined; `quiet` is the old name for it) and `danger`.
  - Inputs, the data table (card style, optional whole-row link through `rowHref`) and the
    confirm dialog (optional required reason through `reasonLabel`).
  - New: `StatusBadge`, `Card`, `Avatar`, `FilterChips`, `SwitchInput`, `OtpInput`, `NoAccess`
    and `LoadError`.
- **Admin menu:** Overview, Accounts (`/admin/users`), Team and permissions (`/admin/access`). The
  admin screens that are not in Figma sit under **Operations**: Properties, Tenancies, Contact
  requests, Tradespeople, Maintenance, Bans, Access tokens and Notifications. Cases, Removal
  requests and Audit log are hidden until their APIs exist.
- **Reasons:** suspending, reactivating, banning and changing an admin's permissions all ask for a
  reason, as Figma does.
- **No access:** an admin page that gets a 403 shows a "You don't have permission to see this"
  panel instead of a bare error line.
- **Session ended:** when a session can't be refreshed, log in shows "Your session ended".
- **Status badges:** list tables show statuses as coloured badges. The colour for each status is
  in `admin/constants/status-tones.ts`; anything not listed is grey.

## Source locations

- Admin: `admin/app/globals.css`, `admin/app/layout.tsx`, `admin/components/common/`,
  `admin/components/layout/`, `admin/constants/navigation.ts`, `admin/constants/status-tones.ts`,
  `admin/proxy.ts`
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

Other gaps:

- **Dark mode:** Figma has no dark theme, so the app is light only for now.
- **Repeated titles:** list pages that already had a heading (Bans, Properties and others) repeat
  the page title under the top bar. Those headings are shared with tenant pages, which have no top
  bar, so they were kept.
- **Last active** shows a date, not "Today" or "3 days ago" as in Figma.
