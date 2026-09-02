"""Verification: confirm _clean_text() strips stage directions + emits SSML."""
import re
from pipeline.run_v7 import _clean_text

if __name__ == "__main__":
    tx1 = "(quietly) We do, Sarah."
    c1, s1 = _clean_text(tx1, "en-US-BrianNeural")
    print(f"Original: {tx1}")
    print(f"Cleaned:  {c1}")
    print(f"SSML:     {s1}")
