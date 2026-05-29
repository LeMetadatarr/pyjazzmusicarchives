"""Example 01 — browse the A–Z artist index.

Run::

    python examples/01_browse_by_letter.py
"""
import pyjazzmusicarchives as jma


def main() -> None:
    artists = jma.get_artists_by_letter("A")
    print(f"{len(artists)} artists whose name starts with A\n")
    for a in artists[:12]:
        print(f"  {a.display_name:<34} {a.genre or '':<22} {a.country or ''}")
        print(f"       {a.url}")


if __name__ == "__main__":
    main()
