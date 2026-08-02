# Building a Hugging Face dataset

jazzmusicarchives data is a small graph: artist to albums. For Hugging Face you want flat tables. `pyjazzmusicarchives.dataset` emits two streams that share `artist_slug`.

## What columns and rows?

### Table 1 -- `artists` (headline table)

**One row per artist.** The cheap version (`artist_rows`, built from the index, with no per-artist fetch):

| Column | Type | Example |
|---|---|---|
| `artist_slug` | string | `"miles-davis"` |
| `name` | string | `"DAVIS, MILES"` (as listed) |
| `display_name` | string | `"MILES DAVIS"` |
| `genre` | string | `"Cool Jazz"` (primary) |
| `country` | string | `"United States"` |
| `url` | string | canonical page |

The rich version (`artist_detail_row`, one fetch per artist) adds **`genres`** (the full style list), **`bio`** (the free-text biography, the headline NLP feature), and `n_albums`.

**Rows:** thousands of artists (letter A alone holds about 630).

### Table 2 -- `albums`

**One row per album**, from `album_rows(detail)`:

| Column | Type | Notes |
|---|---|---|
| `album_id` | int64 | canonical id |
| `artist_slug` | string | **join key** |
| `artist_name` | string | denormalized |
| `title` | string | |
| `subgenre` | string | per-album style, e.g. `"Cool Jazz"` |
| `year` | int64 | release year |
| `avg_rating` | float64 | member average, 0-5; null when unrated |
| `num_ratings` | int64 | sample size and popularity weight |
| `cover` | string | image URL |
| `url` | string | |

## Why this shape

- **`artist_slug` everywhere** joins the two tables and gives every row a stable canonical key.
- **`avg_rating` and `num_ratings`** give an out-of-the-box rating-prediction target with a confidence weight. Filter to `num_ratings >= N` for reliable labels.
- **`subgenre`** per album and **`genres`** per artist form a jazz-style taxonomy for classification.
- **`bio`** is the long free-text field for classification, retrieval, or summarization.
- Consistent nulls (`avg_rating = None` for unrated albums) keep the Arrow schema stable.

## Recipe

```python
import itertools, pyjazzmusicarchives as jma
from pyjazzmusicarchives import dataset

# Headline table for one initial (cheap)
rows = list(dataset.artist_rows(jma.get_artists_by_letter("A")))

# Whole index to JSONL (cheap rows)
dataset.write_jsonl("artists.jsonl", dataset.build_dataset())
# Rich variant (slow: one request per artist, throttle yourself)
# dataset.write_jsonl("artists_rich.jsonl", dataset.build_dataset(with_detail=True))

# Albums table for a set of artists
albums = []
for a in itertools.islice(jma.iter_artists(), 100):
    albums.extend(dataset.album_rows(jma.fetch_artist(a.slug)))
dataset.write_jsonl("albums.jsonl", albums)
```

## Load into Hugging Face `datasets`

```python
from datasets import Dataset, DatasetDict
ds = DatasetDict({
    "artists": Dataset.from_json("artists.jsonl"),
    "albums":  Dataset.from_json("albums.jsonl"),
})
ds.push_to_hub("your-org/jazz-music-archives")
```

> Be polite when you scrape the full index for the rich or album tables. Throttle your requests. See [advanced.md](advanced.md).

See `examples/08_build_dataset.py` for a runnable version.

---
[← Canonical ids](canonical_ids.md) · [Home](../README.md)
