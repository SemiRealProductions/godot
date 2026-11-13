#!/usr/bin/env python3
"""Run against a 3D editor with WebRTC enabled; error output fails the check."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

project = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="classdb-defaults-") as temporary:
    env = dict(os.environ, XDG_DATA_HOME=temporary, XDG_CONFIG_HOME=temporary, XDG_CACHE_HOME=temporary)
    result = subprocess.run(
        [str(Path(sys.argv[1]).resolve()), "--headless", "--path", str(project), "--script", str(project / "check.gd")],
        env=env, capture_output=True, text=True, timeout=30,
    )
output = result.stdout + result.stderr
print(output)
assert result.returncode == 0 and "CLASSDB_EXPLICIT_DEFAULTS_PASS" in output
assert not any(line.startswith(("ERROR:", "SCRIPT ERROR:")) for line in output.splitlines())
