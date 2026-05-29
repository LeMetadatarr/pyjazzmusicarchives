"""Example 04 — fetch a full artist page.

Run::

    python examples/04_fetch_artist.py
"""
import pyjazzmusicarchives as jma


def main() -> None:
    detail = jma.fetch_artist("miles-davis")
    print(detail.name)
    print(f"  styles : {' / '.join(detail.genres[:6])}")
    print(f"  page   : {detail.url}")
    print(f"  bio    : {(detail.bio or '')[:160]}")
    print(f"  albums : {len(detail.albums)}")

    print("\nUnknown slug raises ArtistNotFound:")
    try:
        jma.fetch_artist("definitely-not-an-artist-xyz")
    except jma.ArtistNotFound as e:
        print(f"  {e}")


if __name__ == "__main__":
    main()
