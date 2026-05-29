# AGENTS.md — pyjazzmusicarchives

Typed Python client for Jazz Music Archives (jazzmusicarchives.com): browse the
A–Z artist index, search by name, fetch full artist pages (styles, biography,
rated discography), and a dataset row builder. Pure scraper — the metadatarr
`MetadataProvider` that consumes it lives in the **metadatarr** repo
(`metadatarr/resolve/providers/jazzmusicarchives.py`), not here.

## Setup

```bash
pip install -e .
pip install -e .[stealth]   # adds curl-cffi for Chrome TLS impersonation (recommended)
pip install -e .[dev]       # adds pytest
```

## Test

```bash
pytest
```

Tests (`tests/`) parse real-markup fixtures in `tests/fixtures/` — no network.
In the shared OVOS dev venv `pytest-recording` and `pytest-vcr` clash (an
environment issue, not this package); run `pytest -p no:recording` if needed.

## Lint/Typecheck

None configured. Source is fully type-annotated with
`from __future__ import annotations`.

## Layout

- `pyjazzmusicarchives/__init__.py` — public surface: models (`Artist`,
  `ArtistDetail`, `Album`), functions (`get_artists_by_letter`, `iter_artists`,
  `get_all_artists`, `fetch_artist`, `search_artists`) and `ArtistNotFound`.
- `pyjazzmusicarchives/types.py` — the dataclasses. `_display_name` flips the
  surname comma (`"DAVIS, MILES"` → `"MILES DAVIS"`). Artists are keyed by slug.
- `pyjazzmusicarchives/parse.py` — **pure** HTML→model parsers (no network).
  `parse_listing` reads `<li>` rows (`a[href^=/artist/]` + `"Genre • Country"`
  span); `parse_artist` reads the name from `<title>`, the styles from the leaf
  `<div>` in `div.col1`, the bio from `div[id$=BioUpdatePanel]`, and a
  `div.discographyContainer` per album.
- `pyjazzmusicarchives/artists.py` — fetching + client-side `search_artists`.
- `pyjazzmusicarchives/_transport.py` — `get_html()`; defaults to `curl_cffi`
  Chrome impersonation, `PYJAZZMUSICARCHIVES_TRANSPORT=requests` forces requests.
- `pyjazzmusicarchives/dataset.py` — flat HF row builders.
- `docs/`, `examples/`, `tests/fixtures/`.

## Site structure (jazzmusicarchives.com)

HTML scrape (no JSON API), behind **Cloudflare**:

- `/ListArtistsAlpha.aspx?letter=X` — A–Z index. `<li>` rows, each an
  `<a href="/artist/SLUG">` plus a `<span>` of `"Genre • Country"`.
- `/artist/SLUG` — artist page. Name from `<title>` (`"NAME discography…"`),
  styles in a bare leaf `<div>` inside `div.col1`, bio in
  `div[id$=BioUpdatePanel]`, and a `div.discographyContainer` per album:
  cover `img.album-cover`, title anchor `/album/…`, id-less styled subgenre span,
  trailing year, and a `generateReadOnlyStarbox('readOnlyRating_<id>', <value>)`
  script giving the universal album id + precise rating.

## Conventions (Org hard rules)

- Branches: `dev` (work) / `master` (stable). NEVER `main`.
- Never edit `pyjazzmusicarchives/version.py`; gh-automations bumps semver from commit prefixes.
- New repos private by default.
- Commit identity: JarbasAi <jarbasai@mailfence.com>.
- gh-automations reusable workflows referenced at `@dev`.
- No Neon / `neon-*`. No meta-commentary in docs/commits/code.

## Gotchas

- Cloudflare may serve a JS challenge from flagged IPs even with curl_cffi; the
  parsing layer is decoupled (`parse.py` takes raw HTML).
- Use the `readOnlyRating_<id>` star-box for the album id + rating, **not** the
  `avgRatings_<id>` span — that span is absent on unrated albums (which use
  generic `Span1`/`Span2` ids). Unrated → `avg_rating=None`.
- `country` is reliable on the listing, not the artist page; `ArtistDetail.country`
  is usually `None` (use `genres` there).
- Multi-comma listed names (e.g. `"ELLINGTON, DUKE  ORCHESTRA, THE"`) flip
  imperfectly via the single-comma rule; the slug is still correct.
- `search_artists` only fetches the listings for the **initials in the query**.
