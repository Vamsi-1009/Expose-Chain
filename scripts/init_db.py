"""Initialize database tables."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import init_db


def main():
    print("Creating database tables...")
    init_db()
    print("Done.")


if __name__ == "__main__":
    main()
