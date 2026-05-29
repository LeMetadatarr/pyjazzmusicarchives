# Advanced usage

## Cloudflare and transport

jazzmusicarchives.com is fronted by Cloudflare. The shared session (created
lazily in `pyjazzmusicarchives._transport.default_session`) therefore defaults
to **`curl_cffi` Chrome TLS impersonation** when the `stealth` extra is
installed:

```bash
pip install pyjazzmusicarchives[stealth]
```

### Transport modes

`PYJAZZMUSICARCHIVES_TRANSPORT` selects how pages are fetched:

| Value | Behaviour |
|---|---|
| *(unset)* / `curl_cffi` | Live fetch with Chrome TLS impersonation (default). |
| `requests` | Live fetch with plain `requests`, no impersonation. |
| `wayback` | **Do not touch the live site** — fetch the latest snapshot from the Internet Archive (Wayback Machine). |

```bash
export PYJAZZMUSICARCHIVES_TRANSPORT=requests   # or: curl_cffi (default), wayback
```

### Wayback Machine — surviving the JS challenge

If you receive a Cloudflare **JS challenge**, your IP is flagged and TLS
impersonation alone won't help. The client can read the site out of the
**Internet Archive** instead — archive.org is not Cloudflare-gated:

```bash
# Archive-only: every request goes to the Wayback Machine
export PYJAZZMUSICARCHIVES_TRANSPORT=wayback

# Or: try live first, fall back to the archive on failure (challenge / non-2xx)
export PYJAZZMUSICARCHIVES_WAYBACK_FALLBACK=1
```

It fetches the most recent capture's *raw* bytes (the Wayback `id_` form — no
toolbar, no link rewriting), so the parsers see the page exactly as
jazzmusicarchives served it. The trade-off is **staleness**: a snapshot may be
weeks or months old, and very obscure pages may not be archived at all (those
raise `RuntimeError` in `wayback` mode, or fall through to the live error under
fallback). `pyjazzmusicarchives._transport.wayback_html(url)` is exposed if you
want to drive it directly.

Other escape hatches:

- run from a residential / unblocked network;
- front the client with a challenge-solving proxy;
- fetch the HTML however you like and call the parsers in
  `pyjazzmusicarchives.parse` directly — they take a raw HTML string and need
  no network:

  ```python
  from pyjazzmusicarchives.parse import parse_artist, parse_listing
  artists = parse_listing(open("list-A.html").read())
  detail  = parse_artist(open("miles-davis.html").read(), slug="miles-davis")
  ```

## Pagination and politeness

The index is one page per initial. Prefer the lazy iterator:

```python
import itertools, pyjazzmusicarchives as jma
head = list(itertools.islice(jma.iter_artists(), 200))
```

When walking the whole index or fetching many artist pages, throttle — an
artist page is one request and a prolific artist's discography is large (Miles
Davis: 340+ entries):

```python
import time
for a in jma.iter_artists():
    detail = jma.fetch_artist(a.slug)
    ...
    time.sleep(1)
```

## Error handling

| Situation | What happens |
|---|---|
| Unknown slug | `fetch_artist` raises `ArtistNotFound` |
| Non-letter passed to `get_artists_by_letter` | `ValueError` |
| Network / non-2xx / Cloudflare challenge | underlying HTTP error propagates |

## Parsing notes

- Album id and the precise rating come from the per-album rating star-box
  script (`readOnlyRating_<id>`), which is present on **every** release — unlike
  the `avgRatings_<id>` span, which only appears once an album has been rated.
- Unrated releases (`"0.00 | 0 ratings"`, or an empty star value) surface as
  `avg_rating = None`, `num_ratings = 0` — the album id is still captured.
- The per-album sub-genre is the id-less styled span in each discography cell;
  the year is the trailing four-digit token.
- `country` is reliably available on the **listing**, not the artist page, so
  `ArtistDetail.country` is usually `None`; `ArtistDetail.genres` lists the
  styles the artist worked across.
- `display_name` flips the leading surname comma (`"DAVIS, MILES"` →
  `"MILES DAVIS"`).
