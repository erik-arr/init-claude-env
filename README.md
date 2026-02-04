# Meta-Agent Orchestration Hub v2.0

A **persistent state registry and coordination layer** for Claude Code agents. Provides session continuity, decision tracking, and environment context for both automated agents and human operators.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION HUB (~/.claude/)                 │
├─────────────────────────────────────────────────────────────────┤
│  STATE REGISTRY   │  logs/           → JSONL event stream      │
│                   │  decisions       → Queryable audit trail   │
│                   │  correlations    → Cross-session tracking  │
├───────────────────┼─────────────────────────────────────────────┤
│  KNOWLEDGE BASE   │  docs/           → Operational standards   │
│                   │  skills/         → Reusable capabilities   │
│                   │  templates/      → Project scaffolding     │
├───────────────────┼─────────────────────────────────────────────┤
│  CONFIGURATION    │  CLAUDE.md       → Runtime constraints     │
│                   │  manifest.md     → Project context         │
│                   │  .version        → Environment metadata    │
└───────────────────┴─────────────────────────────────────────────┘
```

**For Agents:** Initialize from this registry on session start.
**For Operators:** Query logs and decisions for audit and review.

## Features

- **Cross-Platform Python Installer** - Works on macOS, Linux, and Windows
- **Persistent State Registry** - Session continuity across agent invocations
- **Extended Thinking Integration** - Thinking triggers aligned with `budget_tokens`
- **Hooks-Aware Logging** - PreToolUse/PostToolUse event tracking
- **Audit Trail** - Query decisions, escalations, handoffs
- **Log Retention Management** - Automatic cleanup to prevent storage bloat
- **SKILL.md Format** - Skills follow Claude Agent SDK patterns

## Quick Start

```bash
# Install (Python 3.9+)
python install.py clean

# Or clone and run
git clone https://github.com/erik-arr/init-claude-env.git
cd init-claude-env
python install.py clean
```

## Directory Structure

```
~/.claude/                           # ORCHESTRATION HUB ROOT
├── README.md                        # Architecture overview
├── CLAUDE.md                        # Runtime constraints (auto-loaded)
│
├── logs/                            # STATE REGISTRY
│   └── {date}/
│       └── {session-id}.jsonl       # Decision history, events
│
├── docs/                            # KNOWLEDGE BASE
│   ├── dev-philosophy.md            # Workflow principles
│   ├── pr-standards.md              # Review standards
│   ├── testing.md                   # Test philosophy
│   ├── error-handling.md            # Error principles
│   ├── message-protocol.md          # Inter-agent communication
│   ├── log-format.md                # Logging with hooks
│   ├── thinking-triggers.md         # budget_tokens alignment
│   ├── context-management.md        # Compaction strategies
│   └── agent-virtualization.md      # Claude Code mapping
│
├── skills/                          # CAPABILITIES
│   └── example/
│       └── SKILL.md
│
├── templates/                       # SCAFFOLDING
│   ├── project-manifest.md
│   └── project-logging.md
│
├── lib/
│   └── logger.py                    # Python logging with hooks
│
└── bin/
    ├── init-project                 # Bootstrap projects
    ├── query-logs                   # Query state registry
    └── cleanup-logs                 # Manage log retention
```

## Commands

```bash
python install.py clean      # Fresh install with backup
python install.py update     # Update, preserve logs
python install.py status     # Check installation
python install.py uninstall  # Remove with backup
```

## State Registry

### Event Types

| Event | Logged Fields | Use Case |
|-------|--------------|----------|
| `decision.made` | rationale, alternatives, thinking_budget | Audit trail |
| `task.started/completed` | description, duration | Progress tracking |
| `handoff.initiated` | critical_decisions, open_questions | Context transfer |
| `escalation.raised` | severity, context | Issue tracking |
| `hook.pre_tool/post_tool` | tool_name, duration_ms | Performance |
| `context.compacted` | tokens_saved, preserved_decisions | State management |

### Querying the Registry

```bash
# Recent decisions
~/.claude/bin/query-logs 'select(.evt=="decision.made")'

# Open escalations
~/.claude/bin/query-logs 'select(.evt=="escalation.raised")'

# Session trace
~/.claude/bin/query-logs 'select(.cid | startswith("corr_sess_abc"))'

# Tool execution history
~/.claude/bin/query-logs 'select(.evt | startswith("hook."))'
```

### State Continuity Example

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude/lib"))
from logger import get_logger

# Session 1: Agent logs decision
log = get_logger(agent_id="spec:backend:auth01")
log.decision_made("Use JWT tokens", rationale="Industry standard", thinking_budget=8192)

# Session 2: New agent queries prior decisions
previous = log.query('select(.evt=="decision.made")')
# Returns: [{"msg": "Use JWT tokens", "rationale": "Industry standard", ...}]
```

## Log Retention Management

Automatic cleanup prevents storage bloat:

```bash
# Check storage usage
~/.claude/bin/cleanup-logs --status

# Preview cleanup
~/.claude/bin/cleanup-logs --dry-run

# Custom retention (14 days)
~/.claude/bin/cleanup-logs --retention 14

# Compact old logs (keep decisions only)
~/.claude/bin/cleanup-logs --compact
```

**Defaults:**
- Retention: 7 days
- Max size: 50MB
- Max files: 100
- Compact after: 3 days

## Extended Thinking Integration

| Trigger | budget_tokens | Use Case | Logging Impact |
|---------|---------------|----------|----------------|
| `think` | 1,024-2,048 | Quick decisions | Light |
| `think hard` | 4,096-8,192 | Trade-offs | Log alternatives |
| `think harder` | 16,384-32,768 | Architecture | Full rationale |
| `ultrathink` | 65,536+ | Security-critical | Exhaustive |

## Agent Taxonomy

| Type | ID Format | Registry Role |
|------|-----------|---------------|
| Orchestrator | `orch:{session}` | Coordinates, writes state |
| Specialist | `spec:{domain}:{id}` | Executes, logs decisions |
| Verifier | `verif:{id}` | Reviews, validates |
| User | `user:{id}` | Human operator |

## Context Management

### Progressive Disclosure
```
Level 1: README.md (always loaded)
Level 2: Relevant docs (on trigger)
Level 3: Full skills (on demand)
```

### Compaction Rules
- Sub-agents return 1,000-2,000 token summaries
- Critical decisions **always preserved** in registry
- Tool outputs logged then discarded from context

## SKILL.md Format

```yaml
---
name: code-review
description: Adversarial code review with security focus
user-invocable: true
context: fork          # Isolated execution context
---

# Instructions for Claude when skill is activated
```

## Requirements

- Python 3.9+
- `jq` for log queries (optional but recommended)

## Migration from v1.x

```bash
python install.py update  # Preserves logs
```

## Version

Current: **v2.0.0**

## License

MIT
