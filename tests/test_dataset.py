"""Dataset row builders produce flat, join-able rows."""
import os

from pyjazzmusicarchives import dataset
from pyjazzmusicarchives.parse import parse_artist, parse_listing

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return fh.read()


def test_artist_rows():
    rows = list(dataset.artist_rows(parse_listing(_read("listing.html"))))
    assert len(rows) == 4
    assert set(rows[0]) == {"artist_slug", "name", "display_name", "genre", "country", "url"}


def test_album_rows_carry_artist():
    detail = parse_artist(_read("artist.html"), "miles-davis")
    rows = list(dataset.album_rows(detail))
    assert len(rows) == 3
    for r in rows:
        assert r["artist_slug"] == "miles-davis"
        assert r["artist_name"] == "MILES DAVIS"
        assert "subgenre" in r and "avg_rating" in r


def test_detail_row_has_genres_and_bio():
    detail = parse_artist(_read("artist.html"), "miles-davis")
    row = dataset.artist_detail_row(detail)
    assert row["n_albums"] == 3
    assert isinstance(row["genres"], list) and row["genres"]
    assert "Miles Dewey Davis" in row["bio"]


def test_write_jsonl(tmp_path):
    rows = dataset.artist_rows(parse_listing(_read("listing.html")))
    path = tmp_path / "out.jsonl"
    n = dataset.write_jsonl(str(path), rows)
    assert n == 4
    assert path.read_text().count("\n") == 4
