"""Example 08 — metadatarr provider integration.

Importing ``pyjazzmusicarchives._provider`` registers a MetadataProvider that
resolves a jazz artist to its jazzmusicarchives slug and a canonical artist
entity. Requires ``metadatarr`` + ``mediavocab``.

This drives the provider directly so it is self-contained; in a pipeline you
would call ``metadatarr.resolve.base.resolve(signals)``.

Run::

    python examples/08_metadatarr.py
"""
import pyjazzmusicarchives._provider as provider_mod  # registers the provider


def main() -> None:
    from mediavocab.models.signals import Signals
    from mediavocab import PlaybackType
    from metadatarr.resolve.entities import EntityRole, allocate_entity_id

    provider = provider_mod.JazzMusicArchivesProvider()
    signals = Signals(
        artist="Miles Davis",
        playback_type=PlaybackType.AUDIO,
        content_genres=["jazz"],
    )

    match = provider.lookup(signals)
    print(f"provider    : {match.provider}")
    print(f"confidence  : {match.confidence}")
    print(f"external ids: {match.external_ids.extra}")

    for e in match.relations.get(EntityRole.ARTIST, []):
        canonical = allocate_entity_id(EntityRole.ARTIST, name=e.name,
                                       external_ids=e.external_ids)
        print(f"\nentity: {e.name}")
        print(f"  kind         : {e.kind}")
        print(f"  external ids : {e.external_ids.extra}")
        print(f"  canonical id : {canonical}")

    print("\nMatches AUDIO+jazz signal?", provider.matches(signals))


if __name__ == "__main__":
    main()
