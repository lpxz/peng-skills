# peng-skills

Public [Agent Skills](https://cursor.com/docs/context/skills).

| Skill | Trigger | What it does |
|-------|---------|--------------|
| [ticketmaster](ticketmaster/) | `/ticketmaster`, "create a ticket", "run the loop" | Plan tickets into a ticket repo (default `peng-tickets`), schedule unblocked work, loop until stuck |

## Install

```bash
git clone https://github.com/lpxz/peng-skills.git
ln -s "$(pwd)/peng-skills/ticketmaster" ~/.cursor/skills/ticketmaster
```

Tickets themselves are **not** in this repo. They go in a ticket repo (default private `peng-tickets`).
