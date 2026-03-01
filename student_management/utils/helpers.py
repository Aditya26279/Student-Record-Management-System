"""
utils/helpers.py — Display and formatting helpers
"""

from typing import List, Any, Optional
from datetime import date, datetime


# ── Table printer (uses tabulate if available, else plain text) ──────────── #
try:
    from tabulate import tabulate as _tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def print_table(rows: List[dict], headers: Optional[List[str]] = None,
                title: str = "") -> None:
    """Pretty-print a list of dicts as a table."""
    if not rows:
        print("  (no records found)\n")
        return
    if title:
        print(f"\n  \033[1;36m{title}\033[0m")
        print("  " + "─" * 60)

    if HAS_TABULATE:
        keys = headers or list(rows[0].keys())
        table_data = [[r.get(k, "") for k in keys] for r in rows]
        print(_tabulate(table_data, headers=keys, tablefmt="rounded_outline"))
    else:
        # Minimal fallback
        keys = headers or list(rows[0].keys())
        widths = [max(len(str(k)), max(len(str(r.get(k, ""))) for r in rows))
                  for k in keys]
        sep = "  " + "  ".join("-" * w for w in widths)
        header_row = "  " + "  ".join(str(k).ljust(w) for k, w in zip(keys, widths))
        print(header_row)
        print(sep)
        for r in rows:
            print("  " + "  ".join(str(r.get(k, "")).ljust(w)
                                   for k, w in zip(keys, widths)))
    print()


def format_gpa(gpa: float) -> str:
    colour = (
        "\033[32m" if gpa >= 8.0 else       # green
        "\033[33m" if gpa >= 6.0 else       # yellow
        "\033[31m"                           # red
    )
    return f"{colour}{gpa:.2f}\033[0m"


def format_result(result: Optional[str]) -> str:
    if result == "Pass":
        return "\033[32mPass\033[0m"
    if result == "Fail":
        return "\033[31mFail\033[0m"
    return result or "—"


def format_attendance_pct(pct: float) -> str:
    colour = "\033[32m" if pct >= 75 else "\033[31m"
    return f"{colour}{pct:.1f}%\033[0m"


def print_header(title: str) -> None:
    width = 60
    print("\n" + "\033[1;35m" + "═" * width)
    print(f"  {title}")
    print("═" * width + "\033[0m")


def print_success(msg: str) -> None:
    print(f"\n  \033[1;32m✓ {msg}\033[0m\n")


def print_error(msg: str) -> None:
    print(f"\n  \033[1;31m✗ {msg}\033[0m\n")


def print_info(msg: str) -> None:
    print(f"  \033[1;34mℹ {msg}\033[0m")


def confirm(prompt: str) -> bool:
    """Ask y/n and return True for yes."""
    ans = input(f"  {prompt} [y/N]: ").strip().lower()
    return ans == "y"


def get_input(prompt: str, default: str = "") -> str:
    val = input(f"  {prompt}" + (f" [{default}]" if default else "") + ": ").strip()
    return val if val else default


def get_int_input(prompt: str, default: Optional[int] = None) -> Optional[int]:
    raw = input(f"  {prompt}" + (f" [{default}]" if default is not None else "") + ": ").strip()
    if not raw and default is not None:
        return default
    try:
        return int(raw)
    except ValueError:
        print_error("Invalid number — please try again.")
        return None


def get_float_input(prompt: str, lo: float = 0, hi: float = 100,
                    default: Optional[float] = None) -> Optional[float]:
    raw = input(f"  {prompt} ({lo}-{hi})" +
                (f" [{default}]" if default is not None else "") + ": ").strip()
    if not raw and default is not None:
        return default
    try:
        v = float(raw)
        if lo <= v <= hi:
            return v
        print_error(f"Must be between {lo} and {hi}.")
        return None
    except ValueError:
        print_error("Invalid number.")
        return None


def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def current_year() -> int:
    return datetime.now().year
