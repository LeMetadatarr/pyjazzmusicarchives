# Advanced usage

## Cloudflare and transport

jazzmusicarchives.com sits behind Cloudflare. The shared session (created lazily per `Transport` instance) defaults to **`curl_cffi` Chrome TLS impersonation** when the `stealth` extra is installed:

```bash
pip install pyjazzmusicarchives[stealth]
```

### Transport modes

`PYJAZZMUSICARCHIVES_TRANSPORT` selects how pages are fetched:

| Value | Behavior |
|---|---|
| *(unset)* / `curl_cffi` | Live fetch with Chrome TLS impersonation (default). |
| `requests` | Live fetch with plain `requests`, no impersonation. |
| `wayback` | **Does not touch the live site.** Fetches the latest snapshot from the Internet Archive (Wayback Machine). |
| `flaresolverr` | Fetches through a FlareSolverr proxy that solves the Cloudflare challenge in a real browser and returns **live** HTML. |

```bash
export PYJAZZMUSICARCHIVES_TRANSPORT=requests   # or: curl_cffi (default), wayback, flaresolverr
```

### Configure in code (no environment variables)

Every setting is also a constructor keyword argument on the `JazzMusicArchives` client, and on `Transport`. Explicit keyword arguments always win over the environment.

```python
import pyjazzmusicarchives as jma

# FlareSolverr (live) -- setting the URL selects the flaresolverr transport
client = jma.JazzMusicArchives(flaresolverr_url="http://192.168.1.116:8191")
miles = client.fetch_artist("miles-davis")

# Force the Internet Archive
archived = jma.JazzMusicArchives(wayback=True)        # == transport="wayback"

# Try live first, fall back to the archive
resilient = jma.JazzMusicArchives(flaresolverr_url="http://192.168.1.116:8191",
                                  wayback_fallback=True)

# Or build a Transport yourself and pass it to the functions
from pyjazzmusicarchives import Transport
t = Transport(mode="flaresolverr", flaresolverr_url="http://192.168.1.116:8191",
              flaresolverr_timeout_ms=90000)
artists = jma.get_artists_by_letter("M", transport=t)
```

The module-level functions (`jma.fetch_artist(...)` and others) keep using the environment-driven default transport.

### FlareSolverr -- solve the challenge and get live data

[FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) runs a headless browser that clears the Cloudflare JS challenge. Unlike the Wayback fallback, it returns **current** pages, so it is the best option if you have an instance. It is a one-container service, commonly run on port `8191`. Point the client at it:

```bash
export PYJAZZMUSICARCHIVES_FLARESOLVERR_URL=http://192.168.1.116:8191
# setting the URL alone selects flaresolverr transport automatically.
# PYJAZZMUSICARCHIVES_FLARESOLVERR_TIMEOUT (ms, default 60000) tunes the solve budget.
```

```python
import pyjazzmusicarchives as jma
miles = jma.fetch_artist("miles-davis")   # fetched live, challenge solved by FlareSolverr
```

`pyjazzmusicarchives._transport.flaresolverr_html(url)` is exposed for direct use. Combine it with `PYJAZZMUSICARCHIVES_WAYBACK_FALLBACK=1` to fall back to the archive if FlareSolverr is down.

### Wayback Machine -- surviving the JS challenge

If you receive a Cloudflare **JS challenge**, your IP is flagged and TLS impersonation alone will not help. The client can read the site from the **Internet Archive** instead. archive.org is not Cloudflare-gated:

```bash
# Archive-only: every request goes to the Wayback Machine
export PYJAZZMUSICARCHIVES_TRANSPORT=wayback

# Or: try live first, fall back to the archive on failure (challenge / non-2xx)
export PYJAZZMUSICARCHIVES_WAYBACK_FALLBACK=1
```

This mode fetches the most recent capture's raw bytes (the Wayback `id_` form, with no toolbar and no link rewriting), so the parsers see the page exactly as jazzmusicarchives served it. The trade-off is **staleness**. A snapshot may be weeks or months old, and very obscure pages may not be archived at all. Those raise `RuntimeError` in `wayback` mode, or fall through to the live error under fallback. `pyjazzmusicarchives._transport.wayback_html(url)` is exposed if you want to drive it directly.

Other options:

- Run from a residential or unblocked network.
- Front the client with a challenge-solving proxy.
- Fetch the HTML however you like and call the parsers in `pyjazzmusicarchives.parse` directly. They take a raw HTML string and need no network:

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

When you walk the whole index or fetch many artist pages, throttle your requests. An artist page is one request, and a prolific artist's discography is large (Miles Davis: 340+ entries):

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

- The album id and the precise rating come from the per-album rating star-box script (`readOnlyRating_<id>`), present on **every** release. This differs from the `avgRatings_<id>` span, which appears only once an album has been rated.
- An unrated release (`"0.00 | 0 ratings"`, or an empty star value) surfaces as `avg_rating = None`, `num_ratings = 0`. The album id is still captured.
- The per-album sub-genre is the id-less styled span in each discography cell. The year is the trailing four-digit token.
- `country` is available on both the listing and the artist page. On the artist page it is appended to the last style in the styles line as `"... • Country"`, with no separate element, so it is split off before the styles are parsed. `ArtistDetail.genres` lists the styles the artist worked across.
- `display_name` flips the leading surname comma (`"DAVIS, MILES"` becomes `"MILES DAVIS"`).

---
[← API reference](api.md) · [Home](../README.md) · [Canonical ids →](canonical_ids.md)
