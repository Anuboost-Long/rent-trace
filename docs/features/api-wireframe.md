# API wireframe pages

## Status — 27 November 2026

Built. A bare test UI for the reviews and documents APIs, so nobody has to hand-write request
bodies. It is a wireframe: plain forms and raw JSON, no styling, for the front-end teammate to replace
with the real screens.

## Goal

Let a developer or tester sign in as a tenant, landlord or admin and exercise every reviews and
documents endpoint from a form: pick the action, fill the fields, see the status and response.

## How it works

- **Routes** (signed in, like every other page): `/tools/wireframe` (index: choose a role and an id),
  `/tools/wireframe/tenant/<tenancyId>`, `/tools/wireframe/landlord/<unitId>`,
  `/tools/wireframe/admin` (queues; a unit id for the lookups). Only available when the app is not in
  production, or when `WIREFRAME_ENABLED=true`; otherwise a 404.
- **Each API is one entry** in a spec file (method, path, fields). The page turns an entry into a
  form: `{placeholders}` in the path become number fields, the idempotency key is generated for you,
  files become file pickers, lists of ids are comma separated, and `GET` entries load on open. The
  result shows the HTTP status and the JSON.
- **Calls go through one server action** that checks the path against an allowlist (reviews and
  documents routes only) and sends it to the API with the signed-in person's session, so the API's own
  permission checks still apply. Photo and document files download through a small route.
- **Covered:** condition reports (add, photos, withdraw, answer, escalate), asking for more information,
  corrections, removal requests, documents (publish, version, confirm, flag, read), the admin queues,
  and a super admin acting for a landlord or tenant.

## Checked

Typecheck and lint are clean; `npm test` (6 tests, including the path allowlist). In Chrome on a
production build with `WIREFRAME_ENABLED=true`, signed in as a tenant: the index renders, the report
and correction lists load on open, and filling the "Reports: add" form created a report (no JSON
written by hand). **Not seen:** the landlord and admin pages, file uploads from the file pickers, and
the download route.

## Source locations

- Admin app: `admin/app/tools/wireframe/` (`spec.ts`, `actions.ts`, `call-form.tsx`, the role pages,
  `download/route.ts`).

## Not done

Styling, real screens, and any API outside reviews and documents.
