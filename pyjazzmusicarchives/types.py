"""Typed dataclass models for pyjazzmusicarchives.

Shared interface on every model: ``site_id``, ``url``, ``to_dict()``,
``to_external_ids_dict()``.

Note that jazzmusicarchives identifies artists by a URL **slug**
(``"miles-davis"``), not a number — so :attr:`Artist.site_id` is that slug.
Albums do carry a numeric id (used as :attr:`Album.site_id`).
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

BASE = "https://www.jazzmusicarchives.com"


def _display_name(listed: str) -> str:
    """``"DAVIS, MILES"`` → ``"MILES DAVIS"`` (and ``"ORCH, THE"`` →
    ``"THE ORCH"``); names without a comma are returned unchanged."""
    if "," in listed:
        head, tail = listed.split(",", 1)
        return f"{tail.strip()} {head.strip()}".strip()
    return listed


@dataclass
class Artist:
    """A jazz artist as it appears in the A–Z listing.

    Example::

        import pyjazzmusicarchives as jma
        for a in jma.get_artists_by_letter("A")[:3]:
            print(a.slug, a.display_name, a.genre, a.country)
    """

    slug: str
    name: str                         # as listed, surname-first e.g. "DAVIS, MILES"
    genre: Optional[str] = None       # primary style, e.g. "Post Bop"
    country: Optional[str] = None

    @property
    def site_id(self) -> str:
        return self.slug

    @property
    def display_name(self) -> str:
        """Natural ``"First Last"`` form of :attr:`name`."""
        return _display_name(self.name)

    @property
    def url(self) -> str:
        return f"{BASE}/artist/{self.slug}"

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d["display_name"] = self.display_name
        d["url"] = self.url
        return d

    def to_external_ids_dict(self) -> Dict[str, str]:
        return {"jazzmusicarchives_artist": self.slug, "jazzmusicarchives_url": self.url}


@dataclass
class Album:
    """A release from a jazz artist's discography, with member ratings.

    Example::

        detail = jma.fetch_artist("miles-davis")
        a = detail.albums[0]
        print(a.title, a.year, a.subgenre, a.avg_rating)
    """

    album_id: int
    title: str
    slug: Optional[str] = None         # path under /album/, e.g. "miles-davis/kind-of-blue"
    subgenre: Optional[str] = None     # per-album style, e.g. "Bop"
    year: Optional[int] = None
    avg_rating: Optional[float] = None
    num_ratings: Optional[int] = None
    cover: Optional[str] = None
    artist_slug: Optional[str] = None
    artist_name: Optional[str] = None

    @property
    def site_id(self) -> str:
        return str(self.album_id)

    @property
    def url(self) -> str:
        return f"{BASE}/album/{self.slug}" if self.slug else f"{BASE}/album/{self.album_id}"

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d["url"] = self.url
        return d

    def to_external_ids_dict(self) -> Dict[str, str]:
        return {"jazzmusicarchives_album": self.site_id, "jazzmusicarchives_url": self.url}


@dataclass
class ArtistDetail:
    """Full artist page: styles, biography and rated discography.

    Obtain via :func:`pyjazzmusicarchives.fetch_artist`.

    ``country`` is usually only present on the listing, not the artist page,
    so it may be ``None`` here; ``genres`` is the list of styles the artist
    worked across.

    Example::

        detail = jma.fetch_artist("miles-davis")
        print(detail.name, detail.genres[:3])
        print(detail.bio[:120])
        for a in detail.albums[:5]:
            print(a.year, a.avg_rating, a.title)
    """

    slug: str
    name: str
    genres: List[str] = field(default_factory=list)
    country: Optional[str] = None
    bio: Optional[str] = None
    albums: List[Album] = field(default_factory=list)

    @property
    def site_id(self) -> str:
        return self.slug

    @property
    def genre(self) -> Optional[str]:
        """The primary (first) style, for parity with :class:`Artist`."""
        return self.genres[0] if self.genres else None

    @property
    def url(self) -> str:
        return f"{BASE}/artist/{self.slug}"

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d["url"] = self.url
        return d

    def to_external_ids_dict(self) -> Dict[str, str]:
        return {"jazzmusicarchives_artist": self.slug, "jazzmusicarchives_url": self.url}
