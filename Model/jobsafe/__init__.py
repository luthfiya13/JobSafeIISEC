# Forwarding package to preserve original import paths after moving the implementation.
# The actual implementation now lives in `src.jobsafe`.

import sys
from pathlib import Path
from importlib import import_module

# Ensure `src` is on the import path.
src_dir = Path(__file__).resolve().parents[1] / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

_real_pkg = import_module("jobsafe")  # imports from src.jobsafe due to sys.path order

# Re‑export public symbols.
__all__ = getattr(_real_pkg, "__all__", [])
for name in __all__:
    globals()[name] = getattr(_real_pkg, name)
