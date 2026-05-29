# TODO — pyjazzmusicarchives

## Open issues

None open.

## Gaps

- [ ] No CI workflows. Add gh-automations reusable workflows (`build-tests`,
      `coverage`, `license-check`, `release_workflow`, `publish_stable`) at `@dev`.
- [ ] No `.github/` directory.
- [ ] No linter/type checker configured (mypy/ruff).
- [ ] No live smoke test — the suite parses saved fixtures only (the live site
      is Cloudflare-gated, so live verification needs an unblocked network).

## Possible enhancements

- [ ] Album detail pages (`/album/<slug>`) — tracklist, lineup, reviews — could
      back a `fetch_album()`.
- [ ] `ArtistDetail.country` is not parsed from the artist page (only the
      listing carries it reliably); a flag/region parse could fill it.
- [ ] `to_mediavocab()` helpers building `Release`/`Entity` objects.
- [ ] Multi-comma listed names flip imperfectly in `display_name`.

## Code TODOs

None found.
