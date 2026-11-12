# RentTrace back end

Django REST API for RentTrace. It runs on **PostgreSQL 17** and **Redis 8**, both provided locally by Docker.

| Part                           | Version                                        |
| ------------------------------ | ---------------------------------------------- |
| Python                         | 3.14                                           |
| Django / Django REST Framework | 5.2 / 3.18                                     |
| API docs                       | drf-spectacular (OpenAPI, Swagger UI, ReDoc)   |
| Database                       | PostgreSQL 17 (Docker locally, Supabase later) |
| Cache and rate limits          | Redis 8 (Docker)                               |

## 1. Prerequisites

- **Python 3.14**: check with `python3.14 --version`. On macOS: `brew install python@3.14`.
- **Docker Desktop**: install it from docker.com and make sure it's running. `docker info` should print server details, not "Cannot connect to the Docker daemon".

## 2. First-time setup

Run everything from the `back-end/` folder.

```bash
cd back-end

# 1. Python environment and packages (requirements-dev.txt = app packages + Ruff + pre-commit)
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install   # format and lint automatically on every git commit

# 2. Environment file
cp config/.env.example config/.env
```

Then replace both `change-me` values in `config/.env` with real secrets:

```bash
python manage.py generate_jwt_key --write                      # JWT_SIGNING_KEY, written into .env
python -c "import secrets; print(secrets.token_urlsafe(50))"   # paste as DJANGO_SECRET_KEY
```

**Changing the JWT key later** (for example after a leak, or on a schedule) uses the same command. Restart the server afterwards; everyone has to sign in again.

| Command                                                                     | Result                                                                                                                                                                                                                                                                 |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `python manage.py generate_jwt_key` or `GET /api/auth/signing-key/`         | Gives a new random key (the strongest option) to paste into `.env`                                                                                                                                                                                                     |
| `python manage.py generate_jwt_key --write`                                 | Writes a new random key into `config/.env` without printing it                                                                                                                                                                                                         |
| `python manage.py generate_jwt_key --from-words --label production --write` | Asks for your secret words (hidden), builds the key from them and writes it. The same words and label always give the same key, so you can recreate it; each label (`local`, `staging`, `production`) gives a different key. Needs at least 4 words and 20 characters. |
| `--env-file path/to/.env`                                                   | Update a different env file                                                                                                                                                                                                                                            |

A key built from words is only as strong as the words: use an unusual phrase that isn't written anywhere else, and keep it as secret as the key. `python manage.py check` warns (`accounts.W001`) when the key is shorter than 32 bytes.

```bash
# 3. Start PostgreSQL and Redis
docker compose up -d --wait

# 4. Create the tables
python manage.py migrate

# 5. Run the API
python manage.py runserver
```

The API is now at http://127.0.0.1:8000. Check it with the docs pages:

| URL                               | What                |
| --------------------------------- | ------------------- |
| http://127.0.0.1:8000/api/docs/   | Swagger UI          |
| http://127.0.0.1:8000/api/redoc/  | ReDoc               |
| http://127.0.0.1:8000/api/schema/ | OpenAPI schema file |

## 3. Daily use

```bash
cd back-end
source .venv/bin/activate
docker compose up -d --wait   # start the database and Redis (safe to run if already up)
python manage.py runserver
```

When you're done, `docker compose down` stops the containers. Your data is kept.

## 4. Docker

`docker-compose.yml` defines two services:

| Service    | Image                | Port on your machine | Data volume     |
| ---------- | -------------------- | -------------------- | --------------- |
| `postgres` | `postgres:17-alpine` | **5433**             | `postgres-data` |
| `redis`    | `redis:8-alpine`     | 6379                 | `redis-data`    |

PostgreSQL uses host port **5433**, not the usual 5432, so it doesn't clash with other PostgreSQL servers or containers on your machine. Inside Docker it's still 5432. The local database, user and password are all `renttrace`; they're for local development only.

| Task                     | Command                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------- |
| Start                    | `docker compose up -d --wait`                                                               |
| Status                   | `docker compose ps`                                                                         |
| Logs                     | `docker compose logs -f postgres` (or `redis`)                                              |
| Stop, keep data          | `docker compose down`                                                                       |
| **Reset all local data** | `docker compose down -v`, then `docker compose up -d --wait` and `python manage.py migrate` |
| Open a SQL shell         | `docker compose exec postgres psql -U renttrace -d renttrace`                               |
| Open a Redis shell       | `docker compose exec redis redis-cli`                                                       |

## 5. Formatting and lint

The code is formatted and linted with [Ruff](https://docs.astral.sh/ruff/). Settings are in `pyproject.toml`: 100-character lines, sorted imports, Django checks, and a complexity limit that keeps functions flat.

| Task                                      | Command                                 |
| ----------------------------------------- | --------------------------------------- |
| Format everything                         | `ruff format .`                         |
| Lint (auto-fix what's safe)               | `ruff check . --fix`                    |
| Check without changing files, as CI would | `ruff format --check . && ruff check .` |

**These run automatically on every commit** once you've run `pre-commit install` (first-time setup, step 1). The hook is configured in `.pre-commit-config.yaml` at the repository root and only checks `back-end/` files. It runs Ruff (lint with safe fixes, then format) plus basic checks: trailing whitespace, end of file, merge-conflict markers, valid YAML and TOML, large files, private keys.

If the hook fixes something, the commit stops so you can see the changes: run `git add` on the fixed files and commit again. To run the hook on everything by hand: `pre-commit run --all-files` (from the repository root).

For format-on-save, install the **Ruff** extension in VS Code or PyCharm; it picks up `pyproject.toml` automatically.

## 6. Database migrations

| Task                                                       | Command                                             |
| ---------------------------------------------------------- | --------------------------------------------------- |
| After changing a model, create a migration                 | `python manage.py makemigrations`                   |
| Apply migrations                                           | `python manage.py migrate`                          |
| See what's applied                                         | `python manage.py showmigrations`                   |
| Check models and migrations match (good before committing) | `python manage.py makemigrations --check --dry-run` |

Once a migration is committed, never edit or delete it. Change the model and create a new migration instead, because other people's databases have already applied the old one.

Some apps have two initial migrations (`0001` and `0002`). That's expected: their tables link to other apps that link back, so Django adds those cross-links in a second step.

## 7. Environment variables (`config/.env`)

These are required: Django won't start if one is missing.

| Variable                            | Purpose                                                                                 | Local value                               |
| ----------------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------- |
| `DJANGO_SECRET_KEY`                 | Django signing key                                                                      | Generate (section 2)                      |
| `DJANGO_DEBUG`                      | Debug mode                                                                              | `True`                                    |
| `DJANGO_ALLOWED_HOSTS`              | Allowed host names                                                                      | `localhost,127.0.0.1`                     |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Database login                                                                          | `renttrace`                               |
| `DB_HOST`, `DB_PORT`                | Database address                                                                        | `localhost`, `5433`                       |
| `DB_SSLMODE`                        | SSL to the database                                                                     | `disable` locally, `require` for Supabase |
| `REDIS_URL`                         | Cache and rate-limit store                                                              | `redis://localhost:6379/0`                |
| `JWT_SIGNING_KEY`                   | Signs our access tokens                                                                 | Generate (section 2)                      |
| `API_KEY`                           | Required in the `X-API-Key` header on every `/api/` request (the docs pages are exempt) | Empty: every `/api/` request is rejected  |

Optional, with defaults (see `config/.env.example`):

| Variable                                                        | Purpose                                                                                                                                                                                                            | Default                                         |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- |
| `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`                      | Google sign-in through Supabase                                                                                                                                                                                    | Empty: `/api/auth/google/` answers 503          |
| `EMAIL_BACKEND`                                                 | How auth emails are sent                                                                                                                                                                                           | Console: emails print in the `runserver` output |
| `DEFAULT_FROM_EMAIL`                                            | Sender of auth emails                                                                                                                                                                                              | `RentTrace <no-reply@renttrace.local>`          |
| `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN` | Gmail API login with OAuth 2.0, used with `EMAIL_BACKEND=accounts.integrations.gmail_backend.GmailApiBackend`. Get the refresh token with `python manage.py generate_gmail_refresh_token`                          | Empty                                           |
| `AUTH_LINK_BASE_URL`                                            | Base of the link in reset emails                                                                                                                                                                                   | `renttrace://auth`                              |
| `MFA_ENCRYPTION_KEY`                                            | Fernet key that encrypts admins' authenticator secrets. Generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Back it up: losing it locks out enrolled admins | Empty: MFA endpoints answer 503                 |
| `LOG_LEVEL`                                                     | How much to log: every request is `INFO`, client errors `WARNING`, server errors `ERROR`                                                                                                                           | `INFO`                                          |
| `LOG_DIR`                                                       | Folder for the daily log file `renttrace-debug-YYYYMMDD.log`. Empty: console only                                                                                                                                  | `back-end/Log/Debug`                            |
| `ADMIN_BOOTSTRAP_SECRET`                                        | Setup secret for `POST bootstrap-admin/`, which creates the first super admin once. Remove it afterwards                                                                                                           | Empty: the endpoint answers 503                 |
| `WEB_APP_URL`                                                   | The Next web app: verification emails link to its `/verify-email` page                                                                                                                                             | `http://localhost:3000`                         |

`config/.env` is git-ignored. Never commit it. When you add a new variable, add it to `config/.env.example` too.

## 8. Auth API and tests

All auth endpoints live under `/api/auth/`. Each one is a controller in `accounts/views.py` that calls one use case in `accounts/services/` (for example `sign_in/` → `services/sign_in_with_password.py`). Every other endpoint requires `Authorization: Bearer <access_token>`.

| Endpoint                    | Needs a token | What it does                                                                                                                                                                                                                     |
| --------------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST sign-up/`             | No            | Create an email/password account; sends a verification email                                                                                                                                                                     |
| `POST verify-email/`        | No            | Verify the email with the token from the link                                                                                                                                                                                    |
| `POST resend-verification/` | No            | Send a new verification link                                                                                                                                                                                                     |
| `POST bootstrap-admin/`     | Setup secret  | Create the first super admin (once); answers 409 afterwards                                                                                                                                                                      |
| `POST sign-in/`             | No            | Email/password sign-in; returns access and refresh tokens                                                                                                                                                                        |
| `POST google/`              | No            | Exchange a Supabase Google access token for our tokens                                                                                                                                                                           |
| `POST refresh/`             | No            | Swap a refresh token for new tokens (each refresh token works once)                                                                                                                                                              |
| `POST forgot-password/`     | No            | Email a reset link                                                                                                                                                                                                               |
| `POST reset-password/`      | No            | Set a new password with the reset token                                                                                                                                                                                          |
| `POST mfa/enrol/`           | Yes (admin)   | Start two-step setup; returns the secret and QR link                                                                                                                                                                             |
| `POST mfa/confirm/`         | Yes (admin)   | Confirm the first code; returns backup codes once                                                                                                                                                                                |
| `POST mfa/verify/`          | Yes           | Verify this session with a code or backup code                                                                                                                                                                                   |
| `POST sign-out/`            | Yes           | End this session                                                                                                                                                                                                                 |
| `POST change-password/`     | Yes           | Change the password; optionally sign out other devices                                                                                                                                                                           |
| `GET me/`                   | Yes           | The signed-in user, with role names, join date, last sign-in and effective permissions                                                                                                                                           |
| `PATCH profile/`            | Yes           | Edit your own `first_name`, `last_name` and `phone_number` (blank clears it). Email can't be changed. Needs `accounts.update_profile`, and admins must have finished two-step verification. Recorded in `account_access_history` |
| `POST onboarding/`          | Yes           | First-time names and role (Google users)                                                                                                                                                                                         |
| `GET signing-key/`          | No            | Generate a new random value for `JWT_SIGNING_KEY` (doesn't change the server's key)                                                                                                                                              |

### Users (admins only)

Needs an admin who has finished two-step verification (a super admin skips it). All under `/api/users/`.

| Endpoint                | What it does                                                                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /`                 | Paginated list, newest first. Query: `page`, `page_size` (max 100), `q`, `role`, `status`. A page number past the end gives the last page                     |
| `GET all/`              | Plain list of `id`, `email`, names and `roles` for dropdowns. Same `q`, `role`, `status` filters; capped at 500                                               |
| `GET <id>/`             | One user's details; 404 if missing or deleted                                                                                                                 |
| `PATCH <id>/`           | Edit `first_name`, `last_name`, `phone_number` and `role`. Email can't be changed. Only the super admin may touch admin accounts or set `ADMIN`               |
| `POST <id>/deactivate/` | Suspend the account and sign the person out everywhere. Repeating it changes nothing                                                                          |
| `POST <id>/activate/`   | Let a suspended account sign in again                                                                                                                         |
| `DELETE <id>/`          | Soft-delete the account (204) and end its sessions. The email stays reserved. An optional `reason` on deactivate, activate and delete is saved in the history |
| `POST /`                | Create a verified account with a starting password the admin chooses (no email is sent). Only the super admin may create `ADMIN` accounts                     |

### Properties (admins only)

Needs an admin who has finished two-step verification. All under `/api/properties/`. Reading needs `properties.admin_view`; everything else needs `properties.admin_manage`.

| Endpoint                       | What it does                                                                                                                                                          |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /`                        | Paginated list, newest first, with the primary owner and unit count. Query: `page`, `page_size`, `q` (name, address, owner), `status`                                 |
| `POST /`                       | Create a property for a landlord. `owner_id` must be an active landlord; they become the primary owner with 100%. `property_type` is one of `properties/catalogue.py` |
| `GET owner-options/`           | Active landlords for the owner dropdown. Query: `q`. Capped at 500                                                                                                    |
| `GET <id>/`                    | One property with its current owners and units; 404 if missing or deleted                                                                                             |
| `PATCH <id>/`                  | Edit any property field and `property_status`. Only the fields sent change. The owner can't be changed here                                                           |
| `DELETE <id>/`                 | Remove the property and its units (soft delete). 409 while any of its units has a tenancy                                                                             |
| `POST <id>/units/`             | Add a unit: `name`, `unit_type`, optional `unit_number`, `description`, `is_public`                                                                                   |
| `PATCH <id>/units/<unit_id>/`  | Edit a unit                                                                                                                                                           |
| `DELETE <id>/units/<unit_id>/` | Remove a unit. 409 while it has a tenancy                                                                                                                             |

Property and unit changes are stamped with `created_by`, `updated_by` and `row_version`. They aren't written to `business_change_history` yet, because that table hangs off the review engine.

### Public listings (no sign-in)

Anyone can browse, so these endpoints need only the API key. They are under `/api/public/listings/`, rate limited, and return public fields only: no street address, owners, private notes, private units, documents or sign-in details. A property appears only when its owner or an admin has set the listing to `AVAILABLE` or `PARTIALLY_AVAILABLE`, it is active, and at least one unit is public.

| Endpoint                     | What it does                                                                                                                                                                                                                                                                            |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /`                      | Paginated listings with cover photo, suburb, "from" rent and unit count. Query: `q`, `state`, `suburb`, `type`, `min_rent`, `max_rent` (per week, monthly and fortnightly rents are converted), `sort` (`newest`, `rent_low`, `rent_high`; unpriced last), `page`, `page_size` (max 48) |
| `GET places/`                | Every state and suburb that currently has a listing, with a count, for search pickers                                                                                                                                                                                                   |
| `GET <id>/`                  | One listing: public description, public units with rent, and photos (property and public-unit photos)                                                                                                                                                                                   |
| `GET <id>/photos/<file_id>/` | A public photo's bytes. Documents and photos of private units are a 404                                                                                                                                                                                                                 |

Landlords and admins control a listing with `POST listing/` on the property (`/api/landlord/properties/<id>/listing/` needs `properties.publish`; `/api/properties/<id>/listing/` needs `properties.admin_manage`) with `listing_status`. To go live the property must be active and have a public unit. Landlords can't set `SUSPENDED` or `ARCHIVED` and can't change a suspended listing; admins can. Units now have an optional `rent_amount` with `rent_frequency` (`WEEKLY`, `FORTNIGHTLY` or `MONTHLY`); both or neither, and an optional `max_occupants` (1 to 100): the most people who can live there.

### Property photos and files

Photos and PDF documents attached to a property, on both the admin routes (`/api/properties/<id>/files/`, needs `properties.admin_manage` to change, `properties.admin_view` to read) and the landlord routes (`/api/landlord/properties/<id>/files/`, needs `properties.update` / `properties.view`, own properties only). Files are stored with Django's default storage, which writes under `MEDIA_ROOT` (default `back-end/media`, git-ignored; back it up). To move to S3 or Supabase Storage later, change the storage backend in settings; the API doesn't change.

| Endpoint                       | What it does                                                                                                                                                                                                                                                                                               |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST files/`                  | Upload one file as `multipart/form-data`: `file`, `kind` (`PHOTO` or `DOCUMENT`), optional `caption`. Photos are JPEG or PNG, documents are PDF, up to 10 MB. The type is checked from the file's contents, not its name. Up to 30 photos and 20 documents per property. The first photo becomes the cover |
| `PATCH files/<file_id>/`       | Change the `caption` or make a photo the cover with `is_cover: true` (the previous cover is unset)                                                                                                                                                                                                         |
| `DELETE files/<file_id>/`      | Remove a file (kept in the database, marked deleted). If it was the cover, the next photo becomes the cover                                                                                                                                                                                                |
| `GET files/<file_id>/content/` | The file itself, with its real content type. Needs the same sign-in and API key as every other request, so the admin app fetches it on the server                                                                                                                                                          |

`GET <id>/` on a property also lists its `files`, each with a `unit_id` (empty for the property's own files).

**Unit files:** the same four endpoints exist per unit under `<id>/units/<unit_id>/files/…`. A file belongs to exactly one scope, the property or one unit, and the routes only reach files of their own scope (a unit file asked for through the property route, or through another unit, is a 404). Each unit has its own cover photo and its own photo and document limits. Removing a unit removes its files, never the property's.

### Landlord properties

Needs a signed-in landlord. All under `/api/landlord/properties/`. Every endpoint only sees properties the landlord currently owns (as primary or co-owner); anyone else's property answers 404. Reading needs `properties.view`, creating `properties.create`, and editing properties and units `properties.update`.

| Endpoint                       | What it does                                                                                                                        |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `GET /`                        | Paginated list of your properties, newest first. Query: `page`, `page_size`, `q` (name, address, owner), `status`                   |
| `POST /`                       | Set up a property. You become the primary owner with 100%. There is no `owner_id`. Same fields as the admin create, minus the owner |
| `GET <id>/`                    | One property with its current owners and units                                                                                      |
| `PATCH <id>/`                  | Edit fields and `property_status`. Set `ARCHIVED` to retire a property; landlords can't delete one                                  |
| `POST <id>/units/`             | Add a unit                                                                                                                          |
| `PATCH <id>/units/<unit_id>/`  | Edit a unit                                                                                                                         |
| `DELETE <id>/units/<unit_id>/` | Remove a unit. 409 while it has a tenancy                                                                                           |

### Tenancies and tenant invitations

A landlord (or an admin) creates a tenancy on a unit and invites tenants to it by email. The invitee follows the emailed link, signs in with the same verified email, and joins. Rules and errors are in `docs/features/tenant-invitations.md` (at the repository root). Under `/api/landlord/tenancies/` (needs a landlord; only your own properties) and `/api/tenancies/` (admins, all properties), with the same paths:

| Endpoint                                         | Landlord permission        | Admin permission         | What it does                                                                                                                                                |
| ------------------------------------------------ | -------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /`                                          | `tenancies.view`           | `tenancies.admin_view`   | Tenancies, newest first, with place, status, dates, tenant count and pending invites. Query: `q`, `status`, `page`. Landlords see their own properties only |
| `POST /`                                         | `tenancies.create`         | `tenancies.admin_manage` | Create a draft whole-unit tenancy: `property_unit_id`, `start_date`, optional `end_date`, `notes`                                                           |
| `GET <id>/`                                      | `tenancies.view`           | `tenancies.admin_view`   | The tenancy with its unit, property, current tenants and invitations                                                                                        |
| `POST <id>/invitations/`                         | `tenancies.manage_parties` | `tenancies.admin_manage` | Invite `email`, optionally `is_primary`. Valid for 7 days; the link is emailed after commit                                                                 |
| `POST <id>/invitations/<invitation_id>/resend/`  | `tenancies.manage_parties` | `tenancies.admin_manage` | New link and 7 more days for a pending or expired invite; the old link stops working                                                                        |
| `POST <id>/invitations/<invitation_id>/revoke/`  | `tenancies.manage_parties` | `tenancies.admin_manage` | End a pending or expired invite                                                                                                                             |
| `POST <id>/activate/`                            | `tenancies.update`         | `tenancies.admin_manage` | Start a `DRAFT` tenancy: needs a current tenant and no overlapping active tenancy on the unit                                                               |
| `POST <id>/end/`                                 | `tenancies.update`         | `tenancies.admin_manage` | End an `ACTIVE` tenancy that has started: end date becomes today if open or later; tenants leave                                                            |
| `POST <id>/cancel/`                              | `tenancies.update`         | `tenancies.admin_manage` | Cancel a `DRAFT` tenancy that never started; anyone who joined is released                                                                                  |
| `POST <id>/invitations/<invitation_id>/approve/` | `tenancies.manage_parties` | `tenancies.admin_manage` | The landlord says yes to a tenant's housemate request; the person joins if they already said yes                                                            |
| `POST <id>/invitations/<invitation_id>/decline/` | `tenancies.manage_parties` | `tenancies.admin_manage` | Decline a tenant's housemate request; it ends and the tenant and invitee are told                                                                           |

Tenants use `/api/tenant/invitations/` and need `tenancies.accept_invitation`:

| Endpoint            | What it does                                                     |
| ------------------- | ---------------------------------------------------------------- |
| `GET /`             | Pending invitations for the signed-in tenant's email (no tokens) |
| `POST accept/`      | Accept with the `token` from the email                           |
| `POST <id>/accept/` | Accept one from the list                                         |

Accepting needs the account's verified email to equal the invited email; any other failure answers the same 400 so it doesn't reveal who was invited. 409 when the invite is for the primary tenant and the tenancy already has one.

Tenants also read their own tenancies, past ones included, under `/api/tenant/tenancies/` (needs a tenant and `tenancies.view`; rules in `docs/features/tenant-tenancies.md`):

| Endpoint                                          | What it does                                                                                                                                                                                                          |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /`                                           | Every tenancy they joined, newest start first, with place, dates, rent and bond if set, the landlord's name only, and `is_current`                                                                                    |
| `GET <id>/`                                       | One of theirs, plus the other current tenants' names. Anyone else's tenancy is a 404                                                                                                                                  |
| `POST <id>/invitations/`                          | Ask to add a housemate (`email`). Needs `tenancies.invite_housemate`. It goes to the invitee and the landlord, and both have to say yes. At most 5 open per tenancy and 10 per person per day; a full unit refuses it |
| `POST <id>/invitations/<invitation_id>/withdraw/` | Take back your own request                                                                                                                                                                                            |

A unit's `max_occupants` (optional, 1 or more) caps how many current tenants a tenancy can have. It is checked on every invitation and again when someone would join. The housemate rules are in `docs/features/housemate-invitations.md`.

### Contact requests

A tenant asks a landlord to get in touch about a listing. The landlord accepts or declines; on accept each side sees the other's name, email and phone. Rules are in `docs/features/contact-requests.md` (repository root).

Tenants, under `/api/tenant/contact-requests/` (needs a tenant and `contact_requests.send`):

| Endpoint            | What it does                                                                                                                                                                  |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /`            | Ask about a listed property: `listing_id`, optional `unit_id` (an available public unit), `message` (1 to 1000 characters). One open request per property, at most 10 waiting |
| `GET /`             | Your requests, newest first. Query: `status`, `page`, `page_size`                                                                                                             |
| `GET <id>/`         | One request. `landlord` holds name, email and phone only when it is `ACCEPTED`, otherwise `null`                                                                              |
| `POST <id>/cancel/` | Withdraw a `PENDING` request                                                                                                                                                  |

Landlords, under `/api/landlord/contact-requests/` (needs a landlord and `contact_requests.respond`; only properties you own):

| Endpoint             | What it does                                                                   |
| -------------------- | ------------------------------------------------------------------------------ |
| `GET /`              | Requests for your properties. Query: `status`, `page`, `page_size`             |
| `GET <id>/`          | One request. `tenant_contact` (email, phone) is set only once it is `ACCEPTED` |
| `POST <id>/accept/`  | Accept a `PENDING` request; the tenant is emailed                              |
| `POST <id>/decline/` | Decline a `PENDING` request; the tenant is emailed                             |
| `POST <id>/revoke/`  | Take back an `ACCEPTED` request; the contact details are hidden again          |

### Notifications (everyone signed in)

An in-app inbox, so people can act without opening email. Rules, events and who is told are in `docs/features/notifications.md`. Every call is about the caller's own notifications; someone else's id is a 404. No permission code is needed beyond being signed in with two-step done.

| Endpoint                               | What it does                                            |
| -------------------------------------- | ------------------------------------------------------- |
| `GET /api/notifications/`              | Newest first. Query: `unread=true`, `page`, `page_size` |
| `GET /api/notifications/unread-count/` | `{"unread": n}`, for the bell                           |
| `POST /api/notifications/<id>/read/`   | Mark one read (safe to repeat)                          |
| `POST /api/notifications/read-all/`    | Mark every unread one read; returns `{"marked": n}`     |

A row has `kind` and `subject_id` (what it is about) plus `title` and `body`; it never holds contact details or invitation links. The `notifications` table now also holds rows with no review event (see `docs/schema-changes-for-diagram.md` §7).

### Locations (signed in)

Australian states and suburbs for address pickers, under `/api/locations/`. Needs a signed-in user (admins after two-step verification).

| Endpoint       | What it does                                                                                                                                                         |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET states/`  | The eight states and territories as `code` and `name`                                                                                                                |
| `GET suburbs/` | Suburbs and postcodes of one state. Query: `state` (required), `q` (words in the name; names starting with what you typed come first), `limit` (max 100, default 50) |

The suburb list is `locations/data/au_suburbs.csv`, built from the community-maintained [Australian postcodes](https://github.com/matthewproctor/australianpostcodes) dataset with PO boxes and large-volume recipients removed. It has no stated licence, so check it before shipping. Property `state` must be one of the state codes.

### Access (permissions, roles, grants)

Needs the `access.manage` permission. Under `/api/access/`. One rule governs every write: **you can't give or act on what you don't hold** (the super admin passes it).

| Endpoint                                 | What it does                                                                                                                                                                                            |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET permissions/`                       | Every permission, with `is_admin_only` and the roles that hold it                                                                                                                                       |
| `POST permissions/`                      | Add a permission: `code` as `module.action` (lower case), `name`, optional `is_admin_only`. Codes in the `accounts` and `access` modules are always admin-only. Codes can't be changed or deleted later |
| `PATCH permissions/<code>/`              | Rename it, change `is_admin_only` or deactivate it. You can only edit a permission you hold. It can't become admin-only while a tenant or landlord role or person holds it                              |
| `GET permissions/<code>/holders/`        | Which roles give it (including through inheritance), how many people get it through them, and who has it as an individual grant                                                                         |
| `GET grants/`                            | Every active individual grant, newest first. Query: `q` (person), `permission`, `page`, `page_size`                                                                                                     |
| `GET roles/`                             | Every role: kind, parent, holder count, its own permissions and the inherited ones                                                                                                                      |
| `POST roles/`                            | Create a custom admin role: `name`, optional `description`, `parent` and `permissions`                                                                                                                  |
| `PATCH roles/<code>/`                    | Change name, description, parent, permissions or `is_active`. Built-in roles can't be deactivated or given a parent. Cycles and chains over 5 levels are refused                                        |
| `GET roles/<code>/members/`              | The people in an admin role (paginated)                                                                                                                                                                 |
| `POST roles/<code>/members/`             | Add a person (`user_id`) to an admin role, keeping their other admin roles. Tenants and landlords are changed on their own page                                                                         |
| `DELETE roles/<code>/members/<user_id>/` | Remove a person from an admin role. An admin always keeps at least one                                                                                                                                  |
| `GET users/<id>/permissions/`            | What a person gets through their roles (with inheritance), their individual grants, and the effective list                                                                                              |
| `POST users/<id>/grants/`                | Grant a permission with a required `reason`. Re-granting reactivates the same grant                                                                                                                     |
| `DELETE users/<id>/grants/<code>/`       | Revoke a grant (it is switched off, not deleted)                                                                                                                                                        |

People get roles through `POST /api/users/` and `PATCH /api/users/<id>/` with `roles: [codes]`: one of TENANT or LANDLORD, or one or more admin roles. Role changes are recorded in `role_change_history`; grant changes in `account_access_history`. `GET auth/me/` returns the effective `permissions` and `is_admin`.

### Overview (admins only)

`GET /api/overview/` gives the admin dashboard its figures: users, properties and units, tenancies by status, tenancies ending within 60 days, invitations pending or expired, bans in force, and the latest account changes. Any admin may call it; each block is `null` unless the person holds the permission that shows it (`accounts.view`, `properties.admin_view`, `tenancies.admin_view`, `bans.view`). See `docs/features/admin-overview.md` at the repository root.

### Bans and access tokens (admins only)

Both need two-step verification done plus the permission shown. Lists are paginated like the users list (`page`, `page_size`).

| Endpoint                        | Permission      | What it does                                                                                                                                                                  |
| ------------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /api/bans/`                | `bans.view`     | Every ban, newest first, with `status` ACTIVE, EXPIRED or LIFTED. Query: `q`, `status`, `type`                                                                                |
| `POST /api/bans/`               | `bans.manage`   | Ban an `EMAIL`, an `EMAIL_DOMAIN` or an `ACCOUNT`. `reason` is required; `expires_at` is optional. Account bans end that person's sessions and write their history            |
| `POST /api/bans/<id>/lift/`     | `bans.manage`   | Lift an active ban. `reason` is required and kept on the ban. Lifting an account ban also writes the person's history                                                         |
| `GET /api/tokens/`              | `tokens.view`   | Every signed-in session (what an access token belongs to): person, device, IP, last used, expiry, `status` ACTIVE, REVOKED or EXPIRED, and `is_current`. Query: `q`, `status` |
| `POST /api/tokens/<id>/revoke/` | `tokens.revoke` | End a session: its access token stops working on the next request and its refresh token can't be used. You can't revoke the session you are using. Optional `reason`          |

Acting on an admin's account bans or sessions follows the same rule as everything else: you can't act on someone who can do more than you can. `POST /api/bans/` creates one (see `docs/features/bans-and-sessions.md`).

The full request and response shapes are in Swagger at `/api/docs/`. The rules behind them are in `docs/authentication.md`.

**Trying it locally:** sign up, then open the link from the verification email printed in the `runserver` output (it opens the web app's confirm page), or copy the token from it and send it to `verify-email/`.

**Run the tests** (needs the Docker containers running; Django creates and removes a separate test database):

```bash
python manage.py test            # everything
python manage.py test accounts   # just auth
python manage.py test accounts.tests.test_sign_up   # one use case
```

## 9. Project layout

```
back-end/
├── config/            Settings, URLs, .env
├── common/            Shared model field sets (M, E, C, J) and constraint helpers
├── accounts/          Users, sign-in, sessions, MFA, roles, permissions, bans
│   ├── models/          Tables: users.py, sessions.py, access.py
│   ├── views.py         Controllers (one class per endpoint)
│   ├── dtos/            Request bodies, one per file (sign_up.py → SignUpDto)
│   ├── resources/       Response objects, one per file (user.py → UserResource)
│   ├── urls.py          Routes
│   ├── services/        One use case per file (sign_up.py, refresh.py, …)
│   │   └── shared/      Helpers several use cases need
│   ├── tests/           One test file per use case, plus base.py (shared setup)
│   ├── security/        Token check, JWT, rate limits
│   ├── integrations/    Email and Supabase
│   └── seeds/           Seed data drafts
├── properties/        Properties, owners, units, areas (admin API and landlord API)
├── locations/         Australian states and suburbs for address pickers
├── listings/          Public browsing of listed properties (no sign-in)
├── tenancies/         Tenancies, tenants, covered areas, invitations (invite API built)
├── overview/          Figures for the admin dashboard (read-only)
├── files/             Uploaded file metadata
├── conditions/        Condition records and their versions
├── reviews/           Shared review engine: requests, decisions, disputes, removals
├── maintenance/       Maintenance issues and their status history
├── documents/         Documents and their versions
├── providers/         Service providers and categories
├── communications/    Logged external communications, and tenant contact requests
├── notifications/     Business events, notifications (the in-app inbox is built), email delivery
├── history/           Change history and timeline
├── docs/              Design notes (see below)
└── docker-compose.yml
```

## 10. Further reading

| Document                                                                            | Contents                                                                                                                         |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `AGENTS.md`                                                                         | **Coding conventions for this back end**: app layout, services, named queries, models, checks to run. Read before adding an app. |
| `docs/authentication.md`                                                            | How sign-in, sessions, tokens, MFA, bans and permissions work                                                                    |
| `docs/schema-changes-for-diagram.md`                                                | Every schema change since spec v3, for updating the ER diagrams                                                                  |
| `accounts/seeds/permissions.py`                                                     | Draft permission codes per role (not yet seeded)                                                                                 |
| Spec v3 (`RentTrace_Database_Structure_and_Processes_v3.md`, kept outside the repo) | The original database design; the docs above note where it has changed                                                           |

## 11. Switching to Supabase

1. In the Supabase dashboard, make sure the project is active, then open **Connect** and copy the **Session pooler** values. They work over IPv4. Don't use the Transaction pooler (port 6543) for migrations.
2. In `config/.env`, replace the database block with the Supabase one from `.env.example` and set `DB_SSLMODE=require`.
3. Check what's already in that database before running `python manage.py migrate`: Supabase projects come with their own schemas.

## 12. Troubleshooting

| Problem                                                   | Fix                                                                                                                         |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `Cannot connect to the Docker daemon`                     | Start Docker Desktop and wait until `docker info` works.                                                                    |
| `Bind for 0.0.0.0:5433 failed: port is already allocated` | Something else uses the port. Change `"5433:5432"` in `docker-compose.yml` and `DB_PORT` in `.env` to a free port.          |
| `connection refused` on port 5433 or 6379                 | The containers aren't running. Run `docker compose up -d --wait`.                                                           |
| `ImproperlyConfigured: Set the X environment variable`    | `config/.env` is missing that variable. Compare it with `config/.env.example`.                                              |
| `failed to resolve host '...supabase.co'`                 | The Supabase project is paused or the host is wrong, or your network has no IPv6. Use the Session pooler host (section 11). |
| `accounts.W001: JWT_SIGNING_KEY is shorter than 32 bytes` | Run `python manage.py generate_jwt_key --write` and restart the server.                                                     |
| `ModuleNotFoundError`                                     | The virtual environment isn't active. Run `source .venv/bin/activate`, then `pip install -r requirements-dev.txt`.          |
