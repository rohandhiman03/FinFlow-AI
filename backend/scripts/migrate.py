import argparse

from app.db import init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize or migrate database schema.")
    parser.add_argument("--dry-run", action="store_true", help="Print action without executing")
    args = parser.parse_args()

    if args.dry_run:
        print("[dry-run] Would initialize database schema via SQLAlchemy metadata.create_all")
        return

    init_db()
    print("Database schema initialized successfully.")


if __name__ == "__main__":
    main()
