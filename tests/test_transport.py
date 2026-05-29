"""Offline tests for the transport's Wayback helpers (no network)."""
from pyjazzmusicarchives import _transport as t


def test_wayback_raw_url_inserts_id_marker():
    snap = "http://web.archive.org/web/20250519231750/https://www.jazzmusicarchives.com/artist/miles-davis"
    raw = t.wayback_raw_url(snap)
    assert raw == (
        "http://web.archive.org/web/20250519231750id_/"
        "https://www.jazzmusicarchives.com/artist/miles-davis"
    )
    assert raw.count("id_/") == 1


def test_url_variants_cover_scheme_forms():
    variants = list(t._url_variants("https://www.jazzmusicarchives.com/artist/miles-davis"))
    assert "https://www.jazzmusicarchives.com/artist/miles-davis" in variants
    assert "http://www.jazzmusicarchives.com/artist/miles-davis" in variants
    assert "www.jazzmusicarchives.com/artist/miles-davis" in variants
    assert len(variants) == len(set(variants))


def test_truthy():
    assert t._truthy("1") and t._truthy("true") and t._truthy("YES")
    assert not t._truthy("") and not t._truthy("0") and not t._truthy(None)


def test_challenge_detection():
    assert t._is_challenge("<html><head><title>Just a moment...</title>")
    assert not t._is_challenge("<html><body><div class='discographyContainer'>")
