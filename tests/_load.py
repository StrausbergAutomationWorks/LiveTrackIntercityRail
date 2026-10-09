"""Import the component's HA-free modules without Home Assistant.

The package __init__ imports Home Assistant, so it must never run here. This
registers the component folder as a bare package named `ltir` whose __init__
is skipped; `ltir.attributes`, `ltir.operators` and `ltir.sources.amtraker`
then import normally, relative imports included. Live Track Commuter Rail's
tests/_load.py, renamed.

Run from the repo root, in a Python with saw-livetrack[gtfs] installed
(bin\\ltcr_venv on this machine):  python -m unittest discover -s tests -v
"""

import importlib
import importlib.machinery
import importlib.util
import pathlib
import sys

COMP = (pathlib.Path(__file__).resolve().parents[1]
        / "custom_components" / "live_track_intercity_rail")

if "ltir" not in sys.modules:
    spec = importlib.machinery.ModuleSpec("ltir", None, is_package=True)
    pkg = importlib.util.module_from_spec(spec)
    pkg.__path__ = [str(COMP)]
    sys.modules["ltir"] = pkg


def load(name: str):
    return importlib.import_module(f"ltir.{name}")
