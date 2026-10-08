# Forwarding package to preserve original import paths after moving the implementation.
# The actual implementation now lives in `src.jobsafe`.

from pathlib import Path

# Keep the historical ``Model/jobsafe`` import path while loading the
# implementation from ``Model/src/jobsafe/jobsafe``.  Importing ``jobsafe``
# from this module recursively imported this forwarding package itself, so
# submodules such as ``jobsafe.verification`` were unavailable.
implementation_dir = Path(__file__).resolve().parents[1] / "src" / "jobsafe" / "jobsafe"
__path__.append(str(implementation_dir))

from .engine import JobsafeEngine
from .hybrid_engine import JobsafeHybridEngine
from .ml_model import JobsafeMLModel
from .pipeline import process_input
from .verification import VerificationLayer

__all__ = [
    "JobsafeEngine",
    "JobsafeHybridEngine",
    "JobsafeMLModel",
    "VerificationLayer",
    "process_input",
]
