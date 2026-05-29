"""Example 02 — stream the whole artist index lazily.

Run::

    python examples/02_stream_all.py
"""
import itertools

import pyjazzmusicarchives as jma


def main() -> None:
    print("First 25 artists across the whole index:")
    for a in itertools.islice(jma.iter_artists(), 25):
        print(f"  {a.display_name:<36} {a.genre or '':<22} {a.country or ''}")


if __name__ == "__main__":
    main()
