#!/usr/bin/env python3
"""Print the ready / blocked / failed sets for a ticketmaster project."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    raw = parts[1]
    if yaml:
        data = yaml.safe_load(raw) or {}
        return data if isinstance(data, dict) else {}
    data: dict = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
        else:
            data[key] = val.strip("'\"")
    return data


def load_tickets(project_dir: Path) -> dict[str, dict]:
    tickets = {}
    for path in sorted((project_dir / "tickets").glob("T*.md")):
        meta = parse_frontmatter(path.read_text())
        tid = str(meta.get("id") or path.name.split("-", 1)[0])
        meta["_path"] = str(path)
        meta["blocked_by"] = [str(x) for x in (meta.get("blocked_by") or [])]
        meta["status"] = str(meta.get("status") or "open")
        tickets[tid] = meta
    return tickets


def cycle(tickets: dict[str, dict]) -> list[str] | None:
    visiting, seen = set(), set()

    def dfs(node: str, stack: list[str]) -> list[str] | None:
        if node in visiting:
            return stack[stack.index(node) :] + [node]
        if node in seen or node not in tickets:
            return None
        visiting.add(node)
        for dep in tickets[node]["blocked_by"]:
            hit = dfs(dep, stack + [node])
            if hit:
                return hit
        visiting.remove(node)
        seen.add(node)
        return None

    for tid in tickets:
        hit = dfs(tid, [])
        if hit:
            return hit
    return None


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: ready.py <ticket-repo> <project-slug>", file=sys.stderr)
        return 2
    repo = Path(sys.argv[1]).expanduser()
    project = repo / "projects" / sys.argv[2]
    if not project.is_dir():
        print(f"missing project: {project}", file=sys.stderr)
        return 1
    tickets = load_tickets(project)
    cyc = cycle(tickets)
    if cyc:
        print("CYCLE: " + " -> ".join(cyc))
        return 1

    done = {i for i, t in tickets.items() if t["status"] == "done"}
    failed = [i for i, t in tickets.items() if t["status"] == "failed"]
    ready, blocked = [], []
    for tid, t in tickets.items():
        if t["status"] in ("done", "failed", "in-progress"):
            continue
        unmet = [d for d in t["blocked_by"] if d not in done]
        if unmet:
            blocked.append(f"{tid} <- {', '.join(unmet)}")
        else:
            ready.append(tid)

    print("READY: " + (", ".join(ready) if ready else "(none)"))
    print("BLOCKED: " + ("; ".join(blocked) if blocked else "(none)"))
    print("FAILED: " + (", ".join(failed) if failed else "(none)"))
    running = [i for i, t in tickets.items() if t["status"] == "in-progress"]
    print("IN_PROGRESS: " + (", ".join(running) if running else "(none)"))
    if not ready and (blocked or failed):
        print("STATE: stuck")
    elif not ready and not blocked and not failed:
        print("STATE: done")
    else:
        print("STATE: runnable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
