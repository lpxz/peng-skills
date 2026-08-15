---
name: ticketmaster
description: Plan and run software tickets stored in a ticket repo (default ~/peng-tickets). Walks the user through creating a project-folder plan with blocking edges, optional per-ticket validation, and a loop that executes unblocked tickets (parallel agents) until stuck. Use when the user says "ticketmaster", "create a ticket", "plan tickets", "run the loop", "unblock", or wants multi-agent ticket scheduling.
---

# /ticketmaster — plan tickets, then loop the DAG

Tickets live in a **ticket repo**, organized by **project folder**. Default ticket repo: `~/peng-tickets` (`lpxz/peng-tickets`). Switch with `repo:<path-or-github>` or by editing that repo's `config.yml`.

This skill does **not** invent work. It walks the user through a plan, writes tickets, then (when asked) runs the loop.

**Before writing any implementation code for a ticket**, follow Superpowers. Read [architecture.md](architecture.md) and the vendored skills in [vendor/superpowers/](vendor/superpowers/). Source: [obra/superpowers](https://github.com/obra/superpowers) (MIT).

## Actions

Parse `$ARGUMENTS` plus the user message:

| Action | Triggers |
|--------|----------|
| **plan** (default) | "create a ticket", "plan", no args |
| **loop** | "loop", "run the loop", "execute until stuck" |
| **status** | "status", "what's unblocked" |
| **repo** | `repo:~/other` or `repo:owner/name` |

If both plan and loop are requested, finish the plan (user must approve tickets) before looping.

## Ticket repo

Resolve in this order:

1. `repo:` argument this turn
2. `~/peng-skills/ticketmaster/config.yml` → `ticket_repo`
3. Default `~/peng-tickets`

If the path is missing, clone `git@github.com:lpxz/peng-tickets.git` to `~/peng-tickets` (private). For another GitHub repo, clone to `~/<name>` only after the user confirms.

Read `<ticket-repo>/config.yml` if present (`default_retry_limit`, `default_project`). Layout is in [ticket-format.md](ticket-format.md).

```
<ticket-repo>/
  config.yml
  projects/
    <project-slug>/
      PROJECT.md
      tickets/
        T001-<slug>.md
```

## 1. Plan (walk through what they want)

Follow vendored `brainstorming` then `writing-plans`. Ask **one question per message**. Do not write ticket files until the user approves the ticket list and edges.

Walkthrough order:

1. **Outcome** — what should be true when this project is done?
2. **Code repo** — which codebase do agents implement in? (path or GitHub). Not the same as the ticket repo.
3. **Project slug** — existing `projects/*` or a new kebab-case name.
4. **Ticket repo** — confirm default `~/peng-tickets` or switch.
5. **Decompose** — propose 3–12 tickets. Each is one independently testable deliverable (Superpowers task sizing). Show a DAG of `blocked_by` edges. Unblocked tickets have empty `blocked_by`.
6. **Validation** — for **each** ticket, ask for validation logic. Allowed answers: a shell command, a checklist, or **empty**. Empty means "done when the implementer says so + Superpowers verification-before-completion." Do not invent validation.
7. **Retry limit** — default `3` from `config.yml`, overridable per ticket.

Then write `PROJECT.md` and one file per ticket. Commit in the ticket repo (not the code repo) with a message like `plan(<project>): add T001–T00N`.

Show the ready set before stopping:

```
Ready (unblocked): T001, T003
Blocked: T002 ← T001; T004 ← T002, T003
```

## 2. Loop (execute until stuck)

**Stuck** = no ticket is `ready` (open/ready, not failed, all `blocked_by` are `done`). Remaining work is blocked or failed.

Announce: "Using ticketmaster loop on `<project>`."

```
loop:
  ready ← tickets whose blockers are all done and status ∈ {open, ready}
  if ready is empty:
    report DONE (nothing left) or STUCK (blocked/failed remain)
    stop
  pick ready tickets that do not share files / code-repo paths
  dispatch one agent per independent ticket (see vendor dispatching-parallel-agents)
  wait
  for each returned ticket:
    run its validation (or Superpowers verification if validation is empty)
    pass → status=done, retries unchanged, unblocks dependents
    fail → retries += 1
            if retries < retry_limit → status=ready (retry next wave)
            else → status=failed (does not unblock)
  repeat
```

Use `python3 scripts/ready.py <ticket-repo> <project>` to compute the ready set. Do not hand-wave the DAG.

**Scheduling rules**

- Never start a ticket whose `blocked_by` is not all `done`.
- Independent ready tickets → parallel agents in **one** turn.
- Same files / same module → sequential, one agent.
- Each agent gets a self-contained prompt: ticket path, code-repo path, vendored Superpowers paths, "do not edit other tickets."
- After each wave, update ticket frontmatter (`status`, `retries`, `updated`, `log`) and commit in the ticket repo.

**Agent must follow Superpowers while implementing**

1. `test-driven-development` — no production code without a failing test first (unless the ticket is docs/config).
2. `verification-before-completion` — no "done" without fresh command evidence.
3. `writing-plans` file/unit rules — small files, one responsibility, clear interfaces.
4. YAGNI / DRY. If the design is still fuzzy, stop and re-enter plan (brainstorming), do not code.

## 3. Validation

Stored on the ticket as `validation` (string, may be `""`).

| `validation` | Pass if |
|--------------|---------|
| empty | Implementer ran the natural proof (tests/build) and pasted evidence. Apply verification-before-completion. |
| shell line | Command exits 0. Run from the **code repo** cwd. |
| multiline script | Write to `/tmp/ticketmaster-validate-<id>.sh`, `bash` it, exit 0. |

On failure: keep the ticket `ready` or `failed` per retry rule. Append a `## Log` line with attempt number, command, and tail of output. Do not mark `done`.

Default `retry_limit: 3`. `retries` starts at `0`. A failed validation consumes one retry.

## 4. Status

Print project, ticket repo, counts by status, ready set, blocked edges, failed tickets with last log line.

## Hard rules

- Tickets go in the **ticket repo**, never inside `peng-skills` except this skill.
- Do not copy personal skills or secrets into the public `peng-skills` repo.
- Do not start the loop until the user asked to run it (or said "loop").
- Do not skip the validation question during plan.
- Cycles in `blocked_by` are a plan bug — refuse to write / refuse to loop until the user fixes the cycle.
- `failed` tickets do not unblock dependents. Report STUCK and ask what to do.

## Arguments

- `plan` / `loop` / `status`
- `repo:~/peng-tickets` or `repo:owner/name`
- `project:<slug>`
- `retry-limit:3`
- A free-text outcome → start **plan**
