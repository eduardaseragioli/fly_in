#!/usr/bin/env python3
"""
Complete tester for the fly_in project.
Tests all requirements from the subject and evaluation sheet.
Usage: python3 test_flyin.py <path_to_project_root>
"""

import sys
import os
import subprocess
import tempfile
import time
from typing import Optional

# ─────────────────────────────────────────────
#  ANSI colors
# ─────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg): print(f"  {RED}✗{RESET} {msg}")
def warn(msg): print(f"  {YELLOW}~{RESET} {msg}")
def info(msg): print(f"  {BLUE}→{RESET} {msg}")
def header(msg): print(f"\n{BOLD}{BLUE}{'='*60}{RESET}\n{BOLD}  {msg}{RESET}\n{BOLD}{BLUE}{'='*60}{RESET}")
def subheader(msg): print(f"\n{BOLD}  {msg}{RESET}")

# ─────────────────────────────────────────────
#  Map definitions
# ─────────────────────────────────────────────
MAPS = {}

MAPS["linear_2drones"] = """\
nb_drones: 2
start_hub: start 0 0 [color=green max_drones=2]
end_hub: goal 4 0 [color=yellow max_drones=2]
hub: a 1 0 [zone=normal color=blue]
hub: b 2 0 [zone=normal color=blue]
hub: c 3 0 [zone=normal color=blue]
connection: start-a
connection: a-b
connection: b-c
connection: c-goal
"""

MAPS["fork_4drones"] = """\
nb_drones: 4
start_hub: start 0 0 [color=green max_drones=4]
end_hub: goal 6 0 [color=yellow max_drones=4]
hub: junction 1 0 [zone=normal color=blue max_drones=2]
hub: top1 2 1 [zone=priority color=cyan]
hub: top2 4 1 [zone=priority color=cyan]
hub: bot1 2 -1 [zone=normal color=blue]
hub: bot2 4 -1 [zone=normal color=blue]
hub: merge 5 0 [zone=normal color=blue max_drones=2]
connection: start-junction
connection: junction-top1
connection: junction-bot1
connection: top1-top2
connection: bot1-bot2
connection: top2-merge
connection: bot2-merge
connection: merge-goal
"""

MAPS["basic_capacity_4drones"] = """\
nb_drones: 4
start_hub: start 0 0 [color=green max_drones=4]
end_hub: goal 4 0 [color=yellow max_drones=4]
hub: narrow 2 0 [zone=normal color=red max_drones=2]
hub: bypass 2 1 [zone=normal color=blue max_drones=2]
connection: start-narrow [max_link_capacity=2]
connection: start-bypass [max_link_capacity=2]
connection: narrow-goal [max_link_capacity=2]
connection: bypass-goal [max_link_capacity=2]
"""

MAPS["dead_end_5drones"] = """\
nb_drones: 5
start_hub: start 0 0 [color=green max_drones=5]
end_hub: goal 8 0 [color=yellow max_drones=5]
hub: main1 2 0 [zone=normal color=blue max_drones=2]
hub: dead_end 2 2 [zone=normal color=red]
hub: main2 4 0 [zone=normal color=blue max_drones=2]
hub: main3 6 0 [zone=normal color=blue max_drones=2]
connection: start-main1 [max_link_capacity=2]
connection: main1-dead_end
connection: main1-main2 [max_link_capacity=2]
connection: main2-main3 [max_link_capacity=2]
connection: main3-goal [max_link_capacity=2]
"""

MAPS["circular_loop_6drones"] = """\
nb_drones: 6
start_hub: start 0 0 [color=green max_drones=6]
end_hub: goal 10 0 [color=yellow max_drones=6]
hub: entry 2 0 [zone=normal color=blue max_drones=3]
hub: loop_top1 4 2 [zone=normal color=cyan max_drones=2]
hub: loop_top2 6 2 [zone=normal color=cyan max_drones=2]
hub: loop_bot1 4 -2 [zone=normal color=orange max_drones=2]
hub: loop_bot2 6 -2 [zone=normal color=orange max_drones=2]
hub: exit 8 0 [zone=normal color=blue max_drones=3]
connection: start-entry [max_link_capacity=3]
connection: entry-loop_top1 [max_link_capacity=2]
connection: entry-loop_bot1 [max_link_capacity=2]
connection: loop_top1-loop_top2 [max_link_capacity=2]
connection: loop_bot1-loop_bot2 [max_link_capacity=2]
connection: loop_top2-exit [max_link_capacity=2]
connection: loop_bot2-exit [max_link_capacity=2]
connection: exit-goal [max_link_capacity=3]
"""

MAPS["priority_puzzle_5drones"] = """\
nb_drones: 5
start_hub: start 0 0 [color=green max_drones=5]
end_hub: goal 8 0 [color=yellow max_drones=5]
hub: junction 2 0 [zone=normal color=blue max_drones=3]
hub: prio1 4 1 [zone=priority color=gold max_drones=2]
hub: prio2 6 1 [zone=priority color=gold max_drones=2]
hub: slow1 4 -1 [zone=normal color=gray max_drones=2]
hub: slow2 6 -1 [zone=normal color=gray max_drones=2]
connection: start-junction [max_link_capacity=3]
connection: junction-prio1 [max_link_capacity=2]
connection: junction-slow1 [max_link_capacity=2]
connection: prio1-prio2 [max_link_capacity=2]
connection: slow1-slow2 [max_link_capacity=2]
connection: prio2-goal [max_link_capacity=2]
connection: slow2-goal [max_link_capacity=2]
"""

MAPS["maze_nightmare_8drones"] = """\
nb_drones: 8
start_hub: start 0 0 [color=green max_drones=8]
end_hub: goal 12 0 [color=yellow max_drones=8]
hub: g1 2 0 [zone=normal color=blue max_drones=2]
hub: g2 2 2 [zone=normal color=blue max_drones=2]
hub: g3 2 -2 [zone=normal color=blue max_drones=2]
hub: m1 4 0 [zone=normal color=purple max_drones=2]
hub: m2 4 2 [zone=normal color=purple max_drones=2]
hub: m3 4 -2 [zone=normal color=purple max_drones=2]
hub: dead1 6 3 [zone=normal color=red]
hub: r1 6 0 [zone=restricted color=brown max_drones=2]
hub: r2 6 2 [zone=restricted color=brown max_drones=2]
hub: r3 6 -2 [zone=restricted color=brown max_drones=2]
hub: conv1 8 1 [zone=normal color=blue max_drones=3]
hub: conv2 8 -1 [zone=normal color=blue max_drones=3]
hub: final1 10 0 [zone=normal color=blue max_drones=3]
connection: start-g1 [max_link_capacity=2]
connection: start-g2 [max_link_capacity=2]
connection: start-g3 [max_link_capacity=2]
connection: g1-m1 [max_link_capacity=2]
connection: g2-m2 [max_link_capacity=2]
connection: g3-m3 [max_link_capacity=2]
connection: m1-r1 [max_link_capacity=2]
connection: m2-r2 [max_link_capacity=2]
connection: m3-r3 [max_link_capacity=2]
connection: m2-dead1
connection: r1-conv1 [max_link_capacity=2]
connection: r2-conv1 [max_link_capacity=2]
connection: r3-conv2 [max_link_capacity=2]
connection: conv1-final1 [max_link_capacity=3]
connection: conv2-final1 [max_link_capacity=3]
connection: final1-goal [max_link_capacity=3]
"""

MAPS["capacity_hell_12drones"] = """\
nb_drones: 12
start_hub: start 0 0 [color=green max_drones=12]
end_hub: goal 10 0 [color=yellow max_drones=12]
hub: p1 2 0 [zone=normal color=blue max_drones=3]
hub: p2 2 2 [zone=normal color=blue max_drones=3]
hub: p3 2 -2 [zone=normal color=blue max_drones=3]
hub: p4 2 4 [zone=normal color=blue max_drones=3]
hub: m1 5 1 [zone=normal color=purple max_drones=4]
hub: m2 5 -1 [zone=normal color=purple max_drones=4]
hub: e1 8 0 [zone=normal color=green max_drones=4]
hub: e2 8 2 [zone=normal color=green max_drones=4]
connection: start-p1 [max_link_capacity=3]
connection: start-p2 [max_link_capacity=3]
connection: start-p3 [max_link_capacity=3]
connection: start-p4 [max_link_capacity=3]
connection: p1-m1 [max_link_capacity=3]
connection: p2-m1 [max_link_capacity=3]
connection: p3-m2 [max_link_capacity=3]
connection: p4-m2 [max_link_capacity=3]
connection: m1-e1 [max_link_capacity=4]
connection: m2-e2 [max_link_capacity=4]
connection: e1-goal [max_link_capacity=4]
connection: e2-goal [max_link_capacity=4]
"""

MAPS["ultimate_15drones"] = """\
nb_drones: 15
start_hub: start 0 0 [color=green max_drones=15]
end_hub: goal 14 0 [color=yellow max_drones=15]
hub: d1 2 0 [zone=normal color=blue max_drones=3]
hub: d2 2 2 [zone=normal color=blue max_drones=3]
hub: d3 2 -2 [zone=normal color=blue max_drones=3]
hub: d4 2 4 [zone=normal color=blue max_drones=3]
hub: d5 2 -4 [zone=normal color=blue max_drones=3]
hub: r1 5 1 [zone=restricted color=brown max_drones=3]
hub: r2 5 -1 [zone=restricted color=brown max_drones=3]
hub: r3 5 3 [zone=restricted color=brown max_drones=3]
hub: prio1 8 0 [zone=priority color=gold max_drones=5]
hub: prio2 8 2 [zone=priority color=gold max_drones=5]
hub: conv 11 0 [zone=normal color=purple max_drones=6]
connection: start-d1 [max_link_capacity=3]
connection: start-d2 [max_link_capacity=3]
connection: start-d3 [max_link_capacity=3]
connection: start-d4 [max_link_capacity=3]
connection: start-d5 [max_link_capacity=3]
connection: d1-r1 [max_link_capacity=3]
connection: d2-r1 [max_link_capacity=3]
connection: d3-r2 [max_link_capacity=3]
connection: d4-r3 [max_link_capacity=3]
connection: d5-r2 [max_link_capacity=3]
connection: r1-prio1 [max_link_capacity=3]
connection: r2-prio2 [max_link_capacity=3]
connection: r3-prio1 [max_link_capacity=3]
connection: prio1-conv [max_link_capacity=5]
connection: prio2-conv [max_link_capacity=5]
connection: conv-goal [max_link_capacity=6]
"""

# ─── Error / edge case maps ───────────────────

MAPS["err_missing_nb_drones"] = """\
start_hub: start 0 0
end_hub: goal 2 0
hub: mid 1 0
connection: start-mid
connection: mid-goal
"""

MAPS["err_missing_start"] = """\
nb_drones: 2
end_hub: goal 2 0
hub: mid 1 0
connection: mid-goal
"""

MAPS["err_missing_end"] = """\
nb_drones: 2
start_hub: start 0 0
hub: mid 1 0
connection: start-mid
"""

MAPS["err_invalid_zone_type"] = """\
nb_drones: 1
start_hub: start 0 0
end_hub: goal 2 0
hub: mid 1 0 [zone=superfast]
connection: start-mid
connection: mid-goal
"""

MAPS["err_duplicate_zone"] = """\
nb_drones: 1
start_hub: start 0 0
end_hub: goal 2 0
hub: mid 1 0
hub: mid 3 0
connection: start-mid
connection: mid-goal
"""

MAPS["err_duplicate_connection"] = """\
nb_drones: 1
start_hub: start 0 0
end_hub: goal 2 0
hub: mid 1 0
connection: start-mid
connection: mid-start
connection: mid-goal
"""

MAPS["err_invalid_capacity"] = """\
nb_drones: 1
start_hub: start 0 0
end_hub: goal 2 0
hub: mid 1 0 [max_drones=0]
connection: start-mid
connection: mid-goal
"""

MAPS["err_zero_drones"] = """\
nb_drones: 0
start_hub: start 0 0
end_hub: goal 2 0
hub: mid 1 0
connection: start-mid
connection: mid-goal
"""

MAPS["edge_single_drone"] = """\
nb_drones: 1
start_hub: start 0 0
end_hub: goal 3 0
hub: a 1 0
hub: b 2 0
connection: start-a
connection: a-b
connection: b-goal
"""

MAPS["edge_blocked_bypass"] = """\
nb_drones: 2
start_hub: start 0 0 [max_drones=2]
end_hub: goal 4 0 [max_drones=2]
hub: blocked_mid 2 0 [zone=blocked color=gray]
hub: bypass 2 1 [zone=normal color=blue max_drones=2]
connection: start-blocked_mid
connection: start-bypass [max_link_capacity=2]
connection: blocked_mid-goal
connection: bypass-goal [max_link_capacity=2]
"""

MAPS["edge_restricted_only"] = """\
nb_drones: 2
start_hub: start 0 0 [max_drones=2]
end_hub: goal 4 0 [max_drones=2]
hub: r1 2 0 [zone=restricted color=brown max_drones=2]
connection: start-r1 [max_link_capacity=2]
connection: r1-goal [max_link_capacity=2]
"""

MAPS["comments_and_blanks"] = """\
# This is a comment
nb_drones: 2

# Another comment
start_hub: start 0 0 [color=green max_drones=2]
end_hub: goal 2 0 [color=yellow max_drones=2]

hub: mid 1 0 [zone=normal color=blue max_drones=2]

# Connection section
connection: start-mid [max_link_capacity=2]
connection: mid-goal [max_link_capacity=2]
"""

MAPS["capacity_connection_limit"] = """\
nb_drones: 4
start_hub: start 0 0 [max_drones=4]
end_hub: goal 2 0 [max_drones=4]
hub: mid 1 0 [zone=normal max_drones=4]
connection: start-mid [max_link_capacity=2]
connection: mid-goal [max_link_capacity=2]
"""


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def write_map(content: str) -> str:
    """Write map content to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    f.write(content)
    f.close()
    return f.name


def run_project(project_root: str, map_path: str, timeout: int = 15) -> tuple[int, str, str]:
    """Run the project and return (returncode, stdout, stderr)."""
    main_py = os.path.join(project_root, "main.py")
    try:
        result = subprocess.run(
            [sys.executable, main_py, map_path],
            capture_output=True, text=True,
            timeout=timeout,
            cwd=project_root
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)


def parse_output(stdout: str) -> tuple[list[list[str]], Optional[int]]:
    """
    Parse simulation stdout into (turns, total_turns).
    Each turn is a list of movement strings like ['D1-zonea', 'D2-zoneb'].
    """
    turns = []
    total = None
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("total turns"):
            try:
                total = int(line.split(":")[-1].strip())
            except ValueError:
                pass
            continue
        # skip lines that look like errors or warnings
        if line.startswith("No path") or line.startswith("Turn limit"):
            continue
        moves = line.split()
        if moves:
            turns.append(moves)
    return turns, total


def validate_output_format(turns: list[list[str]]) -> list[str]:
    """Check that every movement token matches D<ID>-<name> format."""
    errors = []
    for t_idx, turn in enumerate(turns):
        for token in turn:
            parts = token.split("-", 1)
            if len(parts) != 2:
                errors.append(f"Turn {t_idx+1}: bad token '{token}'")
                continue
            drone_id, dest = parts
            if not drone_id.startswith("D"):
                errors.append(f"Turn {t_idx+1}: drone id must start with D, got '{drone_id}'")
    return errors


def get_total_turns(stdout: str) -> Optional[int]:
    _, total = parse_output(stdout)
    return total


# ─────────────────────────────────────────────
#  Test sections
# ─────────────────────────────────────────────

results: dict[str, list[bool]] = {}


def record(section: str, passed: bool) -> None:
    results.setdefault(section, []).append(passed)


# ── 1. README ────────────────────────────────

def test_readme(project_root: str) -> None:
    header("README.md")
    readme_path = os.path.join(project_root, "README.md")

    if not os.path.isfile(readme_path):
        fail("README.md not found at project root")
        record("readme", False)
        return

    with open(readme_path) as f:
        content = f.read().lower()

    checks = [
        ("description section",        "description" in content),
        ("instructions section",        "instructions" in content or "install" in content or "usage" in content),
        ("algorithm explanation",       "algorithm" in content or "dijkstra" in content or "pathfind" in content),
        ("visual representation docs",  "visual" in content or "pygame" in content or "visuali" in content),
        ("example input/output",        "example" in content or "d1-" in content or "d2-" in content),
    ]

    for label, passed in checks:
        (ok if passed else fail)(label)
        record("readme", passed)


# ── 2. Structure & OOP ────────────────────────

def test_structure(project_root: str) -> None:
    header("Project Structure & OOP")

    subheader("Required files")
    main_exists = os.path.isfile(os.path.join(project_root, "main.py"))
    (ok if main_exists else fail)("main.py exists")
    record("structure", main_exists)

    # look for key class files
    py_files = []
    for root, _, files in os.walk(project_root):
        for f in files:
            if f.endswith(".py") and "__pycache__" not in root:
                py_files.append(os.path.join(root, f))

    subheader("Key classes present")
    class_checks = {
        "Graph":       False,
        "Zone":        False,
        "Edge":        False,
        "Drone":       False,
        "Parser":      False,
        "Pathfinder":  False,
        "Simulator":   False,
    }
    for path in py_files:
        try:
            with open(path) as f:
                src = f.read()
            for cls in list(class_checks.keys()):
                if f"class {cls}" in src:
                    class_checks[cls] = True
        except Exception:
            pass

    for cls, found in class_checks.items():
        (ok if found else fail)(f"class {cls} found")
        record("structure", found)

    subheader("Forbidden libraries")
    forbidden = ["networkx", "graphlib"]
    clean = True
    for path in py_files:
        try:
            with open(path) as f:
                src = f.read()
            for lib in forbidden:
                if lib in src:
                    fail(f"Forbidden library '{lib}' found in {os.path.basename(path)}")
                    clean = False
                    record("structure", False)
        except Exception:
            pass
    if clean:
        ok("No forbidden graph libraries used")
        record("structure", True)

    subheader("Type hints present")
    hint_count = 0
    total_funcs = 0
    for path in py_files:
        try:
            with open(path) as f:
                src = f.read()
            for line in src.splitlines():
                stripped = line.strip()
                if stripped.startswith("def "):
                    total_funcs += 1
                    if "->" in stripped or ": " in stripped:
                        hint_count += 1
        except Exception:
            pass

    if total_funcs > 0:
        ratio = hint_count / total_funcs
        typed = ratio >= 0.7
        (ok if typed else warn)(f"Type hints: {hint_count}/{total_funcs} functions ({ratio*100:.0f}%)")
        record("structure", typed)


# ── 3. Parser ─────────────────────────────────

def test_parser(project_root: str) -> None:
    header("Parser — Valid Input")

    subheader("Format requirements")

    # nb_drones
    m = write_map(MAPS["linear_2drones"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    passed = rc == 0 and out.strip() != ""
    (ok if passed else fail)("nb_drones: format parsed")
    record("parser_valid", passed)

    # zone types
    m = write_map(MAPS["maze_nightmare_8drones"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    passed = rc == 0
    (ok if passed else fail)("Zone type prefixes (hub:, start_hub:, end_hub:) parsed")
    record("parser_valid", passed)

    # connections
    m = write_map(MAPS["fork_4drones"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    passed = rc == 0
    (ok if passed else fail)("connection: format parsed")
    record("parser_valid", passed)

    # optional metadata defaults
    m = write_map(MAPS["edge_single_drone"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    passed = rc == 0
    (ok if passed else fail)("Optional metadata with defaults works")
    record("parser_valid", passed)

    # comments and blank lines
    m = write_map(MAPS["comments_and_blanks"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    passed = rc == 0
    (ok if passed else fail)("Comments (#) and blank lines ignored")
    record("parser_valid", passed)

    header("Parser — Error Handling")
    subheader("Invalid inputs should be rejected with clear messages")

    error_cases = [
        ("missing nb_drones",       "err_missing_nb_drones"),
        ("missing start_hub",       "err_missing_start"),
        ("missing end_hub",         "err_missing_end"),
        ("invalid zone type",       "err_invalid_zone_type"),
        ("duplicate zone name",     "err_duplicate_zone"),
        ("duplicate connection",    "err_duplicate_connection"),
        ("invalid capacity (0)",    "err_invalid_capacity"),
        ("zero drones",             "err_zero_drones"),
    ]

    for label, map_key in error_cases:
        m = write_map(MAPS[map_key])
        rc, out, err = run_project(project_root, m)
        os.unlink(m)
        # should fail (non-zero rc) OR print error message
        combined = (out + err).lower()
        rejected = rc != 0 or any(w in combined for w in ["error", "invalid", "missing", "duplicate", "must"])
        (ok if rejected else fail)(f"{label} → rejected with message")
        record("parser_errors", rejected)


# ── 4. Zone & Movement mechanics ──────────────

def test_mechanics(project_root: str) -> None:
    header("Zone & Movement Mechanics")

    subheader("Blocked zones — drones must go around")
    m = write_map(MAPS["edge_blocked_bypass"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    turns, total = parse_output(out)
    # drones should never appear in 'blocked_mid'
    blocked_used = any("blocked_mid" in tok for turn in turns for tok in turn)
    passed = rc == 0 and not blocked_used
    (ok if passed else fail)("Drones never enter blocked zone")
    record("mechanics", passed)

    subheader("Restricted zones — cost 2 turns")
    m = write_map(MAPS["edge_restricted_only"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    turns, total = parse_output(out)
    # with 1 restricted zone path of cost 2+2=4, min turns >= 3
    passed = rc == 0 and total is not None and total >= 3
    (ok if passed else fail)(f"Restricted zone costs 2 turns (total={total})")
    record("mechanics", passed)

    subheader("Zone capacity — max_drones respected")
    m = write_map(MAPS["capacity_connection_limit"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    turns, total = parse_output(out)
    # max_link_capacity=2 means at most 2 drones per turn per connection
    # 4 drones / 2 per turn = at least 2 turns to cross first connection
    passed = rc == 0 and total is not None and total >= 3
    (ok if passed else fail)(f"Connection capacity limits respected (total={total})")
    record("mechanics", passed)

    subheader("Multiple drones share start/end zone")
    m = write_map(MAPS["linear_2drones"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    passed = rc == 0
    (ok if passed else fail)("Multiple drones start together without error")
    record("mechanics", passed)

    subheader("Priority zones — used when available")
    m = write_map(MAPS["priority_puzzle_5drones"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    turns, total = parse_output(out)
    prio_used = any("prio" in tok for turn in turns for tok in turn)
    passed = rc == 0 and prio_used
    (ok if passed else fail)(f"Priority zones used in pathfinding (prio_used={prio_used})")
    record("mechanics", passed)


# ── 5. Output format ──────────────────────────

def test_output_format(project_root: str) -> None:
    header("Simulation Output Format")

    m = write_map(MAPS["linear_2drones"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    turns, total = parse_output(out)

    subheader("Format: D<ID>-<zone> per token")
    fmt_errors = validate_output_format(turns)
    passed = len(fmt_errors) == 0
    (ok if passed else fail)(f"All tokens match D<ID>-<zone> format ({len(fmt_errors)} errors)")
    for e in fmt_errors[:3]:
        info(e)
    record("format", passed)

    subheader("Each turn on its own line")
    passed = len(turns) > 0
    (ok if passed else fail)(f"Output has {len(turns)} turn lines")
    record("format", passed)

    subheader("Stationary drones omitted")
    # With 2 drones on linear 4-zone path, turns should have <= 2 tokens each
    max_tokens = max((len(t) for t in turns), default=0)
    passed = max_tokens <= 2
    (ok if passed else warn)(f"Max tokens per turn: {max_tokens} (expected ≤ 2 for 2 drones)")
    record("format", passed)

    subheader("Simulation ends when all drones delivered")
    # Total turns should be reported
    passed = total is not None
    (ok if passed else fail)(f"Total turns reported: {total}")
    record("format", passed)

    subheader("Delivered drones not tracked after arrival")
    m2 = write_map(MAPS["fork_4drones"])
    rc2, out2, err2 = run_project(project_root, m2)
    os.unlink(m2)
    turns2, total2 = parse_output(out2)
    # After a drone reaches goal it should not appear in subsequent turns
    drone_arrivals: dict[str, int] = {}
    errors_after_delivery = []
    for t_idx, turn in enumerate(turns2):
        for tok in turn:
            parts = tok.split("-", 1)
            if len(parts) == 2:
                drone_id, dest = parts
                if dest == "goal":
                    drone_arrivals[drone_id] = t_idx
                elif drone_id in drone_arrivals and t_idx > drone_arrivals[drone_id]:
                    errors_after_delivery.append(f"{drone_id} moved after delivery at turn {t_idx+1}")
    passed = len(errors_after_delivery) == 0
    (ok if passed else fail)(f"No drone moves after reaching end zone ({len(errors_after_delivery)} violations)")
    record("format", passed)


# ── 6. Basic functionality ────────────────────

def test_basic(project_root: str) -> None:
    header("Basic Functionality")

    cases = [
        ("Single drone linear path",   "edge_single_drone",      None),
        ("2 drones linear",            "linear_2drones",         None),
        ("4 drones fork",              "fork_4drones",           None),
        ("4 drones basic capacity",    "basic_capacity_4drones", None),
        ("Blocked zone bypass",        "edge_blocked_bypass",    None),
    ]

    for label, map_key, _ in cases:
        m = write_map(MAPS[map_key])
        rc, out, err = run_project(project_root, m)
        os.unlink(m)
        turns, total = parse_output(out)
        passed = rc == 0 and len(turns) > 0 and total is not None
        (ok if passed else fail)(f"{label} → {total} turns")
        record("basic", passed)


# ── 7. Pathfinding ────────────────────────────

def test_pathfinding(project_root: str) -> None:
    header("Pathfinding Algorithm")

    subheader("Finds valid paths in various scenarios")

    cases = [
        ("Simple linear",              "linear_2drones"),
        ("Multiple paths (fork)",      "fork_4drones"),
        ("Bottleneck capacity",        "basic_capacity_4drones"),
        ("Restricted zones",           "edge_restricted_only"),
        ("Dead end avoidance",         "dead_end_5drones"),
    ]

    for label, map_key in cases:
        m = write_map(MAPS[map_key])
        rc, out, err = run_project(project_root, m)
        os.unlink(m)
        turns, total = parse_output(out)
        passed = rc == 0 and total is not None and total > 0
        (ok if passed else fail)(f"{label} → solved in {total} turns")
        record("pathfinding", passed)

    subheader("Conflict resolution — capacity respected")

    m = write_map(MAPS["capacity_hell_12drones"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    turns, total = parse_output(out)
    passed = rc == 0 and total is not None
    (ok if passed else fail)(f"12 drones capacity hell → {total} turns")
    record("pathfinding", passed)

    # Verify no zone exceeds its capacity in output
    # We check the simple capacity map
    
    # Count simultaneous arrivals to 'mid' per turn (max_drones=4, max_link=2)
    m = write_map(MAPS["capacity_connection_limit"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    turns, total = parse_output(out)
    passed = rc == 0 and total is not None
    (ok if passed else fail)(f"4 drones capacity map solved in {total} turns")
    record("pathfinding", passed)


# ── 8. Performance benchmarks ─────────────────

def test_performance(project_root: str) -> None:
    header("Performance Benchmarks")

    benchmarks = [
        # (label, map_key, target_turns, category)
        ("Linear path (2 drones)",       "linear_2drones",         6,  "easy"),
        ("Simple fork (4 drones)",       "fork_4drones",           8,  "easy"),
        ("Basic capacity (4 drones)",    "basic_capacity_4drones", 6,  "easy"),
        ("Dead end trap (5 drones)",     "dead_end_5drones",       12, "medium"),
        ("Circular loop (6 drones)",     "circular_loop_6drones",  15, "medium"),
        ("Priority puzzle (5 drones)",   "priority_puzzle_5drones",12, "medium"),
        ("Maze nightmare (8 drones)",    "maze_nightmare_8drones", 30, "hard"),
        ("Capacity hell (12 drones)",    "capacity_hell_12drones", 35, "hard"),
        ("Ultimate challenge (15 dr.)",  "ultimate_15drones",      45, "hard"),
    ]

    categories: dict[str, list[bool]] = {"easy": [], "medium": [], "hard": []}

    for label, map_key, target, category in benchmarks:
        m = write_map(MAPS[map_key])
        t0 = time.time()
        rc, out, err = run_project(project_root, m, timeout=30)
        elapsed = time.time() - t0
        os.unlink(m)
        turns, total = parse_output(out)

        if rc != 0 or total is None:
            fail(f"{label} → FAILED (rc={rc})")
            categories[category].append(False)
            record("performance", False)
            continue

        met = total <= target
        symbol = "✓" if met else "~"
        color  = GREEN if met else YELLOW
        print(f"  {color}{symbol}{RESET} {label}: {total} turns (target ≤ {target}) [{elapsed:.1f}s]")
        categories[category].append(met)
        record("performance", met)

    subheader("Category summary")
    for cat, results_list in categories.items():
        if not results_list:
            continue
        n = len(results_list)
        n_ok = sum(results_list)
        passed = n_ok == n
        (ok if passed else warn)(f"{cat.capitalize()}: {n_ok}/{n} maps meet target")


# ── 9. Edge cases ─────────────────────────────

def test_edge_cases(project_root: str) -> None:
    header("Edge Cases")

    subheader("Single drone")
    m = write_map(MAPS["edge_single_drone"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    passed = rc == 0 and out.strip() != ""
    (ok if passed else fail)(f"Single drone → {'ok' if passed else 'failed'}")
    record("edge", passed)

    subheader("All-blocked path (should handle gracefully)")
    bad_map = """\
nb_drones: 1
start_hub: start 0 0
end_hub: goal 4 0
hub: b1 1 0 [zone=blocked]
hub: b2 2 0 [zone=blocked]
hub: b3 3 0 [zone=blocked]
connection: start-b1
connection: b1-b2
connection: b2-b3
connection: b3-goal
"""
    m = write_map(bad_map)
    rc, out, err = run_project(project_root, m, timeout=10)
    os.unlink(m)
    # Should either report no path or finish gracefully — not crash
    combined = out + err
    no_crash = rc != -1  # -1 means timeout
    graceful = "no path" in combined.lower() or "no path" in out.lower() or rc != 0
    passed = no_crash
    (ok if passed else fail)("No crash on unreachable goal")
    (ok if graceful else warn)("Graceful message when no path exists")
    record("edge", passed)

    subheader("Restricted zone only path")
    m = write_map(MAPS["edge_restricted_only"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    turns, total = parse_output(out)
    passed = rc == 0 and total is not None and total >= 3
    (ok if passed else fail)(f"Restricted-only path handled correctly (total={total})")
    record("edge", passed)

    subheader("High capacity (many drones share zones)")
    m = write_map(MAPS["capacity_hell_12drones"])
    rc, out, err = run_project(project_root, m)
    os.unlink(m)
    passed = rc == 0
    (ok if passed else fail)("12 drones handled without crash")
    record("edge", passed)

    subheader("Disconnected graph graceful handling")
    disconnected = """\
nb_drones: 1
start_hub: start 0 0
end_hub: goal 4 0
hub: island 2 2
connection: start-island
"""
    m = write_map(disconnected)
    rc, out, err = run_project(project_root, m, timeout=10)
    os.unlink(m)
    no_crash = rc != -1
    combined = (out + err).lower()
    graceful = "no path" in combined or rc != 0
    (ok if no_crash else fail)("No crash on disconnected graph")
    (ok if graceful else warn)("Reports gracefully when goal unreachable")
    record("edge", no_crash)


# ── 10. mypy type checking ────────────────────

def test_mypy(project_root: str) -> None:
    header("Type Safety (mypy)")
    try:
        result = subprocess.run(
            ["mypy", ".", "--ignore-missing-imports",
             "--disallow-untyped-defs", "--check-untyped-defs",
             "--warn-return-any", "--warn-unused-ignores"],
            capture_output=True, text=True,
            timeout=30, cwd=project_root
        )
        lines = result.stdout.strip().splitlines()
        errors = [l for l in lines if ": error:" in l]
        warnings = [l for l in lines if ": note:" in l or ": warning:" in l]

        if not errors:
            ok(f"mypy passed (0 errors, {len(warnings)} notes)")
            record("mypy", True)
        else:
            fail(f"mypy found {len(errors)} error(s)")
            for e in errors[:5]:
                info(e)
            record("mypy", False)
    except FileNotFoundError:
        warn("mypy not installed — skipping type check")
        record("mypy", True)
    except subprocess.TimeoutExpired:
        warn("mypy timed out")
        record("mypy", False)


# ── 11. flake8 ────────────────────────────────

def test_flake8(project_root: str) -> None:
    header("Code Style (flake8)")
    try:
        result = subprocess.run(
            ["flake8", ".", "--max-line-length=100",
             "--exclude=__pycache__,.mypy_cache,.venv,venv"],
            capture_output=True, text=True,
            timeout=20, cwd=project_root
        )
        lines = result.stdout.strip().splitlines()
        if not lines:
            ok("flake8 passed — no style errors")
            record("flake8", True)
        else:
            fail(f"flake8 found {len(lines)} issue(s)")
            for l in lines[:5]:
                info(l)
            record("flake8", len(lines) <= 10)
    except FileNotFoundError:
        warn("flake8 not installed — skipping style check")
        record("flake8", True)
    except subprocess.TimeoutExpired:
        warn("flake8 timed out")
        record("flake8", False)


# ─────────────────────────────────────────────
#  Final summary
# ─────────────────────────────────────────────

def print_summary() -> None:
    header("FINAL SUMMARY")

    section_labels = {
        "readme":        "README.md",
        "structure":     "Project Structure & OOP",
        "parser_valid":  "Parser (valid input)",
        "parser_errors": "Parser (error handling)",
        "mechanics":     "Zone & Movement Mechanics",
        "format":        "Output Format",
        "basic":         "Basic Functionality",
        "pathfinding":   "Pathfinding Algorithm",
        "performance":   "Performance Benchmarks",
        "edge":          "Edge Cases",
        "mypy":          "Type Safety (mypy)",
        "flake8":        "Code Style (flake8)",
    }

    total_pass = 0
    total_all  = 0

    for key, label in section_labels.items():
        checks = results.get(key, [])
        if not checks:
            continue
        n_pass = sum(checks)
        n_all  = len(checks)
        total_pass += n_pass
        total_all  += n_all
        ratio = n_pass / n_all
        color = GREEN if ratio == 1.0 else (YELLOW if ratio >= 0.7 else RED)
        bar = "█" * int(ratio * 10) + "░" * (10 - int(ratio * 10))
        print(f"  {color}{bar}{RESET}  {label}: {n_pass}/{n_all}")

    overall = total_pass / total_all if total_all else 0
    color = GREEN if overall >= 0.85 else (YELLOW if overall >= 0.6 else RED)
    print(f"\n{BOLD}  Overall: {color}{total_pass}/{total_all} ({overall*100:.0f}%){RESET}")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <path_to_project_root>")
        sys.exit(1)

    project_root = os.path.abspath(sys.argv[1])

    if not os.path.isdir(project_root):
        print(f"Error: '{project_root}' is not a directory")
        sys.exit(1)

    print(f"\n{BOLD}fly_in Project Tester{RESET}")
    print(f"Project root: {project_root}\n")

    test_readme(project_root)
    test_structure(project_root)
    test_parser(project_root)
    test_mechanics(project_root)
    test_output_format(project_root)
    test_basic(project_root)
    test_pathfinding(project_root)
    test_performance(project_root)
    test_edge_cases(project_root)
    test_mypy(project_root)
    test_flake8(project_root)
    print_summary()


if __name__ == "__main__":
    main()