"""pyjazzmusicarchives — typed Python client for Jazz Music Archives.

Jazz Music Archives (jazzmusicarchives.com) is a community catalogue of jazz
artists: an A–Z index of artists, each with a biography and a member-rated
discography tagged by sub-genre.

Quick start::

    import pyjazzmusicarchives as jma

    # Browse the A–Z artist index
    for a in jma.get_artists_by_letter("A")[:5]:
        print(a.slug, a.name, a.genre, a.country)

    # Search by name
    miles = jma.search_artists("miles davis")[0]

    # Full artist page: styles, bio, rated discography
    detail = jma.fetch_artist(miles.slug)
    print(detail.genres[:3])
    for album in detail.albums[:5]:
        print(album.year, album.subgenre, album.avg_rating, album.title)

    # Stream the whole index lazily
    import itertools
    for a in itertools.islice(jma.iter_artists(), 20):
        print(a.name)

    # Serialise + canonical ids
    import json
    print(json.dumps(detail.to_dict(), indent=2)[:300])
    print(detail.to_external_ids_dict())   # consumed by metadatarr for resolution
"""
from pyjazzmusicarchives.types import Artist, Album, ArtistDetail
from pyjazzmusicarchives.artists import (
    ArtistNotFound,
    fetch_artist,
    get_all_artists,
    get_artists_by_letter,
    iter_artists,
    search_artists,
)
from pyjazzmusicarchives.version import __version__

__all__ = [
    "Artist",
    "Album",
    "ArtistDetail",
    "ArtistNotFound",
    "fetch_artist",
    "get_all_artists",
    "get_artists_by_letter",
    "iter_artists",
    "search_artists",
    "__version__",
]
