"""Example 05 — an artist's rated discography.

Run::

    python examples/05_discography.py
"""
import pyjazzmusicarchives as jma


def main() -> None:
    detail = jma.fetch_artist("miles-davis")
    print(f"{detail.name}: {len(detail.albums)} albums\n")

    for a in sorted(detail.albums, key=lambda x: x.year or 0)[:15]:
        rating = f"{a.avg_rating:.2f}" if a.avg_rating is not None else "  -  "
        print(f"  {a.year or '????'}  {rating}  {a.subgenre or '':<14} {a.title[:48]}")

    rated = [a for a in detail.albums if a.avg_rating is not None and (a.num_ratings or 0) >= 10]
    if rated:
        best = max(rated, key=lambda x: x.avg_rating)
        print(f"\nHighest rated (>=10 ratings): {best.title} ({best.avg_rating:.2f}, "
              f"{best.num_ratings} ratings)")


if __name__ == "__main__":
    main()
