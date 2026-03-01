"""
cli/base_menu.py — Abstract base class for all CLI menus
"""

from __future__ import annotations
import sys
from typing import Callable, Optional
from ..utils.helpers import print_header, print_error, print_info, get_input


class MenuItem:
    """A single selectable option in a menu."""
    def __init__(self, key: str, label: str, action: Callable):
        self.key    = key
        self.label  = label
        self.action = action

    def run(self) -> None:
        self.action()


class BaseMenu:
    """
    Generic, reusable menu engine.

    Subclasses define:
        title   — displayed at top
        items   — list of MenuItem objects
    """
    title: str = "Menu"
    items: list[MenuItem] = []

    def __init__(self):
        self._running = True

    # ── Rendering ─────────────────────────────────────────────────────── #

    def _print_banner(self) -> None:
        print("\n\033[1;35m" + "╔" + "═" * 58 + "╗")
        print(f"║  {'Student Record Management System':^54}  ║")
        print("╚" + "═" * 58 + "╝\033[0m")

    def _print_menu(self) -> None:
        print_header(self.title)
        for item in self.items:
            print(f"  \033[1;33m[{item.key}]\033[0m  {item.label}")
        print()

    # ── Main loop ─────────────────────────────────────────────────────── #

    def run(self) -> None:
        self._running = True
        while self._running:
            self._print_menu()
            choice = input("  Enter choice: ").strip().upper()
            matched = False
            for item in self.items:
                if choice == item.key.upper():
                    try:
                        item.run()
                    except KeyboardInterrupt:
                        print("\n  (cancelled)")
                    except Exception as exc:
                        print_error(f"Unexpected error: {exc}")
                    matched = True
                    break
            if not matched:
                print_error("Invalid option. Please try again.")

    def _go_back(self) -> None:
        self._running = False

    def _exit(self) -> None:
        print("\n\033[1;36m  Goodbye! 👋\033[0m\n")
        sys.exit(0)

    # ── Common input helpers ───────────────────────────────────────────── #

    @staticmethod
    def _pause() -> None:
        input("\n  Press Enter to continue...")

    @staticmethod
    def _get_student_id(prompt: str = "Student ID") -> Optional[int]:
        raw = input(f"  {prompt}: ").strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            print_error("Invalid ID — must be a number.")
            return None

    @staticmethod
    def _get_course_id(prompt: str = "Course ID") -> Optional[int]:
        raw = input(f"  {prompt}: ").strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            print_error("Invalid ID — must be a number.")
            return None
