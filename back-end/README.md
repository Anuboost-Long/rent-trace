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

# 1. Python environment and packages
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Environment file
cp config/.env.example config/.env
```

Then open `config/.env` and replace both `change-me` values with real secrets. Generate each one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Use a different value for `DJANGO_SECRET_KEY` and `JWT_SIGNING_KEY`.

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

## 5. Database migrations

| Task                                                       | Command                                             |
| ---------------------------------------------------------- | --------------------------------------------------- |
| After changing a model, create a migration                 | `python manage.py makemigrations`                   |
| Apply migrations                                           | `python manage.py migrate`                          |
| See what's applied                                         | `python manage.py showmigrations`                   |
| Check models and migrations match (good before committing) | `python manage.py makemigrations --check --dry-run` |

Once a migration is committed, never edit or delete it. Change the model and create a new migration instead, because other people's databases have already applied the old one.

Some apps have two initial migrations (`0001` and `0002`). That's expected: their tables link to other apps that link back, so Django adds those cross-links in a second step.

## 6. Environment variables (`config/.env`)

These are required: Django won't start if one is missing.

| Variable                            | Purpose                    | Local value                               |
| ----------------------------------- | -------------------------- | ----------------------------------------- |
| `DJANGO_SECRET_KEY`                 | Django signing key         | Generate (section 2)                      |
| `DJANGO_DEBUG`                      | Debug mode                 | `True`                                    |
| `DJANGO_ALLOWED_HOSTS`              | Allowed host names         | `localhost,127.0.0.1`                     |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Database login             | `renttrace`                               |
| `DB_HOST`, `DB_PORT`                | Database address           | `localhost`, `5433`                       |
| `DB_SSLMODE`                        | SSL to the database        | `disable` locally, `require` for Supabase |
| `REDIS_URL`                         | Cache and rate-limit store | `redis://localhost:6379/0`                |
| `JWT_SIGNING_KEY`                   | Signs our access tokens    | Generate (section 2)                      |

Optional, with defaults (see `config/.env.example`):

| Variable                                   | Purpose                                        | Default                                         |
| ------------------------------------------ | ---------------------------------------------- | ----------------------------------------------- |
| `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` | Google sign-in through Supabase                | Empty: `/api/auth/google/` answers 503          |
| `EMAIL_BACKEND`                            | How auth emails are sent                       | Console: emails print in the `runserver` output |
| `DEFAULT_FROM_EMAIL`                       | Sender of auth emails                          | `RentTrace <no-reply@renttrace.local>`          |
| `AUTH_LINK_BASE_URL`                       | Base of links in verification and reset emails | `renttrace://auth`                              |

`config/.env` is git-ignored. Never commit it. When you add a new variable, add it to `config/.env.example` too.

## 7. Auth API and tests

All auth endpoints live under `/api/auth/`. Each one is a controller in `accounts/views.py` that calls one use case in `accounts/services/` (for example `sign_in/` → `services/sign_in_with_password.py`). Every other endpoint requires `Authorization: Bearer <access_token>`.

| Endpoint                    | Needs a token | What it does                                                        |
| --------------------------- | ------------- | ------------------------------------------------------------------- |
| `POST sign-up/`             | No            | Create an email/password account; sends a verification email        |
| `POST verify-email/`        | No            | Verify the email with the token from the link                       |
| `POST resend-verification/` | No            | Send a new verification link                                        |
| `POST sign-in/`             | No            | Email/password sign-in; returns access and refresh tokens           |
| `POST google/`              | No            | Exchange a Supabase Google access token for our tokens              |
| `POST refresh/`             | No            | Swap a refresh token for new tokens (each refresh token works once) |
| `POST forgot-password/`     | No            | Email a reset link                                                  |
| `POST reset-password/`      | No            | Set a new password with the reset token                             |
| `POST sign-out/`            | Yes           | End this session                                                    |
| `POST change-password/`     | Yes           | Change the password; optionally sign out other devices              |
| `GET me/`                   | Yes           | The signed-in user                                                  |
| `POST onboarding/`          | Yes           | First-time names and role (Google users)                            |

The full request and response shapes are in Swagger at `/api/docs/`. The rules behind them are in `docs/authentication.md`.

**Trying it locally:** sign up, then copy the token from the verification email printed in the `runserver` output and send it to `verify-email/`.

**Run the tests** (needs the Docker containers running; Django creates and removes a separate test database):

```bash
python manage.py test            # everything
python manage.py test accounts   # just auth
python manage.py test accounts.tests.test_sign_up   # one use case
```

## 8. Project layout

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
├── properties/        Properties, owners, units, areas
├── tenancies/         Tenancies, tenants, covered areas, invitations
├── files/             Uploaded file metadata
├── conditions/        Condition records and their versions
├── reviews/           Shared review engine: requests, decisions, disputes, removals
├── maintenance/       Maintenance issues and their status history
├── documents/         Documents and their versions
├── providers/         Service providers and categories
├── communications/    Logged external communications
├── notifications/     Business events, notifications, email delivery
├── history/           Change history and timeline
├── docs/              Design notes (see below)
└── docker-compose.yml
```

## 9. Further reading

| Document                                                                            | Contents                                                                                                                         |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `AGENTS.md`                                                                         | **Coding conventions for this back end**: app layout, services, named queries, models, checks to run. Read before adding an app. |
| `docs/authentication.md`                                                            | How sign-in, sessions, tokens, MFA, bans and permissions work                                                                    |
| `docs/schema-changes-for-diagram.md`                                                | Every schema change since spec v3, for updating the ER diagrams                                                                  |
| `accounts/seeds/permissions.py`                                                     | Draft permission codes per role (not yet seeded)                                                                                 |
| Spec v3 (`RentTrace_Database_Structure_and_Processes_v3.md`, kept outside the repo) | The original database design; the docs above note where it has changed                                                           |

## 10. Switching to Supabase

1. In the Supabase dashboard, make sure the project is active, then open **Connect** and copy the **Session pooler** values. They work over IPv4. Don't use the Transaction pooler (port 6543) for migrations.
2. In `config/.env`, replace the database block with the Supabase one from `.env.example` and set `DB_SSLMODE=require`.
3. Check what's already in that database before running `python manage.py migrate`: Supabase projects come with their own schemas.

## 11. Troubleshooting

| Problem                                                   | Fix                                                                                                                         |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `Cannot connect to the Docker daemon`                     | Start Docker Desktop and wait until `docker info` works.                                                                    |
| `Bind for 0.0.0.0:5433 failed: port is already allocated` | Something else uses the port. Change `"5433:5432"` in `docker-compose.yml` and `DB_PORT` in `.env` to a free port.          |
| `connection refused` on port 5433 or 6379                 | The containers aren't running. Run `docker compose up -d --wait`.                                                           |
| `ImproperlyConfigured: Set the X environment variable`    | `config/.env` is missing that variable. Compare it with `config/.env.example`.                                              |
| `failed to resolve host '...supabase.co'`                 | The Supabase project is paused or the host is wrong, or your network has no IPv6. Use the Session pooler host (section 10). |
| `ModuleNotFoundError`                                     | The virtual environment isn't active. Run `source .venv/bin/activate`, then `pip install -r requirements.txt`.              |
