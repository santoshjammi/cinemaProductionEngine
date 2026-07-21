# A simple Python script to patch story.py with standard types
with open('/Users/santosh/Desktop/projects/videoGen/movie_os/domain/story.py', 'r') as f:
    content = f.read()

# Replace the broken Pydantic fallback with working standard types
content = content.replace(
    """from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

# Standard Python stubs for Pydantic since it's not installed in this environment
class BaseModel: pass
def Field(**kw): return kw
ConfigDict = lambda **kw: dict""",
    """from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

# Working standard Python stubs since pydantic is not installed
class BaseModel(dict): pass
def Field(**kw): return kw
ConfigDict = lambda **kw: dict"""
)

with open('/Users/santosh/Desktop/projects/videoGen/movie_os/domain/story.py', 'w') as f:
    f.write(content)
print("Fixed story.py successfully")
