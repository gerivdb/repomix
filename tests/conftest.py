# conftest.py - Force coverage of __init__ files

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

# Force import to get coverage of __init__.py
import verses_sync  # noqa: F401