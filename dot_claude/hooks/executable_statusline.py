#!/usr/bin/env python3
"""Claude Code status line — truecolor gradient bars, real quota data, and a
machine/environment chip so you can tell at a glance WHERE a session is running.

Distributed by chezmoi from TheFermiSea/dotfiles; identical on every machine.
Wire it up with, in ~/.claude/settings.json:

    "statusLine": {"type": "command",
                   "command": "python3 ~/.claude/hooks/statusline.py"}

Visual language borrowed from AKCodez's gist (24-bit gradient fill bar, emoji
status thresholds) and extended with the two things the payload actually carries
and the gist does not: the five-hour and seven-day rate limits.

Written against the REAL stdin payload from Claude Code 2.1.234, captured to
~/.claude/statusline-payload.json rather than guessed at. That capture is kept
deliberately — when the schema shifts, the fix is reading a file, not inferring.

Confirmed field paths:
    model.display_name
    workspace.current_dir · workspace.repo.name
    context_window.used_percentage        <- authoritative; no arithmetic needed
    context_window.context_window_size    <- 1_000_000 here
    rate_limits.five_hour.used_percentage
    rate_limits.seven_day.used_percentage
    cost.total_cost_usd · cost.total_lines_added · cost.total_lines_removed

DELIBERATELY UNUSED: `exceeds_200k_tokens`. It is a legacy boolean meaning "past
200k", which on a 1M window is true for most of a session and says nothing about
headroom. An earlier revision fell back to it and rendered ">200k ctx", which
read as though the limit were 200k. `used_percentage` is the real answer.

HOST CHIP (added 2026-09-11): sessions run on five machines with very different
blast radii — one drives a Class-IV laser, one serves the shared beads database.
Confusing them is expensive, and nothing in the default status line says which
you are on. The chip is FIRST and colour-coded so it reads pre-attentively.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

RESET, DIM, BOLD = "\033[0m", "\033[2m", "\033[1m"
SEP = f"{DIM}│{RESET}"

# Gradient stops: healthy -> caution -> critical.
_G, _Y, _R = (0, 200, 80), (220, 200, 0), (220, 40, 20)
_EMPTY = (58, 58, 62)

# ---------------------------------------------------------------------------
# Known hosts. Colour is the signal; the glyph is redundancy for colour-blind
# terminals and for when the line is copied into a log with escapes stripped.
# Keys match `hostname` output, short form. Add machines here rather than
# relying on the hash fallback, which is stable but meaningless.
# ---------------------------------------------------------------------------
HOSTS = {
    "brians-macbook-pro-2310": ("💻", (90, 170, 255), "mac"),
    "ai-proxy":                ("🖥",  (0, 210, 140), "ai-proxy"),
    "leabs-dev":               ("🔬", (190, 140, 255), "leabs-dev"),
    "maitai-optiplex7040":     ("⚗",  (255, 150, 60), "maitai"),
    "ceng-gh62pk3":            ("🪟", (120, 200, 255), "windows"),
}

# Hosts where a mistake is physically dangerous or hits shared state. Rendered
# with a warning marker regardless of colour support.
HAZARD_HOSTS = {
    "ceng-gh62pk3": "CLASS-IV",   # Spirit laser lives here
    "maitai-optiplex7040": "HW",  # real instruments attached
    "ai-proxy": "SHARED-DB",      # serves the beads Dolt database
}


def rgb(c) -> str:
    return f"\033[38;2;{c[0]};{c[1]};{c[2]}m"


def lerp(a, b, t: float):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def ramp(t: float):
    """Green -> yellow -> red across t in [0,1]."""
    t = max(0.0, min(1.0, t))
    return lerp(_G, _Y, t / 0.5) if t < 0.5 else lerp(_Y, _R, (t - 0.5) / 0.5)


def get(d, path, default=None):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def num(v):
    return v if isinstance(v, (int, float)) and v == v else None


def gradient_bar(pct: float, width: int) -> str:
    """Each filled block is coloured by ITS OWN position, giving a true gradient."""
    frac = max(0.0, min(1.0, pct / 100.0))
    filled = int(round(frac * width))
    # Any nonzero usage must show at least one block: a bar that reads as empty
    # while 6% is consumed is a display that says "nothing" about something.
    if frac > 0 and filled == 0:
        filled = 1
    out = []
    for i in range(width):
        if i < filled:
            out.append(f"{rgb(ramp(i / max(1, width - 1)))}█")
        else:
            out.append(f"{rgb(_EMPTY)}░")
    return "".join(out) + RESET


def pct_colour(pct: float) -> str:
    return rgb(_G) if pct < 70 else rgb(_Y) if pct < 90 else rgb(_R)


def status_glyph(pct: float) -> str:
    return "🟢" if pct < 20 else "⚡" if pct < 70 else "🔥" if pct < 90 else "🚨"


def human(n: float) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.0f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k".replace(".0k", "k")
    return f"{n:.0f}"


def git_branch(cwd: str):
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "status", "--porcelain=v2", "--branch"],
            capture_output=True, text=True, timeout=0.4,
        )
        if r.returncode != 0:
            return None
        branch, dirty = None, False
        for line in r.stdout.splitlines():
            if line.startswith("# branch.head "):
                branch = line.split(" ", 2)[2].strip()
            elif line and not line.startswith("#"):
                dirty = True
        return f"{branch}{'*' if dirty else ''}" if branch else None
    except Exception:
        return None


def short_host() -> str:
    """Prefer the real hostname; fall back through the usual env vars."""
    for fn in (socket.gethostname, lambda: os.environ.get("HOSTNAME", ""),
               lambda: os.environ.get("HOST", "")):
        try:
            h = (fn() or "").strip()
        except Exception:
            h = ""
        if h:
            return h.split(".")[0]
    return "unknown"


def hash_colour(name: str):
    """Stable colour for an unlisted host. Deterministic, mid-brightness so it
    stays readable on both light and dark terminals."""
    h = 0
    for ch in name:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    # Keep each channel in [90, 235] — avoids both invisible-dark and washed-out.
    return tuple(90 + ((h >> (8 * i)) & 0xFF) * 145 // 255 for i in range(3))


def environment_marks(cwd: str) -> list[str]:
    """Non-host context that changes what a mistake costs."""
    marks = []
    # Container: a session inside one cannot see the host's services.
    if Path("/.dockerenv").exists() or Path("/run/.containerenv").exists():
        marks.append("📦 container")
    # Worktree: edits here are on a throwaway branch, not the checkout you think.
    if "/.claude/worktrees/" in cwd or "/worktrees/" in cwd:
        marks.append("🌱 worktree")
    # Remote shell: useful when a terminal has been open long enough to forget.
    if os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_TTY"):
        marks.append("🔗 ssh")
    return marks


def host_chip(cwd: str) -> str:
    host = short_host()
    glyph, colour, label = HOSTS.get(host, ("●", hash_colour(host), host))
    chip = f"{rgb(colour)}{BOLD}▌{glyph} {label}{RESET}"

    hazard = HAZARD_HOSTS.get(host)
    if hazard:
        chip += f" {rgb((255, 90, 90))}{BOLD}[{hazard}]{RESET}"

    marks = environment_marks(cwd)
    if marks:
        chip += f" {DIM}{' '.join(marks)}{RESET}"
    return chip


def main() -> None:
    raw = sys.stdin.read()
    try:
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        d = {}

    try:
        (Path.home() / ".claude/statusline-payload.json").write_text(raw)
    except Exception:
        pass

    seg = []

    cwd = get(d, "workspace.current_dir") or get(d, "cwd") or str(Path.cwd())

    # FIRST, always: where am I running. Everything else is secondary to that.
    seg.append(host_chip(cwd))

    model = get(d, "model.display_name")
    if model:
        seg.append(f"{rgb((190, 150, 255))}🤖 {BOLD}{model}{RESET}")

    repo = get(d, "workspace.repo.name") or Path(cwd).name
    piece = f"{rgb((255, 200, 80))}{BOLD}{repo}{RESET}"
    br = git_branch(cwd)
    if br:
        colour = rgb((255, 180, 60)) if br.endswith("*") else rgb((90, 220, 190))
        piece += f" {colour}🌿 {br}{RESET}"
    seg.append(piece)

    pct = num(get(d, "context_window.used_percentage"))
    if pct is None:
        used = num(get(d, "context_window.total_input_tokens"))
        size = num(get(d, "context_window.context_window_size"))
        if used is not None and size:
            pct = 100.0 * used / size
    if pct is not None:
        size = num(get(d, "context_window.context_window_size"))
        cap = f"{DIM}/{human(size)}{RESET}" if size else ""
        seg.append(
            f"{status_glyph(pct)} {gradient_bar(pct, 20)} "
            f"{pct_colour(pct)}{BOLD}{pct:.0f}%{RESET}{cap}"
        )

    limits = []
    for path, label in (
        ("rate_limits.five_hour.used_percentage", "5h"),
        ("rate_limits.seven_day.used_percentage", "7d"),
    ):
        v = num(get(d, path))
        if v is not None:
            limits.append(
                f"{DIM}{label}{RESET} {gradient_bar(v, 5)} {pct_colour(v)}{v:.0f}%{RESET}"
            )
    if limits:
        seg.append(f" {DIM}·{RESET} ".join(limits))

    tail = []
    cost = num(get(d, "cost.total_cost_usd"))
    if cost is not None:
        tail.append(
            f"{rgb((255, 200, 80))}${cost:,.2f}{RESET}" if cost < 100
            else f"{rgb((255, 200, 80))}${cost:,.0f}{RESET}"
        )
    add = num(get(d, "cost.total_lines_added"))
    rem = num(get(d, "cost.total_lines_removed"))
    if add is not None or rem is not None:
        tail.append(
            f"{rgb((0, 200, 80))}+{human(add or 0)}{RESET} "
            f"{rgb((220, 40, 20))}-{human(rem or 0)}{RESET}"
        )
    if tail:
        seg.append(f" {DIM}·{RESET} ".join(tail))

    sys.stdout.write(f" {SEP} ".join(seg))


if __name__ == "__main__":
    main()
