"""Entry point for `python -m movie_os.genesis`."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())