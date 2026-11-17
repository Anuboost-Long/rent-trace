# Date display

## Status — 16 November 2026

Shipped. Typecheck and lint pass. Walked through in Chrome as the test landlord in a UTC+11
zone: "Member since" for an account created at 15:56 UTC on 13 Nov now reads 14 Nov; notification
times show local time (`15 Nov 2026, 18:56 GMT+11`); tenancy start and end dates on the tenancy
list match the stored values exactly.

## Goal

Everyone sees times in their own time zone, and calendar dates never move by a day.

## How it works

- **Timestamps** (created, decided, expires, reported, scheduled, completed, observed, last
  sign-in and the like) are real moments. They show in the viewer's time zone, for example
  `16 Nov 2026, 09:30 GMT+11`. The server cannot know the viewer's zone, so the first paint is in
  UTC and the browser switches it to local time straight away.
- **Calendar dates** (tenancy start and end, tenant joined and left, the date picker) have no
  time of day. They show exactly as stored and are never shifted by a time zone, so a 1 December
  start never reads as 30 November.
- A timestamp is formatted by `LocalTime`; a calendar date by `formatDate`. Passing a timestamp
  to `formatDate` is a bug.

## Source locations

- `admin/utils/format-date.test.ts`: run with `npm test` in `admin/` (Node's built-in runner).
- `admin/utils/format-date.ts`: `formatDate` (calendar dates, UTC) and `formatInstant`.
- `admin/components/common/local-time.tsx`: `LocalTime`, used wherever a timestamp is shown.

## Not done

- The mobile app shows no dates yet, so there is nothing to change there. Use these two formatters if it starts to.
- Browser-checked in one time zone only; the unit test also covers Sydney.
- The first paint of a timestamp is in UTC until the browser takes over.
