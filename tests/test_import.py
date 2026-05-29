"""Public surface is importable and stable."""
import pyjazzmusicarchives as jma


def test_version():
    assert isinstance(jma.__version__, str)


def test_exports():
    for name in [
        "Artist", "Album", "ArtistDetail", "ArtistNotFound",
        "fetch_artist", "get_all_artists", "get_artists_by_letter",
        "iter_artists", "search_artists",
    ]:
        assert hasattr(jma, name), name
