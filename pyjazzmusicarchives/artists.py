"""Artist lookup functions backed by jazzmusicarchives.com.

The site is an A–Z artist index plus per-artist pages carrying the biography
and rated discography. No JSON API — this scrapes the HTML (see
:mod:`pyjazzmusicarchives.parse`).
"""
from __future__ import annotations

import string
from typing import Dict, Iterator, List, Optional

from pyjazzmusicarchives._transport import get_html
from pyjazzmusicarchives.parse import parse_artist, parse_listing
from pyjazzmusicarchives.types import Artist, ArtistDetail


class ArtistNotFound(Exception):
    """Raised by :func:`fetch_artist` when the slug has no artist page."""


def get_artists_by_letter(letter: str) -> List[Artist]:
    """Return every artist whose name starts with *letter* (A–Z).

    Example::

        import pyjazzmusicarchives as jma
        print(len(jma.get_artists_by_letter("M")), "artists under M")
    """
    letter = letter.strip().upper()[:1]
    if letter not in string.ascii_uppercase:
        raise ValueError(f"letter must be A-Z, got {letter!r}")
    return parse_listing(get_html("/ListArtistsAlpha.aspx", letter=letter))


def iter_artists(letters: Optional[str] = None) -> Iterator[Artist]:
    """Lazily iterate the full A–Z artist index.

    Example::

        import itertools, pyjazzmusicarchives as jma
        first = list(itertools.islice(jma.iter_artists(), 50))
    """
    for letter in (letters or string.ascii_uppercase):
        yield from get_artists_by_letter(letter)


def get_all_artists(letters: Optional[str] = None) -> List[Artist]:
    """Eagerly collect the full index. Prefer :func:`iter_artists`."""
    return list(iter_artists(letters))


def fetch_artist(slug: str) -> ArtistDetail:
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
    detail = parse_artist(get_html(f"/artist/{slug}"), slug)
    if not detail.name:
        raise ArtistNotFound(f"no artist found for slug={slug!r}")
    return detail


def search_artists(query: str, limit: Optional[int] = None) -> List[Artist]:
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
        for a in get_artists_by_letter(letter):
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
