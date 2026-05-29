"""Artist lookup functions backed by jazzmusicarchives.com.

The site is an A–Z artist index plus per-artist pages carrying the biography
and rated discography. No JSON API — this scrapes the HTML (see
:mod:`pyjazzmusicarchives.parse`).
"""
from __future__ import annotations

import string
from typing import Dict, Iterator, List, Optional

from pyjazzmusicarchives._transport import Transport, default_transport
from pyjazzmusicarchives.parse import parse_artist, parse_listing
from pyjazzmusicarchives.types import Artist, ArtistDetail


class ArtistNotFound(Exception):
    """Raised by :func:`fetch_artist` when the slug has no artist page."""


def _t(transport: Optional[Transport]) -> Transport:
    return transport or default_transport()


def get_artists_by_letter(letter: str, *, transport: Optional[Transport] = None) -> List[Artist]:
    """Return every artist whose name starts with *letter* (A–Z).

    Example::

        import pyjazzmusicarchives as jma
        print(len(jma.get_artists_by_letter("M")), "artists under M")
    """
    letter = letter.strip().upper()[:1]
    if letter not in string.ascii_uppercase:
        raise ValueError(f"letter must be A-Z, got {letter!r}")
    return parse_listing(_t(transport).get_html("/ListArtistsAlpha.aspx", letter=letter))


def iter_artists(letters: Optional[str] = None, *,
                 transport: Optional[Transport] = None) -> Iterator[Artist]:
    """Lazily iterate the full A–Z artist index.

    Example::

        import itertools, pyjazzmusicarchives as jma
        first = list(itertools.islice(jma.iter_artists(), 50))
    """
    for letter in (letters or string.ascii_uppercase):
        yield from get_artists_by_letter(letter, transport=transport)


def get_all_artists(letters: Optional[str] = None, *,
                    transport: Optional[Transport] = None) -> List[Artist]:
    """Eagerly collect the full index. Prefer :func:`iter_artists`."""
    return list(iter_artists(letters, transport=transport))


def fetch_artist(slug: str, *, transport: Optional[Transport] = None) -> ArtistDetail:
    """Fetch an artist page (styles, biography, rated discography).

    Args:
        slug: The artist slug (the last path segment of ``/artist/<slug>``),
              or a full artist URL.

    Raises:
        ArtistNotFound: when the page carries no artist name.

    Example::

        import pyjazzmusicarchives as jma
        miles = jma.fetch_artist("miles-davis")
        print(miles.name, miles.genres[:3])
        print(len(miles.albums), "albums")
    """
    slug = slug.rstrip("/").rsplit("/artist/", 1)[-1].rsplit("/", 1)[-1]
    detail = parse_artist(_t(transport).get_html(f"/artist/{slug}"), slug)
    if not detail.name:
        raise ArtistNotFound(f"no artist found for slug={slug!r}")
    return detail


def search_artists(query: str, limit: Optional[int] = None, *,
                   transport: Optional[Transport] = None) -> List[Artist]:
    """Search the artist index for *query* by name (client-side).

    No server search exists, so this fetches the listing for the query's
    initial(s) and keeps artists whose name contains every query token,
    ranking exact / prefix matches first.

    Example::

        import pyjazzmusicarchives as jma
        jma.search_artists("miles davis")[0].name      # 'MILES DAVIS'
        jma.search_artists("coltrane", limit=1)
    """
    tokens = [t for t in query.lower().split() if t]
    if not tokens:
        return []
    initials = {t[0].upper() for t in tokens if t[0].upper() in string.ascii_uppercase}
    seen: Dict[str, Artist] = {}
    for letter in sorted(initials):
        for a in get_artists_by_letter(letter, transport=transport):
            seen.setdefault(a.slug, a)

    phrase = query.lower().strip()

    def matches(a: Artist) -> bool:
        hay = f"{a.name} {a.display_name}".lower()
        return all(t in hay for t in tokens)

    def score(a: Artist) -> tuple:
        name = a.display_name.lower()
        if name == phrase:
            tier = 0
        elif name.startswith(phrase) or phrase in name:
            tier = 1
        else:
            tier = 2
        return (tier, len(a.name))

    results = sorted((a for a in seen.values() if matches(a)), key=score)
    return results[:limit] if limit else results


class JazzMusicArchives:
    """High-level client with a configurable transport.

    Mirrors the module-level functions, but every call uses the transport you
    configure here — no environment variables required.

    Args:
        transport:            ``"requests"`` / ``"curl_cffi"`` / ``"wayback"`` /
                              ``"flaresolverr"``, or a ready :class:`Transport`.
        flaresolverr_url:     FlareSolverr base URL (e.g.
                              ``"http://192.168.1.116:8191"``); setting it
                              selects the ``flaresolverr`` transport.
        flaresolverr_timeout_ms: per-request solve budget.
        wayback:              force the Internet Archive (same as
                              ``transport="wayback"``).
        wayback_fallback:     fall back to the archive on any live failure.

    Example::

        import pyjazzmusicarchives as jma

        # Solve Cloudflare live via a FlareSolverr box:
        client = jma.JazzMusicArchives(flaresolverr_url="http://192.168.1.116:8191")
        miles = client.fetch_artist("miles-davis")

        # Or force the Wayback Machine explicitly:
        archived = jma.JazzMusicArchives(wayback=True)
        artists = archived.get_artists_by_letter("A")
    """

    def __init__(self, transport=None, *, flaresolverr_url: Optional[str] = None,
                 flaresolverr_timeout_ms: Optional[int] = None,
                 wayback: bool = False,
                 wayback_fallback: Optional[bool] = None) -> None:
        if isinstance(transport, Transport):
            self.transport = transport
        else:
            mode = "wayback" if wayback else transport
            self.transport = Transport(
                mode=mode,
                flaresolverr_url=flaresolverr_url,
                flaresolverr_timeout_ms=flaresolverr_timeout_ms,
                wayback_fallback=wayback_fallback,
            )

    def get_artists_by_letter(self, letter: str) -> List[Artist]:
        return get_artists_by_letter(letter, transport=self.transport)

    def iter_artists(self, letters: Optional[str] = None) -> Iterator[Artist]:
        return iter_artists(letters, transport=self.transport)

    def get_all_artists(self, letters: Optional[str] = None) -> List[Artist]:
        return get_all_artists(letters, transport=self.transport)

    def fetch_artist(self, slug: str) -> ArtistDetail:
        return fetch_artist(slug, transport=self.transport)

    def search_artists(self, query: str, limit: Optional[int] = None) -> List[Artist]:
        return search_artists(query, limit, transport=self.transport)
