# Action alerts

## Status — 28 November 2026

Built; typecheck, lint, unit tests and the production build pass. **Not yet checked in a browser**: the stacking, the auto-dismiss timing, and that an alert shows above an open dialog.

## Goal

Everyone using the admin app gets a short message when something they did worked or failed, instead of the screen changing silently.

## How it works

- A success alert (green, "Profile saved", "3 files uploaded", "Tenancy ended") disappears after 4 seconds. A failure alert (red) shows the server's message and stays 7 seconds. Both can be dismissed with the close button.
- At most four show at once. The same message is not shown twice at the same time.
- Alerts sit bottom-right on desktop and full width at the bottom on a phone. They use the browser's top layer, so they show above an open dialog. Failures are announced to screen readers as alerts, successes as status.
- Every form and action hook raises a failure alert through `hooks/useApiError.ts`, which replaces the old error state. The inline error next to the field or in the dialog stays as before.
- Success alerts are raised in each hook next to its refresh or redirect, named for the action ("Permission granted", "Tenancy cancelled").
- Standalone buttons (revoke token, lift ban, accept invitation, mark all as read) raise their own.

## Source locations

- `admin/utils/toast.ts`: the store and `toast.success` / `toast.error`.
- `admin/components/common/toast/toast-host.tsx`: renders the alerts, mounted once in `components/layout/config.tsx`.
- `admin/hooks/useApiError.ts`: failure state plus alert.
- `admin/hooks/form/*.ts`: success messages.

## Not done

- Alerts from actions that do not go through a hook (sign-in, verify email, Google callback) show only inline errors.
- No undo links on alerts.
