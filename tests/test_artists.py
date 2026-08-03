"""Offline tests for the artists module, backed by a fake transport that
replays the real-markup fixtures (no network)."""
import os

import pytest

import pyjazzmusicarchives as jma
from pyjazzmusicarchives.artists import ArtistNotFound, fetch_artist, get_artists_by_letter

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return fh.read()


class FakeTransport:
    """Replays fixtures instead of hitting the network."""

    def __init__(self, listing="listing.html", artist="artist.html", empty_artist=False):
        self.listing = listing
        self.artist = artist
        self.empty_artist = empty_artist
        self.calls = []

    def get_html(self, path, **params):
        self.calls.append((path, params))
        if path == "/ListArtistsAlpha.aspx":
            return _read(self.listing)
        if path.startswith("/artist/"):
            if self.empty_artist:
                return "<html><body>no such artist</body></html>"
            return _read(self.artist)
        raise AssertionError(f"unexpected path {path!r}")


def test_get_artists_by_letter_happy_path():
    t = FakeTransport()
    artists = get_artists_by_letter("a", transport=t)
    assert len(artists) == 4
    assert t.calls == [("/ListArtistsAlpha.aspx", {"letter": "A"})]


def test_get_artists_by_letter_rejects_non_alpha():
    with pytest.raises(ValueError):
        get_artists_by_letter("1", transport=FakeTransport())


def test_iter_artists_spans_requested_letters():
    t = FakeTransport()
    artists = list(jma.iter_artists("AB", transport=t))
    assert len(artists) == 8  # same 4-row fixture served for both letters
    assert [c[1]["letter"] for c in t.calls] == ["A", "B"]


def test_get_all_artists_is_eager_list():
    artists = jma.get_all_artists("A", transport=FakeTransport())
    assert isinstance(artists, list) and len(artists) == 4


def test_fetch_artist_happy_path():
    d = fetch_artist("miles-davis", transport=FakeTransport())
    assert d.name == "MILES DAVIS"
    assert d.albums


def test_fetch_artist_accepts_full_url():
    t = FakeTransport()
    d = fetch_artist("https://www.jazzmusicarchives.com/artist/miles-davis/", transport=t)
    assert d.slug == "miles-davis"
    assert t.calls == [("/artist/miles-davis", {})]


def test_fetch_artist_raises_when_page_has_no_name():
    with pytest.raises(ArtistNotFound):
        fetch_artist("nobody-here", transport=FakeTransport(empty_artist=True))


def test_search_artists_ranks_exact_match_first():
    results = jma.search_artists("a/b trio", transport=FakeTransport())
    assert results[0].slug == "ab-trio"


def test_search_artists_matches_display_name_tokens():
    # "greta aagre" only appears in the flipped display name, not the raw
    # surname-first listing text.
    results = jma.search_artists("greta aagre", transport=FakeTransport())
    assert results and results[0].slug == "greta-aagre-and-erik-honore"


def test_search_artists_empty_query_returns_nothing():
    assert jma.search_artists("   ", transport=FakeTransport()) == []


def test_search_artists_respects_limit():
    results = jma.search_artists("trio", limit=1, transport=FakeTransport())
    assert len(results) == 1


def test_jazzmusicarchives_client_reuses_configured_transport():
    t = FakeTransport()
    client = jma.JazzMusicArchives(transport=t)
    assert client.get_artists_by_letter("A") == get_artists_by_letter("A", transport=t)
    assert client.fetch_artist("miles-davis").name == "MILES DAVIS"


def test_jazzmusicarchives_accepts_duck_typed_transport():
    """Regression: the client used to accept only ``isinstance(transport,
    Transport)``, so any object that merely quacks like a transport (e.g. a
    test double implementing ``get_html``) was mistaken for a mode string
    and crashed on ``mode.lower()``."""
    t = FakeTransport()
    client = jma.JazzMusicArchives(transport=t)
    assert client.transport is t
