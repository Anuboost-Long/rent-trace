# Profile pictures

## Status — 27 November 2026

API built; no screens. Back end: 9 tests pass in `accounts/tests/test_profile_picture.py`, and the accounts,
users and access suites still pass (219); ruff, migration check and OpenAPI validation are clean. In
Chrome on a production build, as a tenant: the wireframe form uploaded a picture, the profile then
showed `picture_id`, and the image downloaded as a PNG of the right size. **Not seen:** as a landlord or
admin, the other viewers (housemate, landlord, stranger; these are covered by the tests), and any screen.

## Goal

Every person who signs in — a tenant, a landlord or an admin — can have a profile picture, so the
people they deal with can recognise them.

## How it works

Decided 27 November 2026. Tenants, landlords and admins are all `users`, so one column and one set of
endpoints covers every profile.

- **Where it is stored:** a new nullable column `users.avatar_file` pointing at a `files` row (a JPEG or
  PNG up to 10 MB, type checked from the contents). One picture per person; a file is never shared.
- **Set or replace:** `POST /api/auth/profile/picture/` (multipart, one `file`), permission
  `accounts.update_profile`, own picture only. A replaced picture is hidden, not deleted (soft delete),
  the same as other files.
- **Remove:** `DELETE /api/auth/profile/picture/`. Removing when there is none is not an error.
- **Seeing it:** the user resources (`/api/auth/me/`, the admin user list and detail, the brief used for
  people) gain `picture_id`, the file id or null; it changes when the picture changes, so it can serve
  as a cache key. The image itself is `GET /api/auth/users/<id>/picture/?v=<picture_id>`.
- **Who may open someone's picture** (assumption, change if wrong): the person themselves, any admin,
  and people they share a tenancy with: housemates, the landlord of the property, and the landlord's
  tenants. Anyone else, a missing picture or a deleted account gets a 404, so nobody can tell whether
  a picture exists.
- **History:** setting or removing a picture is recorded in the account history
  (`UPDATED_OWN_PICTURE`, `REMOVED_OWN_PICTURE`).

## Source locations

- Back end: `back-end/accounts/` (`models/users.py` field `avatar_file`, migration `accounts/0015`,
  `services/set_profile_picture.py`, `remove_profile_picture.py`, `open_profile_picture.py`,
  `services/shared/relations.py` and `pictures.py`, `views.py`, `resources/user.py`,
  `tests/test_profile_picture.py`).
- Admin app: the wireframe pages (`admin/app/tools/wireframe/`) have a "Profile picture" form and an
  "avatar" download option.

## Not done

No screens. Also: an admin setting someone's picture, resizing or cropping, and putting the
picture next to every place a person's name already appears (report authors, issue reporters, document
uploaders); those resources get a picture field in a later pass. No screens.
