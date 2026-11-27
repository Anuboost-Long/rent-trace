# Continuous integration

## Status — 27 November 2026

Built; first run on `main` passed. A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every pull request and on
every push to `main`, so the checks no longer depend on someone running them locally.

## What it runs

- **Back end checks** (Postgres 17 and Redis 8 as service containers, the same images as
  `back-end/docker-compose.yml`, throwaway secrets generated per run): a guard that every app with
  tests is in a test group, `ruff check`, `ruff format --check`, `manage.py check`,
  `makemigrations --check --dry-run` and `spectacular --validate --fail-on-warn`.
- **Back end tests (1) to (4):** the test suite split by app into four groups of about 200 tests that
  run side by side (the groups are listed in `.github/workflows/ci.yml`; one run took about 14
  minutes as a single job). Add a new app's name to a group, or the guard fails the checks job.
- **Admin app:** `next typegen`, `tsc --noEmit`, `eslint .`, `npm test`, and `next build`.

All of them show as checks on the pull request. Nothing is deployed.

## To do on GitHub

Make the two checks required for `main` (Settings, Branches, branch protection: "Require status
checks to pass", then pick **Back end checks**, the four **Back end tests** groups and **Admin app**). Without that the checks report but do not
block a merge.

## Not done

Deployment, a mobile job (there is no mobile app in this repo yet), and caching the Next.js build.
