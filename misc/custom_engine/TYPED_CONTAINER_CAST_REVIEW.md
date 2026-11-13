# Typed-container casting compatibility review

Reviewed 13 November 2026 against `semi-real-engine` and upstream
[Godot PR #124662](https://github.com/godotengine/godot/pull/124662), revision
`d699842a191c76652875a8c434bd6189ce1989e2`.

**Status: assessed only; not imported.** The other four requested imports do not
change GDScript container casting.

## Behaviour and secondary effects

The proposal adds typed-array and typed-dictionary cast opcodes and stricter
analyser checks. The VM checks the container's declared type metadata, including
native/script element types. It does not inspect an untyped array's contents and
turn them into a typed container. Relevant changes are in the analyser, bytecode
generator, VM, disassembler and warnings, with analyser/runtime regression cases.

| Code / situation | Effect if the PR is adopted |
| --- | --- |
| `var a = [1]; a as Array[String]` | Invalid cast is caught instead of allowing later invalid element operations. A statically known mismatch can be an analyser error; a dynamically typed mismatch fails at runtime. |
| An untyped `Array` containing only strings, cast with `as Array[String]` | Matching contents alone are insufficient. The runtime requires matching container type metadata; the cast does not convert the array. |
| `PackedStringArray` cast with `as Array[String]` | Rejected rather than converted. The PR explicitly chooses this behaviour. Use a deliberately constructed typed array and validate/convert its elements. |
| `Array[Node2D]` cast with `as Array[Node]` | Element types must match exactly; inheritance of the element classes does not make mutable typed arrays covariant. The same concern applies to dictionaries. |
| Partially typed dictionaries | Key and value type metadata must match. `Dictionary[String, String]` cannot be widened to `Dictionary[String, Variant]` merely with a cast. |
| Dynamic or untyped container casts | Can introduce `unsafe_cast` warnings. Projects treating those warnings as errors may stop parsing until scripts are updated. |
| Invalid casts on a gameplay path | May stop the current script call instead of continuing until a later failure. Treat casts as assertions about an existing type, not conversion or a nullable test for compatibility. |
| Valid, already correctly typed containers | Remain the expected use case; no automatic benefit to general rendering, physics or loading performance is established. |

For intentional conversion, create the destination type explicitly and validate
or convert each element. `Array.assign()` / `Dictionary.assign()` can be useful
where their conversion semantics match the intended data; they should not be
blind substitutions for every cast. Prefer an explicit loop when conversion is
part of the application's rules.

## Backrooms Game Show scan

A read-only text scan covered **197 GDScript files, including 21 installed addon
files**, following dependency symlinks and excluding `.godot` caches.

- No direct `as Array[T]` or `as Dictionary[K, V]` casts were found.
- Lazy Godot VOIP contains three `as PackedByteArray` casts and one unparameterised
  `as Array` cast. These are not the new typed-container target opcodes and do not
  directly trigger the new exact-metadata checks. Their input values must still
  be valid under the existing general casting rules.
- Ordinary typed variable/argument declarations are not the same as an explicit
  `as` cast. Their presence alone does not establish a regression from this PR.
- This scan does not prove compatibility: aliases, generated code, other script
  languages and data-dependent runtime paths were not evaluated.

No game files or dependencies were changed. The game was not run against an
editor containing this PR, so runtime compatibility remains untested.

## Formats, builds and maintenance

No new scene/resource format or save-game schema is introduced by the patch.
The new opcodes are an internal VM/compiler change. Godot's exported `.gdc` files
store tokenizer data, not these executable VM opcodes, so opcode insertion alone
is not evidence of a blanket `.gdc` format incompatibility. The important change
is how the scripts are analysed and executed by the new engine.

Updated export templates would be needed to ship the new runtime behaviour.
Using a changed editor with older templates can leave editor and exported-game
casting behaviour different. Existing GDExtension interfaces are not changed by
this patch, although scripts calling extensions may expose incompatible container
metadata returned by those extensions.

It also overlaps the GDScript analyser/parser/VM and could conflict with later
language improvements, including independently reviewed typed-container
optimisations. Those should be evaluated separately rather than stacked blindly.

## Recommendation

The known source-level exposure in our current game is low, and catching invalid
casts is useful. Nevertheless, keep this as a separate decision from the four
requested imports. Before adoption, run the upstream analyser/runtime tests in
both debug and release configurations, add valid/invalid untyped-container and
subclass cases, parse the game and installed addons, and exercise networking,
VOIP and resource-loading paths with matching export templates.
