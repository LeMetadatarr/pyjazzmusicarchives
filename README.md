# pyjazzmusicarchives

Typed Python client for [Jazz Music Archives](https://www.jazzmusicarchives.com)
— a community catalogue of jazz artists and their member-rated, sub-genre-tagged
discographies.

It scrapes the site's HTML behind clean dataclasses: browse the A–Z artist
index, search by name, and fetch an artist's full page (styles, biography, and a
rated discography). Every model exposes canonical ids for de-duplication and an
optional [metadatarr](../metadatarr) provider for cross-referencing.

## Install

```bash
pip install pyjazzmusicarchives
pip install pyjazzmusicarchives[stealth]   # adds curl-cffi — recommended (see below)
pip install pyjazzmusicarchives[dev]       # adds pytest
```

> **Cloudflare:** jazzmusicarchives.com is fronted by Cloudflare. The client
> defaults to `curl_cffi` Chrome TLS impersonation (the `stealth` extra) which
> clears the bot check from most networks. From flagged IPs you may still hit a
> JS challenge — run from a residential/unblocked network, front it with a
> challenge-solving proxy, or read from the **Internet Archive** with
> `PYJAZZMUSICARCHIVES_TRANSPORT=wayback` (or `PYJAZZMUSICARCHIVES_WAYBACK_FALLBACK=1`).
> The parsing layer is independent of how the HTML was fetched — see
> [docs/advanced.md](docs/advanced.md).

## 30-second tour

```python
import pyjazzmusicarchives as jma

# Browse the A–Z artist index
for a in jma.get_artists_by_letter("A")[:5]:
    print(a.slug, a.display_name, a.genre, a.country)

# Search by name
miles = jma.search_artists("miles davis")[0]

# Full artist page: styles, bio, rated discography (per-album sub-genre)
detail = jma.fetch_artist(miles.slug)
print(detail.genres[:3])
for album in detail.albums[:5]:
    print(album.year, album.subgenre, album.avg_rating, album.title)

# Canonical ids for dedup / cross-referencing
print(detail.to_external_ids_dict())
# {'jazzmusicarchives_artist': 'miles-davis', 'jazzmusicarchives_url': '...'}
```

## What you can fetch

| Function | Returns | Source |
|---|---|---|
| `get_artists_by_letter("A")` | `List[Artist]` | `ListArtistsAlpha.aspx?letter=` |
| `iter_artists()` | `Iterator[Artist]` | the whole A–Z index (lazy) |
| `get_all_artists()` | `List[Artist]` | eager full index |
| `search_artists("miles davis")` | `List[Artist]` | client-side over the index |
| `fetch_artist(slug)` | `ArtistDetail` | `/artist/<slug>` |

Artists are identified by a URL **slug** (`"miles-davis"`); albums carry a numeric
id. An `ArtistDetail` carries `albums: List[Album]`, each with a per-album
sub-genre, year, member average rating and rating count.

## Documentation

Start with **[docs/quickstart.md](docs/quickstart.md)**, then:

- [docs/api.md](docs/api.md) — every function and model field
- [docs/advanced.md](docs/advanced.md) — Cloudflare/transport, pagination, errors
- [docs/canonical_ids.md](docs/canonical_ids.md) — canonical ids (how metadatarr consumes this)
- [docs/dataset.md](docs/dataset.md) — building a Hugging Face dataset

Runnable, numbered scripts live in [examples/](examples/).

## Canonical ids & metadatarr

This package is a **pure scraper**. It exposes jazzmusicarchives' stable ids via
`site_id` and `to_external_ids_dict()`:

```python
m = jma.search_artists("miles davis")[0]
m.to_external_ids_dict()
# {'jazzmusicarchives_artist': 'miles-davis', 'jazzmusicarchives_url': '...'}
```

The metadatarr resolver **consumes** these — the `MetadataProvider` lives in the
[metadatarr](../metadatarr) repo (`metadatarr/resolve/providers/jazzmusicarchives.py`),
not here, so integration code isn't scattered across client repos. Install both
packages and metadatarr auto-discovers the provider. See
[docs/canonical_ids.md](docs/canonical_ids.md).
