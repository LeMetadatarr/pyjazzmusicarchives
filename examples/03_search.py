"""Example 03 — search artists by name (client-side over the index).

Run::

    python examples/03_search.py
"""
import pyjazzmusicarchives as jma


def main() -> None:
    for query in ["miles davis", "john coltrane", "duke ellington"]:
        hits = jma.search_artists(query, limit=3)
        print(f"{query!r} -> {len(hits)} hit(s)")
        for a in hits:
            print(f"    {a.display_name}  ({a.genre}, {a.country})  [{a.slug}]")
        print()


if __name__ == "__main__":
    main()
