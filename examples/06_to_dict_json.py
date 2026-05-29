"""Example 06 — serialise to plain dicts / JSON.

Run::

    python examples/06_to_dict_json.py
"""
import json

import pyjazzmusicarchives as jma


def main() -> None:
    detail = jma.fetch_artist("miles-davis")
    d = detail.to_dict()
    d["albums"] = d["albums"][:2]        # trim for readability
    d["genres"] = d["genres"][:5]
    if d.get("bio"):
        d["bio"] = d["bio"][:80] + "…"
    print(json.dumps(d, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
