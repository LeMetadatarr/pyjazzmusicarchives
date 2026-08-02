"""Example 08 — build flat rows for a Hugging Face dataset.

Run::

    python examples/08_build_dataset.py
"""
import pyjazzmusicarchives as jma
from pyjazzmusicarchives import dataset


def main() -> None:
    rows = list(dataset.artist_rows(jma.get_artists_by_letter("A")))
    print(f"artist_rows(A): {len(rows)} rows")
    print("  columns:", list(rows[0].keys()))
    print("  sample :", rows[0])

    detail = jma.fetch_artist("miles-davis")
    print("\nartist_detail_row keys:", list(dataset.artist_detail_row(detail).keys()))
    albums = list(dataset.album_rows(detail))
    print(f"album_rows: {len(albums)} (sample: {albums[0]})")

    n = dataset.write_jsonl("artists_A_sample.jsonl", rows[:25])
    print(f"\nwrote {n} rows to artists_A_sample.jsonl")


if __name__ == "__main__":
    main()
