# Canonical identifiers (for dedup & cross-referencing)

This client's job is to expose jazzmusicarchives' **stable identifiers** so a
downstream resolver can de-duplicate and cross-reference. The resolver itself —
the metadatarr `MetadataProvider` — lives in the **[metadatarr](../../metadatarr)**
repo, not here. This package is a pure scraper; metadatarr *consumes* it.

## What this client exposes

jazzmusicarchives identifies an artist by a stable URL **slug**
(`"miles-davis"`) and an album by a numeric id. Each model surfaces them two
ways:

| Entity | `site_id` | Canonical web URL | `to_external_ids_dict()` keys |
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

`to_external_ids_dict()` returns exactly the shape metadatarr stores under
`ExternalIds.extra` (a free-form string→string namespace). Two records sharing
`jazzmusicarchives_artist` are the same artist — that's your **dedup / join
key**.

## How metadatarr consumes this

metadatarr ships a provider (`metadatarr/resolve/providers/jazzmusicarchives.py`)
that imports this library, resolves an artist for `PlaybackType.AUDIO` +
`"jazz"` signals, and emits the external ids above plus an `EntityRole.ARTIST`
(group) entity. From that entity metadatarr derives a deterministic canonical
entity id (`allocate_entity_id`), so the same artist collapses to one entity
across providers.

You do not import or configure anything here for that to work — installing both
`pyjazzmusicarchives` and `metadatarr` is enough; metadatarr auto-discovers the
provider and self-disables it if this library is not installed. See the
metadatarr repo for resolver usage.
