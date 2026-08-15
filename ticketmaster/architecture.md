# Architecture bar (Superpowers)

Vendored originals (do not paraphrase away the iron laws):

| When | Read |
|------|------|
| Start of any ticketmaster session | [vendor/superpowers/using-superpowers/SKILL.md](vendor/superpowers/using-superpowers/SKILL.md) |
| Planning / "what should we build" | [vendor/superpowers/brainstorming/SKILL.md](vendor/superpowers/brainstorming/SKILL.md) |
| After the user approves a design | [vendor/superpowers/writing-plans/SKILL.md](vendor/superpowers/writing-plans/SKILL.md) |
| Loop, parallel ready tickets | [vendor/superpowers/dispatching-parallel-agents/SKILL.md](vendor/superpowers/dispatching-parallel-agents/SKILL.md) |
| Loop, one ticket per agent | [vendor/superpowers/subagent-driven-development/SKILL.md](vendor/superpowers/subagent-driven-development/SKILL.md) |
| Implementing a ticket | [vendor/superpowers/test-driven-development/SKILL.md](vendor/superpowers/test-driven-development/SKILL.md) |
| Before marking a ticket done | [vendor/superpowers/verification-before-completion/SKILL.md](vendor/superpowers/verification-before-completion/SKILL.md) |
| Between tickets if quality slipped | [vendor/superpowers/requesting-code-review/SKILL.md](vendor/superpowers/requesting-code-review/SKILL.md) |

Downloaded from [obra/superpowers](https://github.com/obra/superpowers), MIT. See [vendor/superpowers/LICENSE](vendor/superpowers/LICENSE).

## What "looks good" means here

- **Classify then approve** — spike / bounded / architectural. No implementation until the user says yes to the design (brainstorming).
- **Units with one job** — each file has a purpose, an interface, and explicit dependencies. Prefer small files. Split by responsibility, not by technical layer (writing-plans).
- **TDD** — no production code without a failing test first. Delete code written before tests.
- **YAGNI / DRY** — no extra knobs, no "similar to Task N" placeholders.
- **Evidence** — never claim done without a fresh command and its output.
- **Subagents stay narrow** — one ticket, exact paths, no shared-file writes in parallel.

Ticket `## Plan` sections must name exact files, interfaces consumed/produced, and the test command. Empty "implement the feature" plans are a skill failure — rewrite before looping.
