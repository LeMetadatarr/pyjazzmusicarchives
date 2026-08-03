"""Pure HTML → model parsers for jazzmusicarchives.com.

No network access — unit-testable against saved fixtures.

Verified against live markup:

- **Listing** (``ListArtistsAlpha.aspx``): ``<li>`` rows each with an
  ``<a href="/artist/SLUG">`` and a ``<span>`` of ``"Genre • Country"`` (the
  ``• Country`` suffix is sometimes absent, leaving a bare genre).
- **Artist page** (``/artist/SLUG``): name from the ``<title>``, the styles
  line in a bare ``<div>`` inside ``div.col1`` — a ``"/"``-joined genre list
  with the country appended to the last entry as ``"... • Country"``, no
  separate element — the biography in ``div[id$=BioUpdatePanel]``, and a
  ``div.discographyContainer`` per album (numeric id in the
  ``avgRatings_<id>`` span, a title anchor, a per-album subgenre span, a
  trailing year, and an ``img.album-cover``).
"""
from __future__ import annotations

import re
from typing import List, Optional

from bs4 import BeautifulSoup

from pyjazzmusicarchives.types import Artist, Album, ArtistDetail

_STARBOX_RE = re.compile(
    r"generateReadOnlyStarbox\('readOnlyRating_(\d+)',\s*([\d.]*)\)"
)
_RATINGS_RE = re.compile(r"([\d.]+)\s*\|\s*(\d+)\s*ratings")
_YEAR_RE = re.compile(r"\b((?:19|20)\d{2})\b")


def _int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    m = re.search(r"\d[\d,]*", text)
    return int(m.group(0).replace(",", "")) if m else None


def _float(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"[\d.]+", text)
    return float(m.group(0)) if m else None


def parse_listing(html: str) -> List[Artist]:
    """Parse a ``ListArtistsAlpha.aspx`` page into :class:`Artist` objects."""
    soup = BeautifulSoup(html, "html.parser")
    artists: List[Artist] = []
    seen = set()
    for li in soup.find_all("li"):
        a = li.find("a")
        if not a:
            continue
        href = a.get("href", "")
        if not href.startswith("/artist/") or "#" in href:
            continue
        span = li.find("span")
        genre = country = None
        if span:
            text = span.get_text(strip=True)
            if "•" in text:
                genre, country = (p.strip() for p in text.split("•", 1))
            elif text:
                # some rows carry only a genre span, with no country suffix
                genre = text
        slug = href.rsplit("/", 1)[-1]
        if slug in seen:
            continue
        seen.add(slug)
        artists.append(Artist(
            slug=slug, name=a.get_text(strip=True),
            genre=genre or None, country=country or None,
        ))
    return artists


def _parse_album_container(c, artist_slug: str, artist_name: str) -> Optional[Album]:
    # The album id + precise rating live in the rating star-box script, present
    # on every album (rated or not) — unlike the ``avgRatings_`` span, which is
    # only emitted for already-rated releases.
    star = _STARBOX_RE.search(c.decode())
    if not star:
        return None
    album_id = int(star.group(1))

    text = c.get_text(" ", strip=True)
    ratings = _RATINGS_RE.search(text)
    num_ratings = int(ratings.group(2)) if ratings else None
    # unrated releases report "0.00 | 0 ratings" (or an empty star value) —
    # surface that as no rating rather than a misleading 0.0.
    avg_rating = round(float(star.group(2)), 2) if star.group(2) else None
    if not num_ratings:
        avg_rating = None

    link = next((a for a in c.find_all("a", href=re.compile(r"/album/"))
                 if a.get_text(strip=True)), None)
    title = link.get_text(strip=True) if link else ""
    slug = link["href"].split("/album/", 1)[-1] if link else None
    cover = c.find("img", class_="album-cover")

    # per-album subgenre: the first id-less, non-empty <span>
    subgenre = None
    for sp in c.find_all("span"):
        if not sp.get("id") and sp.get_text(strip=True):
            subgenre = sp.get_text(strip=True)
            break
    years = _YEAR_RE.findall(text)
    return Album(
        album_id=album_id, title=title, slug=slug, subgenre=subgenre,
        year=int(years[-1]) if years else None,
        avg_rating=avg_rating, num_ratings=num_ratings,
        cover=cover.get("src") if cover else None,
        artist_slug=artist_slug, artist_name=artist_name,
    )


def parse_artist(html: str, slug: str) -> ArtistDetail:
    """Parse an ``/artist/SLUG`` page into an :class:`ArtistDetail`."""
    soup = BeautifulSoup(html, "html.parser")

    name = ""
    if soup.title:
        name = re.split(r"\s+discography", soup.title.get_text(strip=True))[0].strip()

    genres: List[str] = []
    country = None
    col1 = soup.find("div", class_="col1")
    if col1:
        for div in col1.find_all("div"):
            if div.find(["div", "span", "a"]):
                continue  # want the leaf div holding only the styles text
            txt = div.get_text(" ", strip=True)
            if "/" in txt and name.lower() not in txt.lower():
                # the site appends "• Country" to the last style with no
                # separator of its own — split it off before the "/" split,
                # else it lands merged into the final genre (e.g. "Big Band
                # • United States" instead of "Big Band" + country).
                if "•" in txt:
                    txt, country_part = txt.rsplit("•", 1)
                    country = country_part.strip() or None
                genres = [g.strip() for g in txt.split("/") if g.strip()]
                break

    bio = None
    bio_div = soup.find(id=re.compile(r"BioUpdatePanel"))
    if bio_div:
        bio = bio_div.get_text(" ", strip=True) or None

    albums: List[Album] = []
    for c in soup.find_all("div", class_="discographyContainer"):
        album = _parse_album_container(c, slug, name)
        if album:
            albums.append(album)

    return ArtistDetail(slug=slug, name=name, genres=genres, country=country, bio=bio, albums=albums)
