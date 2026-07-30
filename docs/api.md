# API reference

Everything below is re-exported from the top-level `pyjazzmusicarchives` package, aliased `jma`.

## Functions

### `get_artists_by_letter(letter: str) -> List[Artist]`
Every artist whose name starts with `letter` (A-Z). Raises `ValueError` otherwise.

### `iter_artists(letters: str | None = None) -> Iterator[Artist]`
Iterates the full A-Z index lazily, one initial at a time. Pass `letters` (for example `"ABC"`) to restrict the range.

### `get_all_artists(letters: str | None = None) -> List[Artist]`
The eager version of `iter_artists`.

### `fetch_artist(slug: str) -> ArtistDetail`
The full artist page: styles, biography, and rated discography. Accepts a slug (`"miles-davis"`) or a full artist URL. Raises **`ArtistNotFound`** if the page carries no artist.

### `search_artists(query: str, limit: int | None = None) -> List[Artist]`
Searches the by-letter index client-side. It fetches the listings for the initials in `query`, keeps artists whose name contains every token, and ranks exact and prefix matches first. `limit` caps the results.

## Models

All models are `@dataclass`es. Each shares this interface: `site_id`, `url`, `to_dict()`, `to_external_ids_dict()`.

### `Artist` (list-level)

| Field | Type | Notes |
|---|---|---|
| `slug` | `str` | canonical id (URL slug) |
| `name` | `str` | as listed, surname-first, e.g. `"DAVIS, MILES"` |
| `genre` | `str \| None` | primary style |
| `country` | `str \| None` | |

Properties: `site_id` (= slug), `display_name` (`"MILES DAVIS"`), `url` (`/artist/<slug>`). External ids: `{"jazzmusicarchives_artist", "jazzmusicarchives_url"}`.

### `ArtistDetail` (full page)

| Field | Type | Notes |
|---|---|---|
| `slug` | `str` | canonical id |
| `name` | `str` | natural form, e.g. `"MILES DAVIS"` |
| `genres` | `List[str]` | the styles the artist worked across |
| `country` | `str \| None` | often `None` here -- the listing carries it |
| `bio` | `str \| None` | plain-text biography |
| `albums` | `List[Album]` | rated discography |

The `genre` property returns the first entry of `genres`, for parity with `Artist`.

### `Album`

| Field | Type | Notes |
|---|---|---|
| `album_id` | `int` | canonical id |
| `title` | `str` | |
| `slug` | `str \| None` | path under `/album/`, e.g. `"miles-davis/kind-of-blue"` |
| `subgenre` | `str \| None` | per-album style, e.g. `"Cool Jazz"` |
| `year` | `int \| None` | release year |
| `avg_rating` | `float \| None` | member average, 0-5; `None` when unrated |
| `num_ratings` | `int \| None` | number of member ratings |
| `cover` | `str \| None` | cover image URL |
| `artist_slug` / `artist_name` | `str \| None` | back-references |

Properties: `site_id` (= album_id), `url` (`/album/<slug>`). External ids: `{"jazzmusicarchives_album", "jazzmusicarchives_url"}`.

## Exceptions

### `ArtistNotFound`
Raised by `fetch_artist` when the slug yields no artist.

## Pages used

| Path | Wrapped by |
|---|---|
| `/ListArtistsAlpha.aspx?letter=` | `get_artists_by_letter`, `iter_artists`, `search_artists` |
| `/artist/<slug>` | `fetch_artist` |

---
[← Quickstart](quickstart.md) · [Home](../README.md) · [Advanced usage →](advanced.md)
