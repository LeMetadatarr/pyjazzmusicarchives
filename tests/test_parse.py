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
