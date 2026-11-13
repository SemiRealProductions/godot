# Upstream imports — 13 November 2026

These source changes extend `semi-real-engine` from baseline `ee3506e801`.
They do not update the installed editor or export templates. The four imports
and their documentation were pushed on 14 November 2026; no release was made.

| Change | Original author / upstream revision | Adaptation |
| --- | --- | --- |
| [#114351 — Avoid duplicate CSG updates](https://github.com/godotengine/godot/pull/114351) | Emanuel Acosta Gonzalez (emanvidmaker), `5e2bbbc5ed7da47236de006cc2a1ff990c84f19d` | Original one-line scheduling fix. |
| [#106292 — Box-projected probe contact hardening](https://github.com/godotengine/godot/pull/106292) | landervr, `f5a518f5b5c149e73516e0d7ffd46285c2a1d18d` | Preserve the original linear LOD mapping for non-box Compatibility probes. The visual change remains scoped to box projection. |
| [#125221 — Deterministic imported scene node IDs](https://github.com/godotengine/godot/pull/125221) | spookto, `70c2c7c1d8232a084a7097471b999106b4828d7c` | Reserve all importer-supplied IDs first, and use a HashSet to avoid repeated linear membership scans. |
| [#119996 — Code regions in the script outline](https://github.com/godotengine/godot/pull/119996) | Dexter, `3738804a829c5349c232b50392374b5e32060575` | Port to DocumentOutline, preserving subclass grouping, fuzzy filtering and selection. Add nested/unfinished regions, sibling sorting and fold-state restoration across filtering. |

Original authors and upstream PR/commit provenance are recorded in the individual
commits according to [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Observable effects

- CSG scheduling avoids redundant deferred root updates. This is not asynchronous
  CSG construction and does not remove all room-loading stalls.
- Box-projected reflection probes change appearance without a new toggle. Review
  roughness and SSR/probe transitions in existing rooms. This is an approximation,
  not traced scene reflections; transparent and clearcoat paths need visual checks.
- Imported node IDs become deterministic when an importer does not supply its own
  IDs. The first reimport may cause a one-time scene-ID diff. Generation retains
  upstream's resource-UID/node-name scheme; renaming a node or changing traversal
  order among colliding names can still change generated IDs. Existing assigned
  IDs are preserved; pre-existing duplicate supplied IDs are not repaired.
- In the built-in script editor, `#region Name` / `#endregion` create collapsible
  outline groups. Nested regions work; unnamed ones display “Region”. An unfinished
  region extends through the end of the current document while editing. Subclass
  headings are retained within the containing region. Name filtering keeps the
  matching methods and their context rather than displaying unrelated regions.
- Folder/group keys use source positions, so moving a region can reset its fold
  state. These changes do not create script-list folders or alter runtime scripts.

## Focused validation

The local working records are under `bin/pr-integration-2026-11-13/` (ignored build
and test output, excluded from source commits).

- Source-derived CSG scheduling harness: previous code fails the duplicate-queue
  regression; imported code passes root, repeated-update, child and removal cases.
- Source-derived node-ID harness: upstream code fails a collision with a preserved
  ID visited later; adapted code passes preservation, repeated-name, repeat-import,
  unassigned-ID and 5,000-node cases.
- Source-derived outline harness with lightweight UI/type adapters: previous code
  has no region groups; adapted method passes nested/unfinished/unnamed regions,
  subclass scopes, ordering, selection, filter/fold restoration, docs and empty
  results. The adapters do not replace a full editor UI test.
- Extracted modified reflection expressions compiled and executed on the RX 9070 XT
  using the existing editor's local Vulkan RenderingDevice: RD float/half and
  Compatibility expressions pass LOD endpoint, finite-value, contact-hardening and
  unchanged non-box mapping checks. This does not validate the complete shaders on
  every renderer or driver.
- Linux GCC and Windows LLVM-MinGW syntax checks pass for all three changed C++
  translation units. No full
  editor or template build, native Windows run or performance benchmark was done.

Before publishing binaries, rebuild matching editors/templates and test CSG
reparenting/collision and room timings, repeated GLB imports/inherited overrides,
full Forward+/Mobile/Compatibility shader variants, MSAA/FSR resizing, reflection
appearance and script-outline mouse/keyboard navigation.

## Separate proposal

[#124662 — Typed container casts](https://github.com/godotengine/godot/pull/124662)
was assessed on 13 November and **imported on 14 November 2026** at the user's
request, from `d699842a191c76652875a8c434bd6189ce1989e2`. Original author
HolonProduction and co-author Danil Alexeev are retained in the import commit.
The upstream analyser/runtime regression fixtures are included. Focused Linux /
Windows syntax checks and a debug/release VM-handler adapter harness passed;
full rebuilt-engine suites and game runtime validation remain pending. See the
[compatibility review and watch items](TYPED_CONTAINER_CAST_REVIEW.md).

## Linux test-build follow-up — 14 November 2026

Cold-start testing found three required-virtual getter errors during ClassDB
property-default discovery. The upstream lock-scope change in
[#124892](https://github.com/godotengine/godot/pull/124892) no longer skipped
getters for explicitly registered defaults until after collecting new values.
Copy those defaults under the initial read lock so discovery can skip their
getters, while still performing object construction and property access outside
the lock. This preserves the upstream deadlock fix.

A focused runner at `tests/classdb_defaults/run.py` (relative to this directory)
checks extension defaults, ordinary discovered defaults, repeat queries and the
absence of engine error output. Run it with the editor executable as its argument:

```bash
python3 misc/custom_engine/tests/classdb_defaults/run.py /path/to/godot
```

The test reproduces the three errors in the initial Linux test binary. Linux and
Windows syntax checks pass for the fix; rebuilt-binary validation is recorded in
the test-release build logs rather than assumed from the source checks.
