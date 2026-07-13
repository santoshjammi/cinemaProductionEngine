"""Entry point for `python -m movie_os`."""
import sys

from movie_os.cli import main

sys.exit(main(sys.argv[1:]))
