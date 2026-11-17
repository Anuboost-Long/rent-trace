# Public listings

## Status — 13 November 2026

Built. Back-end tests (`listings/tests/test_public_listings_api.py`) pass in the full
back-end run of 12 November 2026 (444 tests). The site screens were opened in Chrome only
as far as the home page; the browse and detail pages have not been walked through.
The 13 November home page rework (below) is type-checked and linted. It was viewed in Chrome as
the landlord account: the hero and newest-rental band at desktop width, and the whole page at
phone width. The new sections (type links, record, closing panel) are not yet seen at desktop
width, and the tenant-only parts are not yet seen.

## Goal

Anyone, signed in or not, can browse listed properties, filter them, and open
one to see its units and photos.

## How it works

API, under `api/public/listings/`:

- `GET /` — a page of listings. Filters: `q` (name, suburb, postcode,
  description), `state`, `suburb`, `type`, `min_rent`, `max_rent` (both per
  week), `sort` (`newest`, `rent_low`, `rent_high`; default `newest`), `page`,
  `page_size` (up to 48, default 20).
- `GET places/` — the places to offer in the state and suburb filters.
- `GET <listing_id>/` — one listing in detail: its description, its available
  units and the photos.
- `GET <listing_id>/photos/<file_id>/` — a listing photo.

**Available units.** A listing shows only units that are public and `VACANT` or
`PARTIALLY_OCCUPIED`. Occupied and unavailable units are hidden everywhere: the
unit list, `unit_count`, the "from" rent, the rent filter, and which photos are
shown. A listed property with no available public unit drops out of browsing.

**Who listed it.** The detail has `listed_by`: the primary owner's first name and last
initial ("Lou R."), shown in the side panel as "Listed by Lou R.". No email, phone or
full surname; contact details are shared only after a landlord accepts a
[contact request](contact-requests.md). Browse results don't name the landlord.

**Photos per unit.** Each unit in the detail has its own `photos` (id, caption,
`is_cover`). The listing's top-level `photos` still holds the property's photos
and the shown units' photos together, for the gallery.

Site, in the admin app's `(site)` route group:

- `/` — home with hero photos and the search form.
  - Short headline, then the search as one wide row (state, suburb, type, search), and
    quick links by property type under it that open the results filtered to that type.
  - **Newest rental**: one large cover photo with its title, place, type and "From" rent over
    it, linking to the listing. The newest listing that has a cover photo.
  - **New on RentTrace**: the other latest listings as cards (up to four).
  - **Browse by suburb**: up to eight places with listings, most first, each linking to the
    results filtered to that suburb.
  - **A record both sides can see**: what RentTrace keeps for a tenancy (rent and bond
    changes the tenants approve, condition notes the landlord chooses to show, maintenance
    closed only when both sides agree, housemates the landlord approves). Plain text, no
    numbers or statistics.
  - The closing block is a light-on-dark (inverted) panel with the two paths: finding a
    place, and renting out a property (or, for a tenant, "Already renting?").
  - No stock photos: only real listing covers are shown.
  - A signed-in **tenant** sees "Welcome back, <first name>" with a link to their tenancy,
    no "no account needed" line, and an "Already renting?" card with a link to `/tenant`
    in place of the landlord card, which had no action for them.
- `/properties` — results with filters and skeletons while loading.
- `/properties/<id>` — detail with a photo gallery and an "Available units"
  list, each unit with its own rent and photos.
- `/listing-photos/<listingId>/<fileId>` — a route handler that serves photos.
- Header with an account menu, and a footer, on every site page.

## Source locations

- `back-end/listings/`: `urls.py`, `views.py`, `dtos/listing_query.py`,
  `resources/`, `services/` (`list_listings`, `get_listing`, `list_places`,
  `open_listing_photo`, `shared/`).
- `back-end/config/urls.py`, `settings.py`: app registered.
- `admin/app/(site)/`: `layout.tsx`, `page.tsx`, `properties/`.
- `admin/app/listing-photos/[listingId]/[fileId]/route.ts`.
- `admin/components/site/`.
- `admin/api/services/listings/serve-action.ts`, `admin/types/listings/models.ts`.
- `admin/constants/web-routes.ts`: `listings`, `listing`.

## Not done

- Walk through the browse and detail screens in a browser.
- The dev overlay shows a "blocking-prerender-current-time" issue (`Date.now()`) on `/`
  and on every page under the audience layouts (`/admin`, for one). `next build`
  succeeds with all 50 pages and no warnings on 12 November 2026, so it is a
  dev-only check from Cache Components (`cacheComponents: true`). No `Date.now()`
  call in our code is on that path; the cause is not found.
- Rent shown on a listing uses the weekly conversion in
  `listings/services/shared/rent.py`; document the rule once confirmed.
