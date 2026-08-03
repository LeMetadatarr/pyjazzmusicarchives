"""Offline parser tests against real-markup fixtures (no network)."""
import os

from pyjazzmusicarchives.parse import parse_artist, parse_listing
from pyjazzmusicarchives.types import Album, Artist, ArtistDetail

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return fh.read()


def test_parse_listing():
    artists = parse_listing(_read("listing.html"))
    assert len(artists) == 4
    assert all(isinstance(a, Artist) for a in artists)
    first = artists[0]
    assert first.slug == "add-trio"
    assert first.name == "A.D.D. TRIO"
    # surname-first names flip to natural order
    aagre = next(a for a in artists if a.name.startswith("AAGRE,"))
    assert aagre.display_name == "GRETA & ERIK HONORÉ AAGRE"
    assert first.genre == "Eclectic Fusion"
    assert first.country == "United States"
    assert first.url == "https://www.jazzmusicarchives.com/artist/add-trio"
    assert first.to_external_ids_dict()["jazzmusicarchives_artist"] == "add-trio"


def test_parse_artist():
    d = parse_artist(_read("artist.html"), "miles-davis")
    assert isinstance(d, ArtistDetail)
    assert d.name == "MILES DAVIS"
    assert "Fusion" in d.genres and "Hard Bop" in d.genres
    assert d.genre == d.genres[0]
    assert d.bio and "Miles Dewey Davis" in d.bio
    assert d.url == "https://www.jazzmusicarchives.com/artist/miles-davis"


def test_parse_artist_albums():
    d = parse_artist(_read("artist.html"), "miles-davis")
    assert len(d.albums) == 3
    assert all(isinstance(a, Album) for a in d.albums)
    first = d.albums[0]
    assert first.album_id == 136410
    assert first.title.startswith("The New Sounds of Miles Davis")
    assert first.subgenre == "Bop"
    assert first.year == 1951
    assert first.avg_rating == 2.38
    assert first.num_ratings == 4
    assert first.cover and first.cover.startswith("http")
    assert first.artist_slug == "miles-davis"
    assert first.url.endswith(first.slug)
    assert first.to_external_ids_dict()["jazzmusicarchives_album"] == "136410"


def test_unrated_album_has_no_rating():
    d = parse_artist(_read("artist.html"), "miles-davis")
    unrated = [a for a in d.albums if not a.num_ratings]
    assert unrated, "fixture should include one unrated album"
    assert unrated[0].avg_rating is None
    assert unrated[0].album_id > 0       # id still captured from the star-box


def test_empty_listing():
    assert parse_listing("<html><body>nothing</body></html>") == []


# --- Regression fixtures recorded from the live site via the Wayback Machine
# (https://www.jazzmusicarchives.com/artist/miles-davis and
# .../ListArtistsAlpha.aspx?letter=A, captured 2026-08-03) -------------------

def test_parse_artist_splits_trailing_country_from_last_genre():
    """The styles line has no separate element for country: it is appended
    to the last style as ``"... • Country"`` in the same text node (e.g.
    ``"... / Big Band • United States"``). Regression for a bug where the
    unsplit country leaked into ``genres`` as ``"Big Band • United States"``
    and ``ArtistDetail.country`` stayed ``None``."""
    d = parse_artist(_read("artist_live.html"), "miles-davis")
    assert d.country == "United States"
    assert "Big Band" in d.genres
    assert not any("•" in g for g in d.genres)


def test_parse_artist_live_albums_have_titles_and_covers():
    d = parse_artist(_read("artist_live.html"), "miles-davis")
    assert len(d.albums) > 300
    assert all(a.title for a in d.albums)
    assert all(a.cover for a in d.albums)


def test_parse_listing_keeps_genre_without_country():
    """Some rows carry a genre span with no ``"• Country"`` suffix at all.
    Regression for a bug where the whole span (including a bare genre) was
    dropped to ``None`` unless a ``"•"`` was present."""
    artists = parse_listing(_read("listing_live.html"))
    no_country = next(a for a in artists if a.slug == "the-missing-cats")
    assert no_country.genre == "Post-Fusion Contemporary"
    assert no_country.country is None


def test_parse_listing_live_full_page():
    artists = parse_listing(_read("listing_live.html"))
    assert len(artists) > 600
    with_country = [a for a in artists if a.country]
    assert len(with_country) > 500
