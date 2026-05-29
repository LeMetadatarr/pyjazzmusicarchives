# metadatarr integration — canonical ids & entity lookup

Two questions: **what are the canonical identifiers**, and **how do you do
entity/media lookup with them?**

## Canonical identifiers

jazzmusicarchives identifies an artist by a stable URL **slug**
(`"miles-davis"`) and an album by a numeric id. Those are the canonical keys:

| Entity | `site_id` | Canonical URL | `to_external_ids_dict()` keys |
|---|---|---|---|
| Artist | slug | `/artist/<slug>` | `jazzmusicarchives_artist`, `jazzmusicarchives_url` |
| Album | album id | `/album/<slug>` | `jazzmusicarchives_album`, `jazzmusicarchives_url` |

```python
import pyjazzmusicarchives as jma
m = jma.search_artists("miles davis")[0]
m.site_id                    # 'miles-davis'
m.to_external_ids_dict()
# {'jazzmusicarchives_artist': 'miles-davis', 'jazzmusicarchives_url': '...'}
```

These live under `ExternalIds.extra` in [mediavocab](../../mediavocab) — a
free-form string→string namespace. Two records sharing
`jazzmusicarchives_artist` are the same artist: that's your **dedup / join key**.

## Entity lookup

An artist is an entity. The provider emits a `ProviderEntity` under
`EntityRole.ARTIST`, and metadatarr turns it into a deterministic **canonical
entity id** via `allocate_entity_id`:

```python
from metadatarr.resolve.entities import EntityRole, ProviderEntity, allocate_entity_id
from mediavocab.models import ExternalIds

entity = ProviderEntity(
    role=EntityRole.ARTIST,                       # → EntityKind.GROUP
    name="MILES DAVIS",
    external_ids=ExternalIds(extra={"jazzmusicarchives_artist": "miles-davis"}),
)
canonical = allocate_entity_id(EntityRole.ARTIST, name=entity.name,
                               external_ids=entity.external_ids)
# stable sha1 seeded from the slug — same artist ⇒ same entity id across providers.
```

## The resolver provider

Importing `pyjazzmusicarchives._provider` registers a `MetadataProvider` (no-op
without metadatarr/mediavocab). It activates for `PlaybackType.AUDIO` signals
tagged `"jazz"`, resolves the artist (preferring `signals.artist`, then
`signals.title`), and returns the external ids plus the artist entity.

```python
import pyjazzmusicarchives._provider
from metadatarr.resolve.base import resolve
from mediavocab.models.signals import Signals
from mediavocab import PlaybackType

result = resolve(Signals(
    artist="Miles Davis",
    playback_type=PlaybackType.AUDIO,
    content_genres=["jazz"],
))
print(result.external_ids.extra)
```

### Confidence

| Match | Confidence |
|---|---|
| exact artist name (natural order) | 0.95 |
| one contains the other | 0.75 |
| token overlap | 0.40–0.70 |

Matching uses `display_name` (natural order), so surname-first listings still
score as exact matches.

### Driving the provider directly

```python
import pyjazzmusicarchives._provider as p
prov = p.JazzMusicArchivesProvider()
match = prov.lookup(Signals(artist="John Coltrane",
                            playback_type=PlaybackType.AUDIO,
                            content_genres=["jazz"]))
print(match.external_ids.extra, match.confidence)
```

See `examples/08_metadatarr.py` for a runnable script.

## Scope

The provider resolves **artists**. Album ids and per-album sub-genres are
exposed on `ArtistDetail.albums` for you to join on, but the resolver match
anchors on the artist. Combine with MusicBrainz / Discogs providers for
recording-level cross-references.
