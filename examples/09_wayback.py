"""Example 09 — fetch via the Wayback Machine when Cloudflare blocks you.

jazzmusicarchives.com is behind Cloudflare. From a flagged network the live
fetch may hit an unsolvable JS challenge. Two escape hatches, both set by
environment variable (no code change):

- ``PYJAZZMUSICARCHIVES_TRANSPORT=wayback``  — fetch only from the Internet Archive.
- ``PYJAZZMUSICARCHIVES_WAYBACK_FALLBACK=1`` — try live first, fall back to the
  archive on failure.

Archived HTML can be stale, but the parsers are identical either way.

Run::

    PYJAZZMUSICARCHIVES_TRANSPORT=wayback python examples/09_wayback.py
"""
import os

os.environ.setdefault("PYJAZZMUSICARCHIVES_TRANSPORT", "wayback")

import pyjazzmusicarchives as jma


def main() -> None:
    print(f"transport = {os.environ['PYJAZZMUSICARCHIVES_TRANSPORT']}\n")
    detail = jma.fetch_artist("miles-davis")    # from the archived snapshot
    print(detail.name, "—", " / ".join(detail.genres[:4]))
    print(f"{len(detail.albums)} albums; highest rated (>=10 ratings):")
    rated = [a for a in detail.albums if a.avg_rating and (a.num_ratings or 0) >= 10]
    best = max(rated, key=lambda a: a.avg_rating)
    print(f"  {best.title} ({best.year}) — {best.avg_rating} ({best.num_ratings} ratings)")


if __name__ == "__main__":
    main()
