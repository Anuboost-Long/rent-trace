# Agent instructions — RentTrace back end

Read this before changing anything in `back-end/`. These conventions were agreed with the team and override Django's defaults and habits from training data. **`accounts/` is the reference implementation**: when unsure, copy how it does it.

How to run, test and configure the project is in `README.md`. Business rules are in:

- `docs/authentication.md`: sign-in, sessions, tokens, MFA, bans, permissions.
- `docs/schema-changes-for-diagram.md`: every schema change since spec v3.
- Spec v3 (`RentTrace_Database_Structure_and_Processes_v3.md`, kept outside the repo): the original database design. Where the docs above disagree with it, the docs win.

## 1. App layout (.NET style)

Every app looks like `accounts/`. Main files sit at the top; helpers sit in folders named for what they do.

```
<app>/
├── models/            tables, split by topic (users.py, sessions.py, …), re-exported in __init__.py
├── views.py           controllers: one APIView class per endpoint
├── urls.py            routes
├── dtos/              request bodies, ONE class per file: sign_up.py → SignUpDto
├── resources/         response objects, ONE class per file: user.py → UserResource
├── services/          ONE use case per file, ONE public function: sign_up.py → sign_up()
│   └── shared/        helpers several use cases need, grouped by topic
├── tests/             ONE test file per use case: test_sign_up.py; shared setup in base.py
├── security/          request protection (auth classes, tokens, throttles), if the app needs it
├── integrations/      outside services (email, external APIs), if the app needs it
├── seeds/             seed data drafts
└── migrations/
```

Rules:

- **No `serializers.py`, `services.py` or `tests.py` single files.** Use the folders above.
- Each package `__init__.py` re-exports its public names, so callers write `services.sign_up(...)`, `dtos.SignUpDto` and `resources.UserResource`.
- Django's "views" are the **controllers** (Django calls MVC "MVT"). Controllers only validate the DTO, call one service and return a resource. No business logic in views.
- Helpers in `services/shared/` don't get a leading underscore, because other files import them. A leading underscore means "private to this file".
- Test base classes must not be named `Test*` (for example `AuthApiTestCase`), so the test runner doesn't collect them.

## 2. Services

- **Services are plain functions, not classes.** A Python module already plays the role of a static class; dependencies are imported, and tests replace them with `mock.patch`. Use a class only for something with state, configuration or interchangeable implementations (like Django email backends), or for data carriers (frozen `@dataclass`, for example `Device` and `SignedIn`).
- **Flat control flow:** use guard clauses and early returns, with at most one level of nesting per function. No `if/elif` chains inside `try` or `with` blocks.
- **Transactions:** decorate the function with `@transaction.atomic`; don't use `with transaction.atomic():` blocks.
- **When a failure must still be saved** (a lock counter, a revoked session, an email queued for after commit): put the transactional work in a private `_attempt()` that **returns** the result or the error. The public function raises only after the commit. See `services/sign_in_with_password.py`. Raising inside the transaction would roll the failure record back.
- **Emails go out after commit:** `send_after_commit(...)` (that's `transaction.on_commit`). A failed email must never roll back a committed action.
- Group related arguments in a frozen dataclass rather than passing five or more loose arguments (for example `Applicant` in `services/sign_up.py`).
- Errors use DRF exceptions (`ValidationError`, `AuthenticationFailed`, `PermissionDenied`). Convert Django's own `ValidationError` before it reaches DRF, as `check_password_strength` does; otherwise it becomes a 500.

## 3. Database queries: named QuerySets

Services must read like sentences. Write the Django lookup syntax (`field__lookup`, `Q(...)`, `F(...)`, `select_related`) **once**, inside a named method on the model's QuerySet, and call it by name.

```python
# models/users.py
class BanQuerySet(models.QuerySet):
    def active(self, now):
        return self.filter(lifted_at__isnull=True, is_deleted=False).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        )


class Ban(MutableRecord):
    ...
    objects = BanQuerySet.as_manager()


# services/shared/account_rules.py
Ban.objects.active(now).for_identity(email_normalized).exists()
```

- **Name a query** when it encodes a business rule (an active ban, unused links, open sessions), has several conditions, is reused, or needs `select_related`.
- **Leave it plain** when it's trivial: `create(...)`, `get(pk=...)`, `get(code=...)`, `filter(user=user)`.
- Methods are chainable and named for what they mean: `with_email`, `password_accounts`, `not_deleted`, `unverified`, `open(now)`, `matching(token_hash)`.
- They work on related managers too: `user.role_bridges.active()`.
- This is the equivalent of EF extension methods on `IQueryable<T>`. Don't add a separate repository layer.

## 4. Models

- **Table names:** set `db_table` explicitly to the spec's name. Many-to-many link tables use the `_bridge` suffix (`user_role_bridge`).
- **Field sets from `common/models.py`:**
  - `MutableRecord` (M): business rows; includes soft delete and `row_version`.
  - `EventRecord` (E): append-only history and versions.
  - `CatalogueRecord` (C): reference data with `is_active`.
  - `LinkRecord` (J): attachments.
- **Subclassing a field set's Meta:** use `class Meta(MutableRecord.Meta):` and start `constraints` with `*MutableRecord.Meta.constraints`.
- **Foreign keys:** always `models.PROTECT`, never cascading. Removal is a soft delete.
- **Enums:** module-level `TextChoices` (a nested `Meta` can't see names defined inside the model class), stored in a `TextField`, plus a CHECK via `enum_check(table, field, Choices)`.
- **Nullable fields:** every `null=True` also gets `blank=True`. Required text that mustn't be empty or only whitespace gets `nonblank_check(table, field)`.
- **Constraint names:** `ck_<table>_<what>` and `uq_<table>_<what>`. **Index names:** `ix_…`, at most 30 characters (a Django limit).
- **Rules inside a row** go in the database: CHECK constraints and partial unique constraints. Rules across tables go in services (or triggers, later).
- **Money:** `DecimalField(max_digits=12, decimal_places=2)` with a CHECK that it's ≥ 0.
- **Primary keys:** `id` comes from `DEFAULT_AUTO_FIELD` (a BigAutoField, which is an identity column on PostgreSQL). Don't declare it.

## 5. Migrations

- Run `python manage.py makemigrations` after every model change. Never edit or delete a migration once it's committed: add a new one.
- Data migrations: `RunPython(forward, backward)`. Django always calls these as `fn(apps, schema_editor)`; name the second parameter `_schema_editor` when it's unused. Removing it breaks the migration with a `TypeError`.

## 6. Security rules that apply everywhere

- Never reveal whether an email has an account: sign-in, sign-up and reset replies are the same in every case. The account owner learns the details by email.
- Store tokens only as SHA-256 hashes, and passwords only through `make_password`.
- Never put credentials or tokens in logs, `business_events` payloads or responses (other than the one response that issues them).
- Every protected request re-checks the session (not revoked or expired) and the account (active, not deleted, not banned). That's `security/authentication.py`.

## 7. Before you say you're done

Run all of these from `back-end/` with the Docker containers up:

```bash
ruff format .                                       # format (config in pyproject.toml)
ruff check .                                        # lint; must report "All checks passed!"
python manage.py check
python manage.py makemigrations --check --dry-run   # models and migrations match
python manage.py test                               # or: python manage.py test <app>.tests.test_<use_case>
python manage.py spectacular --validate --fail-on-warn --file /dev/null
```

- When you move or rename files, search for stale imports and paths, including in `README.md`, `docs/` and `config/settings.py`.
- Never delete a file before its replacement passes the tests.
- Code style is Ruff's: don't hand-format, and don't silence a lint rule inline (`# noqa`) without saying why. A complexity error (`C901`, over 6 branches) means the function needs splitting or flattening, not a higher limit.
- Never commit `config/.env`. When you add a setting, add it to `config/.env.example` and the README's environment table.

## 8. Open questions (ask the team before assuming)

- Admin sign-in, MFA, the admin panel's cookie handling and the devices screen aren't built yet (`docs/authentication.md`, "Open items").
- The permission codes in `accounts/seeds/permissions.py` are a draft awaiting review; they aren't seeded yet.
