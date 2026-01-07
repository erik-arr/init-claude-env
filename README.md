# Claude Meta-Agent Architecture

Meta-agent orchestration infrastructure for Claude Code with auto-session tracking and JSONL logging.

## Table of Contents

- [Quick Start](#quick-start)
- [What It Installs](#what-it-installs)
- [Commands](#commands)
- [Project Initialization](#project-initialization)
- [Agent Logging (Python)](#agent-logging-python)
  - [Session Continuity](#session-continuity)
- [Log Queries](#log-queries)
- [Agent Taxonomy](#agent-taxonomy)
- [Thinking Triggers](#thinking-triggers)
- [Version](#version)
- [License](#license)

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/erik-arr/init-claude-env/main/install-claude-arch.sh | bash -s -- clean

# Or clone and run
git clone https://github.com/erik-arr/init-claude-env.git
cd init-claude-env
./install-claude-arch.sh clean
```

## What It Installs

```
~/.claude/
├── CLAUDE.md              # Global agent constraints (auto-loaded)
├── README.md              # Architecture documentation
├── docs/                  # Reference documentation
│   ├── dev-philosophy.md
│   ├── pr-standards.md
│   ├── testing.md
│   ├── error-handling.md
│   ├── message-protocol.md
│   ├── log-format.md
│   ├── thinking-triggers.md
│   └── agent-virtualization.md
├── templates/
│   ├── project-manifest.md
│   └── project-logging.md
├── lib/
│   └── logger.py          # Python logging library
├── bin/
│   ├── init-project       # Bootstrap project manifest
│   └── query-logs         # Search JSONL logs
├── commands/
│   └── agent-ops.md
└── logs/
    └── {date}/
        └── {session}.jsonl

~/CLAUDE.md -> ~/.claude/CLAUDE.md  # Symlink for Claude Code
```

## Commands

```bash
./install-claude-arch.sh clean      # Fresh install with backup
./install-claude-arch.sh update     # Update, preserve logs
./install-claude-arch.sh status     # Check installation
./install-claude-arch.sh uninstall  # Remove with backup
./install-claude-arch.sh help       # Show all options
```

## Project Initialization

```bash
~/.claude/bin/init-project /path/to/project
```

Creates `project/.claude/manifest.md` and `project/.claude/logs/`.

## Agent Logging (Python)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude/lib"))

from logger import get_logger

# Auto-generates session ID
log = get_logger(agent_id="spec:backend:auth01")
log.task_started("Implementing feature")
log.decision_made("Using JWT", rationale="Industry standard")
log.task_completed("Feature complete")
```

### Session Continuity

```python
# First agent auto-generates session
log1 = get_logger(agent_id="orch:main")
# sess_20260107_143052_a1b2c3d4

# Second agent reuses same session
log2 = get_logger(agent_id="spec:backend:api01")
# Same session ID maintained
```

## Log Queries

```bash
# All errors
~/.claude/bin/query-logs 'select(.lvl=="error")'

# Decisions only
~/.claude/bin/query-logs 'select(.evt=="decision.made")'

# By correlation ID
~/.claude/bin/query-logs 'select(.cid=="corr_sess_abc_001")'
```

## Agent Taxonomy

| Type | ID Format | Description |
|------|-----------|-------------|
| Orchestrator | `orch:{session}` | Meta-agent coordinator |
| Specialist | `spec:{domain}:{id}` | Task-focused sub-agent |
| Verifier | `verif:{id}` | Adversarial review agent |
| User | `user:{id}` | Human operator |

## Thinking Triggers

Semantic depth hints for Claude's extended reasoning:

| Trigger | When to Use |
|---------|-------------|
| `think` | Simple decisions |
| `think hard` | Trade-offs, moderate complexity |
| `think harder` | Architecture, edge cases |
| `ultrathink` | Critical decisions, security |

## Version

Current: **v1.3.1**

## License

MIT
