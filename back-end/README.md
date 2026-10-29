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

All variables are required: Django won't start if one is missing.

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

`config/.env` is git-ignored. Never commit it. When you add a new variable, add it to `config/.env.example` too.

## 7. Project layout

```
back-end/
├── config/            Settings, URLs, .env
├── common/            Shared model field sets (M, E, C, J) and constraint helpers
├── accounts/          Users, sign-in, sessions, MFA, roles, permissions, bans
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

## 8. Further reading

| Document                                                                            | Contents                                                               |
| ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `docs/authentication.md`                                                            | How sign-in, sessions, tokens, MFA, bans and permissions work          |
| `docs/schema-changes-for-diagram.md`                                                | Every schema change since spec v3, for updating the ER diagrams        |
| `accounts/permission_seed.py`                                                       | Draft permission codes per role (not yet seeded)                       |
| Spec v3 (`RentTrace_Database_Structure_and_Processes_v3.md`, kept outside the repo) | The original database design; the docs above note where it has changed |

## 9. Switching to Supabase

1. In the Supabase dashboard, make sure the project is active, then open **Connect** and copy the **Session pooler** values. They work over IPv4. Don't use the Transaction pooler (port 6543) for migrations.
2. In `config/.env`, replace the database block with the Supabase one from `.env.example` and set `DB_SSLMODE=require`.
3. Check what's already in that database before running `python manage.py migrate`: Supabase projects come with their own schemas.

## 10. Troubleshooting

| Problem                                                   | Fix                                                                                                                        |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `Cannot connect to the Docker daemon`                     | Start Docker Desktop and wait until `docker info` works.                                                                   |
| `Bind for 0.0.0.0:5433 failed: port is already allocated` | Something else uses the port. Change `"5433:5432"` in `docker-compose.yml` and `DB_PORT` in `.env` to a free port.         |
| `connection refused` on port 5433 or 6379                 | The containers aren't running. Run `docker compose up -d --wait`.                                                          |
| `ImproperlyConfigured: Set the X environment variable`    | `config/.env` is missing that variable. Compare it with `config/.env.example`.                                             |
| `failed to resolve host '...supabase.co'`                 | The Supabase project is paused or the host is wrong, or your network has no IPv6. Use the Session pooler host (section 9). |
| `ModuleNotFoundError`                                     | The virtual environment isn't active. Run `source .venv/bin/activate`, then `pip install -r requirements.txt`.             |
