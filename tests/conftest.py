import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
sys.path.insert(0, str(Path(__file__).parent.parent.resolve() / "lib"))
print(sys.path)
