#!/usr/bin/env python3
"""Package both native editors, platform/universal addons, demo and complete source."""
import argparse
from pathlib import Path
import subprocess
import tempfile
import zipfile

from package_editor import ROOT, ENGINE, demo_files, package_editor, write_checksums


def package_source(release):
    # Archive committed trees, never the working directory or compiler outputs.
    if subprocess.check_output(['git', '-C', str(ENGINE), 'status', '--porcelain'], text=True).strip():
        raise SystemExit('Commit or remove outstanding source changes before packaging a release')
    submodule = ROOT / 'godot-cpp'
    expected = subprocess.check_output(['git', '-C', str(ENGINE), 'rev-parse', 'HEAD:misc/fsr3-gdextension/godot-cpp'], text=True).strip()
    actual = subprocess.check_output(['git', '-C', str(submodule), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != expected or subprocess.check_output(['git', '-C', str(submodule), 'status', '--porcelain'], text=True).strip():
        raise SystemExit('godot-cpp must be clean and match the pinned submodule revision')
    output = release / 'Godot-FSR3-Source-with-submodules.zip'
    prefix = 'Godot-FSR3-Source/'
    subprocess.run(['git', '-C', str(ENGINE), 'archive', '--format=zip', '--prefix=' + prefix, '--output=' + str(output.resolve()), 'HEAD'], check=True)
    with tempfile.TemporaryDirectory(prefix='godot-fsr3-source-') as temporary:
        module_zip = Path(temporary) / 'godot-cpp.zip'
        subprocess.run(['git', '-C', str(submodule), 'archive', '--format=zip', '--output=' + str(module_zip), expected], check=True)
        with zipfile.ZipFile(output, 'a', zipfile.ZIP_DEFLATED) as archive, zipfile.ZipFile(module_zip) as module:
            for info in module.infolist():
                target = zipfile.ZipInfo(prefix + 'misc/fsr3-gdextension/godot-cpp/' + info.filename, info.date_time)
                target.external_attr = info.external_attr
                target.create_system = info.create_system
                target.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(target, module.read(info))
            commit = subprocess.check_output(['git', '-C', str(ENGINE), 'rev-parse', 'HEAD'], text=True).strip()
            archive.writestr(prefix + 'SOURCE_COMMIT.txt', commit + '\nIncludes the pinned godot-cpp sources. Skip git submodule update when building this source ZIP.\n')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ENGINE / 'bin/fsr3-release')
    args = parser.parse_args()
    release = args.output_dir.resolve()
    release.mkdir(parents=True, exist_ok=True)
    for platform in ['linux', 'windows', 'all']:
        subprocess.run(['python3', str(ROOT / 'tools/package_addon.py'), '--platform', platform], check=True)
    paths = package_editor('linux', release) + package_editor('windows', release)
    desktop = ROOT / 'build/fsr3-desktop-x86_64.zip'
    desktop_copy = release / desktop.name
    desktop_copy.write_bytes(desktop.read_bytes())
    paths.append(desktop_copy)
    demo = release / 'FSR3-Temporal-Artifact-Lab.zip'
    with zipfile.ZipFile(demo, 'w', zipfile.ZIP_DEFLATED) as archive, zipfile.ZipFile(desktop) as addon:
        for path in demo_files():
            archive.write(path, 'FSR3-Temporal-Artifact-Lab/' + path.name)
        for entry in addon.infolist():
            archive.writestr('FSR3-Temporal-Artifact-Lab/' + entry.filename, addon.read(entry))
        archive.writestr('FSR3-Temporal-Artifact-Lab/README.txt', 'Open project.godot with the matching custom Godot 4.8 editor, let it import, then press F5.\nContains Linux and Windows x86_64 addon libraries. Uses Forward+/Vulkan and source FSR 3.1.4.\n')
    paths.extend([demo, package_source(release)])
    paths.append(write_checksums(paths, release))
    for path in paths:
        print(path)


if __name__ == '__main__':
    main()
