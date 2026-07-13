"""Backends package — register all available render backends here.

To add a new backend:
1. Create a new file in this directory (e.g. `flux.py`)
2. Subclass `RenderBackend`
3. Export it from this `__init__.py`
4. Register it with the orchestrator in your pipeline code
"""

from .sdxl_local import SDXLLocalBackend

# Future backends (stubs — implement when needed):
# from .flux import FluxBackend
# from .openai import OpenAIBackend
# from .stock_footage import StockFootageBackend

__all__ = [
    "SDXLLocalBackend",
    # "FluxBackend",
    # "OpenAIBackend",
    # "StockFootageBackend",
]