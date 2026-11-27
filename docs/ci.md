# Continuous integration

## Status — 27 November 2026

In progress. A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every pull request and on
every push to `main`, so the checks no longer depend on someone running them locally.

## What it runs

- **Back end** (Postgres 17 and Redis 8 as service containers, the same images as
  `back-end/docker-compose.yml`, throwaway secrets generated per run): `ruff check`, `ruff format
  --check`, `manage.py check`, `makemigrations --check --dry-run`, `spectacular --validate
  --fail-on-warn`, then the whole test suite in parallel.
- **Admin app:** `next typegen`, `tsc --noEmit`, `eslint .`, `npm test`, and `next build`.

Both jobs show as checks on the pull request. Nothing is deployed.

## To do on GitHub

Make the two checks required for `main` (Settings, Branches, branch protection: "Require status
checks to pass", then pick **Back end** and **Admin app**). Without that the checks report but do not
block a merge.

## Not done

Deployment, a mobile job (there is no mobile app in this repo yet), and caching the Next.js build.
