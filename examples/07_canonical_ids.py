"""Example 07 — canonical ids for dedup and cross-referencing.

Note: jazzmusicarchives identifies artists by a URL slug (not a number), so the
artist ``site_id`` is that slug. Albums carry a numeric id.

Run::

    python examples/07_canonical_ids.py
"""
import pyjazzmusicarchives as jma


def main() -> None:
    artist = jma.search_artists("miles davis", limit=1)[0]
    print("Artist canonical id:", artist.site_id)
    print("Artist external ids:", artist.to_external_ids_dict())

    detail = jma.fetch_artist(artist.slug)
    if detail.albums:
        a = detail.albums[0]
        print("\nAlbum canonical id: ", a.site_id)
        print("Album external ids: ", a.to_external_ids_dict())


if __name__ == "__main__":
    main()
