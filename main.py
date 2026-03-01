#!/usr/bin/env python3
"""
main.py — Student Record Management System
Entry point: handles environment, DB check, then launches the CLI.

Usage:
    python main.py
    DB_PASSWORD=secret python main.py
"""

import os
import sys

# ── Ensure project root is on the path ───────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

# ── Default environment variables (override via shell or .env) ──────────────
os.environ.setdefault("DB_USER",     "root")
os.environ.setdefault("DB_HOST",     "localhost")
os.environ.setdefault("DB_NAME",     "student_management_db")
os.environ.setdefault("DB_PORT",     "3306")
# DB_PASSWORD must be set externally (env or .env) for security

# ── Optional: load .env file if python-dotenv is installed ───────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass   # dotenv is optional


def check_python_version() -> None:
    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10+ is required.")
        sys.exit(1)


def check_db_connection() -> bool:
    """Verify DB connectivity before entering the menu loop."""
    from student_management.config.database import test_connection
    print("  Connecting to database... ", end="", flush=True)
    ok = test_connection()
    if ok:
        print("\033[32mOK\033[0m")
    else:
        print("\033[31mFAILED\033[0m")
        print()
        print("  Could not connect to the database.")
        print("  Please check:  DB_HOST / DB_USER / DB_PASSWORD / DB_NAME")
        print("  Example:  $env:DB_PASSWORD='yourpassword'  (PowerShell)")
        print("            export DB_PASSWORD='yourpassword' (bash)")
    return ok


def print_startup_banner() -> None:
    GREEN  = "\033[32m"
    CYAN   = "\033[36m"
    YELLOW = "\033[33m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

    banner = f"""
{BOLD}{CYAN}
  ╔══════════════════════════════════════════════════════════╗
  ║                                                          ║
  ║     📘  Student Record Management System  📘            ║
  ║                                                          ║
  ║         Database · Data Structures · Python             ║
  ╚══════════════════════════════════════════════════════════╝
{RESET}
{YELLOW}  Version : 1.0.0{RESET}
{GREEN}  DB      : {os.environ.get('DB_NAME')}@{os.environ.get('DB_HOST')}{RESET}
"""
    print(banner)


def main() -> None:
    check_python_version()
    print_startup_banner()

    if not check_db_connection():
        # Allow running in offline/demo mode (menu still launches)
        ans = input("\n  Launch in demo/offline mode? [y/N]: ").strip().lower()
        if ans != "y":
            print("\n  Exiting. Please fix the DB connection and try again.\n")
            sys.exit(1)
        print("\n  \033[33mWarning: Running offline — database operations will fail.\033[0m\n")

    print()
    try:
        from student_management.cli.main_menu import MainMenu
        MainMenu().run()
    except KeyboardInterrupt:
        print("\n\n  \033[36mGoodbye! 👋\033[0m\n")
        sys.exit(0)
    except Exception as exc:
        print(f"\n  \033[31mFatal error: {exc}\033[0m\n")
        raise


if __name__ == "__main__":
    main()
