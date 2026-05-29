"""Optional metadatarr ``MetadataProvider`` for jazzmusicarchives.com.

Importing this module registers :class:`JazzMusicArchivesProvider` with the
metadatarr resolver. No-op if metadatarr / mediavocab are absent.

Activates for ``PlaybackType.AUDIO`` signals tagged ``"jazz"``. Resolves an
artist to its jazzmusicarchives slug and emits an ``EntityRole.ARTIST``, from
which metadatarr derives a deterministic canonical entity id.

Usage::

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
"""
from __future__ import annotations

from typing import ClassVar, Optional, Set

try:
    from metadatarr.resolve.base import MetadataProvider, ProviderMatch, register
    from metadatarr.resolve.entities import EntityRole, ProviderEntity
    from mediavocab import PlaybackType
    from mediavocab.models import ExternalIds
    from mediavocab.models.signals import Signals
    _AVAILABLE = True
except ImportError:  # pragma: no cover
    _AVAILABLE = False

import pyjazzmusicarchives as _lib


if _AVAILABLE:

    def _confidence(query: str, hit: str) -> float:
        q, h = query.lower().strip(), hit.lower().strip()
        if not q:
            return 0.0
        if q == h:
            return 0.95
        if q in h or h in q:
            return 0.75
        qt, ht = set(q.split()), set(h.split())
        return 0.4 + 0.3 * (len(qt & ht) / max(1, len(qt)))

    class JazzMusicArchivesProvider(MetadataProvider):
        """Resolve a jazz artist to its jazzmusicarchives slug + entity."""

        name: ClassVar[str] = "jazzmusicarchives"
        playback_type: ClassVar[Set["PlaybackType"]] = {PlaybackType.AUDIO}
        genre_filter: ClassVar[Set[str]] = {"jazz"}

        def is_available(self) -> bool:
            return True

        def lookup(self, signals: "Signals") -> Optional["ProviderMatch"]:
            query = (signals.artist or signals.title or "").strip()
            if not query:
                return None
            try:
                hits = _lib.search_artists(query, limit=1)
            except Exception:
                return None
            if not hits:
                return None
            best = hits[0]
            entity = ProviderEntity(
                role=EntityRole.ARTIST,
                name=best.display_name,
                external_ids=ExternalIds(extra={"jazzmusicarchives_artist": best.slug}),
            )
            return ProviderMatch(
                provider=self.name,
                confidence=_confidence(query, best.display_name),
                external_ids=ExternalIds(extra=best.to_external_ids_dict()),
                relations={EntityRole.ARTIST: [entity]},
            )

    register(JazzMusicArchivesProvider())
