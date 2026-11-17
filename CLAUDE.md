# RentTrace

Monorepo: `back-end/` (Django REST), `admin/` (Next.js), `mobile/`.

## Feature tracking

Every feature has a document in `docs/features/<feature>.md`, the same way
Mneme and Lazify keep theirs.

1. Create or update the feature document **before** substantial implementation.
   Record the intended behaviour, source locations, and acceptance criteria.
2. When the code lands, update the document with what actually shipped, and
   mark anything not yet verified.
3. New code with no feature document is unfinished. Changes to an existing
   feature update that feature's document in the same change.

Document shape:

- `# <Feature name>`
- `## Status — <date>`: shipped, in progress, or planned, and what is unverified
- `## Goal`: who it is for and what they can do
- `## How it works`: behaviour as the user or API client sees it, including rules and errors
- `## Source locations`: back-end and admin paths, one line each
- `## Not done`: known gaps

`docs/features/README.md` lists every feature with its status.
