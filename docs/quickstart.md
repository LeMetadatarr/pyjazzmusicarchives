# Quickstart — zero to hero

From `pip install` to an artist's full rated discography.

## 1. Install

```bash
pip install pyjazzmusicarchives[stealth]
```

The `stealth` extra pulls in `curl_cffi`, used by default to clear
jazzmusicarchives.com's Cloudflare bot check. See [advanced.md](advanced.md) if
you still hit a challenge.

## 2. The mental model

Jazz Music Archives catalogues **artists** and their **albums**:

```
Artist ──▶ Album, Album, Album …   (each tagged with a sub-genre + member rating)
```

- An **`Artist`** is the lightweight shape from the A–Z index. It is identified
  by a URL **slug** (`"miles-davis"`), and is listed surname-first
  (`"DAVIS, MILES"`) — use `display_name` for the natural form.
- An **`ArtistDetail`** is the full artist page: styles, biography, and the
  rated discography.
- An **`Album`** is reached through an `ArtistDetail` and carries a per-album
  sub-genre, year, member average rating and rating count.

## 3. Browse the index

```python
import pyjazzmusicarchives as jma

artists = jma.get_artists_by_letter("A")
print(len(artists), "artists under A")
for a in artists[:5]:
    print(a.display_name, "—", a.genre, "—", a.country)
```

Or stream the whole index lazily:

```python
import itertools
for a in itertools.islice(jma.iter_artists(), 20):
    print(a.display_name)
```

## 4. Search

No server search exists, so the library searches the by-letter index (matching
on both surname-first and natural order):

```python
jma.search_artists("miles davis")[0].display_name      # 'MILES DAVIS'
jma.search_artists("coltrane", limit=1)
```

## 5. Fetch an artist page

```python
miles = jma.fetch_artist("miles-davis")
print(miles.name)                       # 'MILES DAVIS'
print(" / ".join(miles.genres[:5]))     # the styles they worked across
print(miles.bio[:160])
print(len(miles.albums), "albums")
```

Unknown slugs raise `ArtistNotFound`.

## 6. The rated discography

```python
detail = jma.fetch_artist("miles-davis")
for a in sorted(detail.albums, key=lambda x: x.year or 0)[:15]:
    rating = f"{a.avg_rating:.2f}" if a.avg_rating is not None else "  -  "
    print(a.year, rating, a.subgenre, a.title)

# Best-rated with a meaningful sample size
rated = [a for a in detail.albums if a.avg_rating and (a.num_ratings or 0) >= 10]
best = max(rated, key=lambda x: x.avg_rating)
print("Top:", best.title, best.avg_rating, f"({best.num_ratings} ratings)")
```

Unrated releases report `avg_rating = None` (the album id is still captured).

## 7. Serialise + canonical ids

```python
import json
print(json.dumps(detail.albums[0].to_dict(), indent=2))
print(detail.to_external_ids_dict())
```

## Next steps

- [api.md](api.md) — the complete reference
- [metadatarr.md](metadatarr.md) — canonical ids and the resolver provider
- [dataset.md](dataset.md) — build a Hugging Face dataset
- [advanced.md](advanced.md) — Cloudflare, transport, errors
