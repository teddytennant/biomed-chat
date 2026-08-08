import sys
from pathlib import Path

# Add the project root to sys.path so tests can import modules directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
