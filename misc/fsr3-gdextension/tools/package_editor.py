#!/usr/bin/env python3
"""Package a native Linux or Windows editor with its matching addon and demo."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT.parent.parent


def demo_files():
    for pattern in ['*.gd', '*.gd.uid', '*.tscn', '*.godot', '*.md']:
        for path in sorted((ROOT / 'demo').glob(pattern)):
            if path.is_file():
                yield path


def package_editor(platform, release):
    label = 'Linux' if platform == 'linux' else 'Windows'
    name = 'godot.linuxbsd.editor.x86_64' if platform == 'linux' else 'godot.windows.editor.x86_64.llvm.exe'
    binary = ENGINE / 'bin' / name
    addon = ROOT / f'build/fsr3-{platform}-x86_64.zip'
    if not binary.is_file() or not addon.is_file():
        raise SystemExit(f'Build the {platform} editor and addon ZIP first')
    release.mkdir(parents=True, exist_ok=True)
    output = release / f'Godot-FSR3-Custom-Editor-{label}-x86_64.zip'
    commit = subprocess.check_output(['git', '-C', str(ENGINE), 'rev-parse', 'HEAD'], text=True).strip()
    if commit.encode() not in binary.read_bytes():
        raise SystemExit(f'{binary.name} does not embed the release commit. Rebuild/relink this editor before packaging.')
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(binary, binary.name)
        if platform == 'windows':
            helper = ENGINE / 'bin/godot.windows.editor.x86_64.llvm.console.exe'
            if not helper.is_file():
                raise SystemExit('Build the Windows console helper first')
            archive.write(helper, helper.name)
        for filename in ['LICENSE.txt', 'COPYRIGHT.txt', 'FSR3_EDITOR.md']:
            archive.write(ENGINE / filename, filename)
        for path in demo_files():
            archive.write(path, 'demo/' + path.name)
        with zipfile.ZipFile(addon) as source:
            for entry in source.infolist():
                archive.writestr('demo/' + entry.filename, source.read(entry))
        if platform == 'linux':
            launcher = zipfile.ZipInfo('Open-FSR3-Lab.sh')
            launcher.create_system = 3
            launcher.external_attr = 0o100755 << 16
            archive.writestr(launcher, '#!/usr/bin/env bash\nset -euo pipefail\nrelease_dir=$(cd -- "$(dirname -- "$0")" && pwd)\nexec "$release_dir/godot.linuxbsd.editor.x86_64" --editor --path "$release_dir/demo" --rendering-method forward_plus --rendering-driver vulkan "$@"\n')
            launch = './Open-FSR3-Lab.sh'
            validation = 'Native Linux Vulkan GPU rendering was tested on RX 9070 XT / RADV.'
        else:
            archive.writestr('Open-FSR3-Lab.cmd', '@echo off\r\n"%~dp0godot.windows.editor.x86_64.llvm.exe" --editor --path "%~dp0demo" --rendering-method forward_plus --rendering-driver vulkan %*\r\n')
            launch = 'Open-FSR3-Lab.cmd'
            validation = 'Native Windows binaries were cross-compiled on Linux; Windows GPU execution has not been tested.'
        archive.writestr('README.txt', f'Experimental Godot custom FSR3 editor ({label} x86_64).\nExtract the ZIP and run {launch}, let the editor import, then press F5.\nThe included demo/addon uses source FSR 3.1.4 through Forward+/Vulkan.\nFSR3 is supplied by the addon, not enabled globally in every project.\nNo external AMD runtime DLL is required for source FSR3.\nNative Linux FSR4 and frame generation are not included.\n{validation}\nSource commit: {commit}\n')
    addon_copy = release / addon.name
    addon_copy.write_bytes(addon.read_bytes())
    return [output, addon_copy]


def write_checksums(paths, release):
    checksums = release / 'SHA256SUMS.txt'
    checksums.write_text(''.join(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n' for path in paths))
    return checksums


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=['linux', 'windows', 'all'], default='linux')
    parser.add_argument('--output-dir', type=Path, default=ENGINE / 'bin/fsr3-release')
    args = parser.parse_args()
    paths = []
    for platform in (['linux', 'windows'] if args.platform == 'all' else [args.platform]):
        paths.extend(package_editor(platform, args.output_dir))
    paths.append(write_checksums(paths, args.output_dir))
    for path in paths:
        print(path)


if __name__ == '__main__':
    main()
