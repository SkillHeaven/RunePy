import sys
from pathlib import Path

# Add repository root to sys.path so tests can import runepy and other modules
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
