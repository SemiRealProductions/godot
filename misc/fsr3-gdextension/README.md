# FSR 3.1.4 GDExtension and Temporal Artifact Lab

This companion addon implements source FSR 3.1.4 outside the Godot renderer.
The custom editor in this repository exposes the experimental ViewportUpscaler
API and the additional temporal metadata needed by the addon. This is not a
standalone addon for stock Godot releases.

Native Linux x86_64, Forward+, Vulkan is the primary tested configuration.
The demo defaults to source FSR 3.1.4 on Linux. No frame generation is included.
Ghosting/image-quality changes are outside this implementation's scope.

## Build from this repository

At the repository root:

```sh
git submodule update --init --recursive
scons platform=linuxbsd target=editor dev_build=no debug_symbols=no -j6
cd misc/fsr3-gdextension
python3 tools/generate_api.py --engine ../../bin/godot.linuxbsd.editor.x86_64
scons platform=linux arch=x86_64 target=template_debug -j6
scons platform=linux arch=x86_64 target=template_release -j6
python3 tools/package_addon.py --platform linux
../../bin/godot.linuxbsd.editor.x86_64 --editor --path demo --rendering-method forward_plus --rendering-driver vulkan
```

Let the editor import the project, then press F5. The HUD reports actual source
dispatches and GPU passes. Controls: 1 Quality-style 0.67, 2 Native AA, 3 basic
compute, 4 bilinear, 5 scale 0.5, 6 native raster; F1–F4 station close-ups, F5
overview, Space pause, C camera motion, R reset history. See demo/ARTIFACT_LAB.md.

For another project, extract the matching addon ZIP (Linux, Windows or combined
desktop) into its root and enable
the **FidelityFX Upscaling** editor plugin. The autoload applies the viewport
settings without manually editing project scripts.

## Windows builds and complete releases

The Windows editor is a native Windows executable. It can be cross-compiled on
Linux with LLVM-MinGW; substitute your toolchain path below. Run the engine build
at the repository root and the addon builds from this directory:

```sh
MINGW_PREFIX=/path/to/llvm-mingw scons platform=windows arch=x86_64 target=editor use_mingw=yes use_llvm=yes mingw_prefix=/path/to/llvm-mingw d3d12=no debug_symbols=no -j6
# From misc/fsr3-gdextension, after generating the matching API:
scons platform=windows arch=x86_64 target=template_debug use_mingw=yes use_llvm=yes mingw_prefix=/path/to/llvm-mingw -j4
scons platform=windows arch=x86_64 target=template_release use_mingw=yes use_llvm=yes mingw_prefix=/path/to/llvm-mingw -j4
```

After building both editor platforms and debug/release addons, commit the source
changes and run this command from the companion directory:

```sh
python3 tools/package_release.py
```

Assets are written under the engine's `bin/fsr3-release/`: Linux/Windows editor
bundles, Linux/Windows/combined addon ZIPs, a standalone demo with both addon
platforms, a complete source ZIP including pinned godot-cpp, and SHA-256 checksums.
Extract the editor bundle and run `Open-FSR3-Lab.sh` (Linux) or
`Open-FSR3-Lab.cmd` (Windows), then press F5 after import. The standalone demo
still requires this matching custom editor. A source ZIP already contains the
submodule contents; skip `git submodule update` when building that archive.

The Windows artifacts are cross-compiled native binaries, not a Wine-based
launcher. Native Windows GPU execution is not tested on this Linux host.

## Verification

From this directory, with a display and GPU available:

```sh
python3 tests/run_gpu_tests.py --engine ../../bin/godot.linuxbsd.editor.x86_64
python3 tests/run_gpu_tests.py --engine ../../bin/godot.linuxbsd.editor.x86_64 --library release
python3 tests/test_fidelityfx_library.py
python3 tests/test_binary_backend.py --engine ../../bin/godot.linuxbsd.editor.x86_64
```

The source suite checks actual GPU passes, Quality/Native AA/0.5 scaling, motion,
resizing, upscaler switching, and reset/sharpness changes. The external native
command test uses an explicitly synthetic provider, not AMD FSR4.

The optional FidelityFXUpscaler class dynamically loads compatible public-API
Vulkan runtimes on Windows; no AMD Windows DLL, custom FSR4 bridge, driver binary,
Wine runtime or portable compiler is distributed here. The native Linux addon
rejects Windows PE DLLs. Native Linux FSR4 is not supported by this release.

## Provenance and engine dependency

See ../../FSR3_EDITOR.md for source links, pinned revisions, additional engine
changes and release instructions. Algorithm source/notices are retained under
thirdparty/amd-ffx; Godot wrappers/shaders were adapted from HydrogenC's Godot
FSR3 implementation. godot-cpp is a pinned submodule. No generated extension API,
compiled library, object file, editor binary or test capture is versioned.
