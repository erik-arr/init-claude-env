#!/usr/bin/env python3
"""
Claude Meta-Agent Architecture Installer v2.0.0

Cross-platform Python installer for meta-agent orchestration infrastructure.
Replaces bash-based installation with modern Python patterns aligned with
Claude Agent SDK, extended thinking, and MCP best practices.

Usage:
    python install.py clean      # Fresh install with backup
    python install.py update     # Update, preserve logs
    python install.py status     # Check installation
    python install.py uninstall  # Remove with backup
    python install.py help       # Show options
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

VERSION = "2.0.0"

# ANSI colors (with fallback for Windows)
if os.name == 'nt':
    os.system('')  # Enable ANSI on Windows

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
BOLD = '\033[1m'
DIM = '\033[2m'
NC = '\033[0m'


def print_success(msg: str) -> None:
    print(f"{GREEN}[OK]{NC} {msg}")


def print_warning(msg: str) -> None:
    print(f"{YELLOW}[!]{NC} {msg}")


def print_error(msg: str) -> None:
    print(f"{RED}[X]{NC} {msg}")


def print_info(msg: str) -> None:
    print(f"{BLUE}-->{NC} {msg}")


def get_home() -> Path:
    """Get home directory cross-platform."""
    return Path(os.environ.get("HOME", Path.home()))


def get_iso_date() -> str:
    """Get ISO8601 timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_backup_dir() -> Path:
    """Generate unique backup directory path."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return get_home() / f".claude-backup-{ts}"


def show_banner() -> None:
    """Display installation banner."""
    print(f"{BLUE}+--------------------------------------------------------------+{NC}")
    print(f"{BLUE}|{NC}  {BOLD}Meta-Agent Architecture Installer{NC} {DIM}v{VERSION}{NC}                    {BLUE}|{NC}")
    print(f"{BLUE}+--------------------------------------------------------------+{NC}")


# =============================================================================
# File Content Templates
# =============================================================================

CLAUDE_MD = '''# Claude Global Standards

## Bootstrap (Read on Session Start)

**First message in session or complex task --> READ THESE FILES:**

1. `~/.claude/README.md` -- Full meta-agent architecture
2. `project/.claude/manifest.md` -- Project requirements (if exists)

**Trigger-based reading:**

| Trigger | Action |
|---------|--------|
| "spawn", "subagent", "delegate" | READ ~/.claude/README.md + message-protocol.md |
| Planning multi-step work | READ ~/.claude/docs/dev-philosophy.md |
| About to open PR | READ ~/.claude/docs/pr-standards.md |
| Writing tests | READ ~/.claude/docs/testing.md |

## Extended Thinking Integration

Use thinking depth semantically aligned with `budget_tokens`:

| Trigger | Approx Budget | Use Case |
|---------|---------------|----------|
| `think` | 1,024-2,048 | Simple decisions, quick checks |
| `think hard` | 4,096-8,192 | Trade-offs, moderate complexity |
| `think harder` | 16,384-32,768 | Architecture, edge cases |
| `ultrathink` | 65,536+ | Critical decisions, security review |

## Context Management

### For Long-Running Tasks
Your context window will be automatically compacted as it approaches its limit.
Do not stop tasks early due to token budget concerns. Save progress before refresh.

### Sub-Agent Communication
- Return condensed summaries (1,000-2,000 tokens) to coordinating agent
- Track correlation IDs across agent boundaries
- Use structured state (JSON) for handoffs

## Communication
- Be extremely concise. Sacrifice grammar for brevity.
- No AI/Claude mentions in commits, docs, comments.
- Plans end with unresolved questions.

## NEVER
- `pip install` --> use `uv sync` / `uv add`
- `python script.py` --> use `uv run script.py`
- Commit messages mentioning AI assistance
- PRs over 500 lines without splitting

## ALWAYS
- Design before implementation
- Type hints with `from __future__ import annotations`
- Handle errors at appropriate abstraction level
- Log decisions with rationale
- Use parallel tool execution when possible

## Commits
```
<type>: <subject under 72 chars>

- What changed, why (technical)
```
Types: feat, fix, refactor, chore, docs, test, perf

## Agent Self-Check

**Before starting work:**
1. Do I understand the task scope? (If unclear --> ask)
2. Is this multi-file or architectural? --> Read README.md
3. Am I spawning/handing off? --> Read message-protocol.md
4. Is context approaching limits? --> Compact and checkpoint
'''

README_MD = '''# Meta-Agent Orchestration Hub v2.0

> **Orchestration Hub** — Persistent state registry and coordination layer
> for multi-agent operations. Provides session continuity, decision tracking,
> and environment context for both automated agents and human operators.

---

## Architecture Overview

This system provides **persistent state management** across agent sessions:

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

---

## Environment State (Quick Assessment)

When entering a session, immediately assess:

| Check | Location | Why |
|-------|----------|-----|
| Recent decisions | `logs/{today}/*.jsonl` | What was just decided? |
| Open questions | Last `handoff.initiated` event | What's unresolved? |
| Active project | `project/.claude/manifest.md` | Project-specific rules |
| Complexity zones | Manifest complexity table | Where to think harder |

```bash
# Quick state check
~/.claude/bin/query-logs 'select(.evt=="decision.made")' | tail -5
~/.claude/bin/query-logs 'select(.evt=="escalation.raised")'
```

---

## TL;DR for Agents

```
YOU ARE: An agent with persistent state via this Orchestration Hub
MEMORY: Your decisions are logged → queryable across sessions
STATE: Read logs to understand what happened before you
COORDINATION: Via message protocol (@~/.claude/docs/message-protocol.md)
YOUR ID: {type}:{domain}:{id} (e.g., spec:backend:auth01)
CORRELATION: Always track with corr_{session}_{seq}
CONTEXT: Compact to 1-2k tokens when handing off
THINKING: Scale budget_tokens with task complexity
ESCALATE: When blocked, uncertain, or security-critical
```

---

## Directory Structure

```
~/.claude/                           # ORCHESTRATION HUB ROOT
├── README.md                        # THIS FILE — read first
├── CLAUDE.md                        # Global constraints (auto-loaded)
│
├── logs/                            # STATE REGISTRY
│   └── {date}/
│       └── {session-id}.jsonl       # Decision history, events, state
│
├── docs/                            # KNOWLEDGE BASE
│   ├── dev-philosophy.md            # Workflow principles
│   ├── pr-standards.md              # Review standards
│   ├── testing.md                   # Test philosophy
│   ├── error-handling.md            # Error principles
│   ├── message-protocol.md          # Inter-agent communication
│   ├── log-format.md                # Logging standard with hooks
│   ├── thinking-triggers.md         # Extended thinking semantics
│   ├── context-management.md        # Context window strategies
│   └── agent-virtualization.md      # Claude Code agent mapping
│
├── skills/                          # CAPABILITIES
│   └── {skill-name}/
│       └── SKILL.md                 # Reusable agent skills
│
├── templates/                       # PATTERNS
│   ├── project-manifest.md          # Project initialization
│   └── project-logging.md           # Application logging
│
├── lib/
│   └── logger.py                    # Python logging with hooks
│
└── bin/
    ├── init-project                 # Bootstrap project manifest
    └── query-logs                   # Query JSONL memory
```

---

## Agent Taxonomy

| Agent Type | Identifier | Registry Role |
|------------|------------|----------------------|
| user | user:{id} | Human operator, reviews decisions |
| orchestrator | orch:{session} | Coordinates, writes to memory |
| specialist | spec:{domain}:{id} | Executes, logs decisions |
| verifier | verif:{id} | Reviews, validates memory |
| external | ext:{provider}:{model} | External integration |

---

## Long-Term Memory System

### What Gets Remembered

| Event Type | Persisted | Queryable By |
|------------|-----------|--------------|
| `decision.made` | Yes | rationale, alternatives, thinking_budget |
| `task.started` | Yes | description, agent_id |
| `task.completed` | Yes | description, duration |
| `handoff.initiated` | Yes | critical_decisions, open_questions |
| `escalation.raised` | Yes | severity, context |
| `context.compacted` | Yes | tokens_saved, preserved_decisions |
| `hook.pre_tool` | Yes | tool_name, tool_input |
| `hook.post_tool` | Yes | tool_name, duration_ms |

### Querying Memory

```bash
# What decisions were made today?
~/.claude/bin/query-logs 'select(.evt=="decision.made")'

# What's still unresolved?
~/.claude/bin/query-logs 'select(.evt=="escalation.raised")'

# Trace a specific task
~/.claude/bin/query-logs 'select(.cid | startswith("corr_sess_abc"))'

# What tools were used?
~/.claude/bin/query-logs 'select(.evt | startswith("hook."))'
```

### Memory Continuity Across Sessions

```python
# Session 1: Agent makes decision
log = get_logger(agent_id="spec:backend:auth01")
log.decision_made("Use JWT tokens", rationale="Industry standard")

# Session 2: New agent queries what was decided
previous = log.query('select(.evt=="decision.made")')
# Returns: [{"msg": "Use JWT tokens", "rationale": "Industry standard", ...}]
```

---

## Context Management Strategy

### Progressive Disclosure (Load on Demand)
1. **Level 1**: Agent ID + this README (always loaded)
2. **Level 2**: Relevant docs (loaded when triggered)
3. **Level 3**: Full skill files (on-demand)

### Compaction Rules
- Sub-agents return 1,000-2,000 token summaries
- Orchestrator synthesizes, never forwards raw context
- **Critical decisions always preserved** in memory
- Tool outputs discarded after logging

---

## Extended Thinking Triggers

| Trigger | Budget | When | Memory Impact |
|---------|--------|------|---------------|
| `think` | ~2k | Quick decisions | Light logging |
| `think hard` | ~8k | Trade-offs | Log alternatives |
| `think harder` | ~32k | Architecture | Full rationale |
| `ultrathink` | 64k+ | Security-critical | Exhaustive record |

---

## Human Review Guide

### Daily Review
```bash
# What did agents decide today?
~/.claude/bin/query-logs 'select(.evt=="decision.made")' --global

# Any escalations needing attention?
~/.claude/bin/query-logs 'select(.lvl=="error" or .lvl=="warn")'
```

### Project Review
```bash
# Project-specific decisions
~/.claude/bin/query-logs '.' --project

# Complexity zone activity
~/.claude/bin/query-logs 'select(.aid | contains("auth"))'
```

### Audit Trail
```bash
# Full session trace
~/.claude/bin/query-logs '.' sess_20260204_123456
```

---

*This orchestration hub maintains state across sessions. Logged decisions*
*form the audit trail for all agent operations. Query this registry to*
*understand operational context before initiating new workflows.*
'''

DEV_PHILOSOPHY_MD = '''# Development Philosophy

## Core Principle
Code generation is cheap; review is expensive.

## Workflow: Explore → Plan → Code → Commit

### 1. Explore
- Read relevant files before planning
- Use subagents for complex research
- **Progressive disclosure**: Load context on-demand

### 2. Plan
- TodoWrite breakdown forces design thinking
- Use thinking triggers: `think` → `ultrathink`
- Scale `budget_tokens` with complexity

### 3. Code
- Target reviewable chunks (<500 lines)
- Verify as you implement
- **Parallel tool execution** when independent

### 4. Commit
- Each commit tells coherent story
- Never mention AI in commits

## Context Efficiency

### Sub-Agent Pattern
```
Main Agent ─────────────────────────────────┐
    │                                        │
    ├── spawn spec:research:01 ──────────┐  │
    │       [full context exploration]   │  │
    │       [return: 1-2k summary]  ─────┘  │
    │                                        │
    ├── spawn spec:implement:02 ─────────┐  │
    │       [focused implementation]     │  │
    │       [return: 1-2k summary]  ─────┘  │
    │                                        │
    └── synthesize ──────────────────────────┘
```

### Context Compaction Triggers
- Approaching 80% context window
- Before handoff to another agent
- After completing major subtask
'''

PR_STANDARDS_MD = '''# PR Standards

## Size Limits
- Target: <500 lines
- Hard limit: >1000 lines degrades review quality

## PR Description Template
```markdown
## Summary
[What changed + architectural reasoning]

## Changes
- Technical bullets, breaking changes noted

## Test Plan
- Verification steps, edge cases

## Deployment
- Migration steps, rollback procedure
```

## Multi-Agent Review
When verifier agents review PRs:
1. Focus on correctness, not style
2. Check for unhandled edge cases
3. Verify test coverage of critical paths
4. Flag security implications
'''

TESTING_MD = '''# Testing Standards

## Core Principle
Meaningful tests > coverage theater.

## Good Tests
- Exercise real behavior
- Cover edge cases: empty, boundary, error states
- Mocks only for external dependencies

## Bad Tests
- Heavy mocking that just verifies mock was called
- Pass regardless of implementation correctness

## Agent-Assisted Testing
- Use verifier subagents for adversarial review
- Check: "What inputs would break this?"
- Validate error paths, not just happy paths
'''

ERROR_HANDLING_MD = '''# Error Handling

## Core Principle
Thoughtful, not paranoid. Handle at appropriate abstraction level.

## Good Error Handling
- Context in messages: what failed, why, what to do
- Specific exception types
- Fail fast on invariant violations

## Anti-Patterns
- Silent swallowing (try/except: pass)
- Paranoid try/except without understanding why error occurs

## Agent Error Escalation
When agents encounter errors:
1. Log with full context (correlation_id, agent_id)
2. Escalate if: blocked, security-related, or affects other agents
3. Include: what was attempted, what failed, suggested recovery
'''

MESSAGE_PROTOCOL_MD = '''# Inter-Agent Message Protocol

## Message Types

| Type | Purpose |
|------|---------|
| request | Task assignment with correlation_id |
| response | Task result (1-2k token summary) |
| handoff | Transfer to another agent |
| escalation | Problem requiring attention |
| checkpoint | State snapshot for context refresh |

## Agent ID Format
```
user:primary           → Human operator
orch:session_abc       → Orchestrator
spec:backend:auth01    → Backend specialist
verif:review_001       → Verifier
```

## Protocol Rules
1. Always include correlation_id
2. Handoffs must include critical_decisions
3. Responses capped at 1-2k tokens (compaction)
4. Escalations require severity + requires_action
5. Checkpoints must include resume_instructions

## Handoff Template
```markdown
## Handoff: {from_agent} → {to_agent}
Correlation: {corr_id}

### Critical Decisions
1. [Decision + rationale]

### Files to Review
- /path/to/file.py (lines X-Y)

### Open Questions
1. [Unresolved item]

### Next Steps
[Specific actionable items]
```
'''

LOG_FORMAT_MD = '''# Logging Standard

## Format: JSONL with Hooks Support
Location: `~/.claude/logs/{date}/{session-id}.jsonl`

## Required Fields
| Field | Type | Description |
|-------|------|-------------|
| ts | ISO8601 | Timestamp |
| lvl | enum | debug, info, warn, error, fatal |
| cid | string | Correlation ID |
| aid | string | Agent ID |
| evt | string | Event type |
| msg | string | Human-readable (<100 chars) |

## Hook Events (Claude Agent SDK Pattern)
| Event | When | Extra Fields |
|-------|------|--------------|
| hook.pre_tool | Before tool execution | tool_name, tool_input |
| hook.post_tool | After tool execution | tool_name, tool_result |
| hook.session_start | Session begins | model, context_size |
| hook.session_end | Session ends | tokens_used, duration_ms |

## Event Types
- agent.spawned
- task.started
- task.completed
- decision.made
- handoff.initiated
- escalation.raised
- context.compacted

## Query Examples
```bash
# All hook events
jq 'select(.evt | startswith("hook."))' session.jsonl

# Tool execution trace
jq 'select(.evt=="hook.pre_tool" or .evt=="hook.post_tool")' session.jsonl

# Context compaction events
jq 'select(.evt=="context.compacted")' session.jsonl
```
'''

THINKING_TRIGGERS_MD = '''# Extended Thinking Integration

## Alignment with budget_tokens

Claude\'s extended thinking uses `budget_tokens` to control reasoning depth.
These semantic triggers map to recommended budget ranges:

| Trigger | budget_tokens | Exploration Depth | Use Case |
|---------|---------------|-------------------|----------|
| `think` | 1,024-2,048 | Surface-level | Simple decisions, quick checks |
| `think hard` | 4,096-8,192 | Multi-angle | Trade-offs, moderate complexity |
| `think harder` | 16,384-32,768 | Exhaustive | Architecture, edge cases, debugging |
| `ultrathink` | 65,536+ | Maximum | Security review, novel problems |

## API Configuration
```python
# For think hard (~8k budget)
thinking={
    "type": "enabled",
    "budget_tokens": 8192
}

# For ultrathink (maximum)
thinking={
    "type": "enabled",
    "budget_tokens": 65536
}
```

## Interleaved Thinking (Claude 4.x)
For complex multi-step tasks with tools:
- Thinking occurs between tool calls
- Budget can exceed max_tokens
- Requires beta header: `interleaved-thinking-2025-05-14`

## Usage in Agent Prompts
```
# Simple
think about whether this needs error handling

# Moderate
think hard about the API boundary between these services

# Deep
think harder about race conditions in this concurrent code

# Maximum
ultrathink about the security implications of this auth flow
```

## Agent Interpretation
1. **Not programmatically enforced** — Semantic cues, not commands
2. **Scale reasoning proportionally** — More trigger = more alternatives
3. **Document proportionally** — Higher depth = more explicit reasoning
4. **Preserve thinking blocks** — Required for tool loops

## Prompt Caching Considerations
- System prompts cached even when thinking parameters change
- Message cache invalidates when budget_tokens changes
- Use consistent budgets for cache efficiency
'''

CONTEXT_MANAGEMENT_MD = '''# Context Window Management

## Core Principle
Context is a precious, finite resource requiring strategic curation.

## Strategies

### 1. Compaction
When approaching context limits:
- Summarize conversation history
- Preserve: critical decisions, open issues, recent file references
- Discard: redundant tool outputs, verbose explanations
- Target: Maximize recall first, then improve precision

### 2. Progressive Disclosure
Load context on-demand:
```
Level 1: Skill name + description (always)
Level 2: Full SKILL.md (when relevant)
Level 3: Supplementary files (on-demand via read)
```

### 3. Sub-Agent Isolation
- Sub-agents work in isolated contexts
- Return only condensed summaries (1-2k tokens)
- Main agent synthesizes, never forwards raw output

### 4. Structured Memory
Maintain state external to context:
- JSON for schemas (validated state)
- Text files for notes (unstructured progress)
- Git commits for checkpoints

## Context-Aware Prompting

### For Long Tasks
```
Your context window will be automatically compacted as it approaches
its limit, allowing you to continue working indefinitely. Do not stop
early due to token budget. Save progress before refresh.
```

### For Multi-Window Tasks
1. First window: Build framework (tests, setup)
2. Subsequent windows: Iterate on todo-list
3. Use init.sh scripts for graceful restarts
4. Track state in JSON + git

## Claude 4.5 Context Awareness
- Model tracks remaining token budget
- Can self-manage context pacing
- Inform model about compaction capabilities

## Compaction Triggers
- 80% context utilization
- Before agent handoff
- After major subtask completion
- Every N tool executions (configurable)
'''

AGENT_VIRTUALIZATION_MD = '''# Agent Virtualization in Claude Code

## Claude Code Built-in Agents

| Agent | Purpose | Context |
|-------|---------|---------|
| general-purpose | Main conversation | Full session |
| Explore | Read-only investigation | Scoped |
| Plan | Step-by-step planning | Scoped |

## Mapping: Conceptual → Claude Code

| Conceptual Role | Claude Code Agent | Implementation |
|-----------------|-------------------|----------------|
| `orch:{session}` | general-purpose | Orchestrates, tracks state |
| `spec:{domain}:{id}` | Task (any type) | Role in prompt, correlation ID |
| `verif:{id}` | Task (Explore) | Read-only suits review |
| `user:{id}` | N/A | Human in conversation |

## Task Prompt Template
```
You are spec:backend:auth01
Correlation: corr_session123_007

Task: Implement token refresh logic
Context: [previous decisions summary]

Report back with (max 1,500 tokens):
- files_modified
- decisions_made
- open_questions
```

## Forked Context Pattern (SKILL.md)
```yaml
---
name: isolated-analysis
context: fork
---
[Instructions for isolated execution]
```

## Hooks Integration
```python
# PreToolUse hook for logging
@hook("PreToolUse")
async def log_tool_use(tool_name, tool_input):
    logger.log("info", "hook.pre_tool",
               f"Executing {tool_name}",
               tool_name=tool_name,
               tool_input=tool_input)

# PostToolUse hook for validation
@hook("PostToolUse")
async def validate_result(tool_name, tool_result):
    if tool_name == "Bash" and "error" in tool_result.lower():
        logger.escalation("Tool returned error", severity="blocked")
```

## MCP Integration Points
```json
{
  "mcpServers": {
    "postgres": {
      "command": "mcp-server-postgres",
      "args": ["--connection-string", "$DATABASE_URL"]
    }
  }
}
```

## Limitations & Mitigations

| Limitation | Mitigation |
|------------|------------|
| No true parallelism | Batch independent work |
| Context not isolated | `context: fork` in skills |
| No persistent state | JSONL logs + git |
| No native agent ID | Embed in prompt |
'''

EXAMPLE_SKILL_MD = '''---
name: code-review
description: Adversarial code review with security focus
user-invocable: true
context: fork
---

# Code Review Skill

You are verif:security_001, an adversarial reviewer.

## Mission
Review code changes for:
- Security vulnerabilities
- Unhandled edge cases
- Performance issues
- Test coverage gaps

## Process
1. Read all modified files
2. Identify critical paths
3. Check: "What inputs would break this?"
4. Review error handling
5. Verify test coverage

## Output Format (max 1,500 tokens)
```markdown
## Security Findings
- [severity: critical|high|medium|low]
- [location: file:line]
- [issue: description]
- [recommendation: fix]

## Edge Cases
- [uncovered scenarios]

## Test Gaps
- [missing test coverage]

## Approved: [yes/no]
```
'''

PROJECT_MANIFEST_MD = '''# Project Manifest

> Source of truth for project-specific agent configuration.

## Project

| Field | Value |
|-------|-------|
| Name | {project-name} |
| Root | {project-root} |

## Agent Configuration

| Setting | Value |
|---------|-------|
| Log Location | .claude/logs/{date}/ |
| Session | auto-generated |
| Format | JSONL |
| Thinking Default | think hard (~8k) |

## MCP Servers (Optional)
```json
{
  "mcpServers": {}
}
```

## Complexity Zones

| Path | Level | Thinking |
|------|-------|----------|
| `**/auth/**` | critical | ultrathink |
| `**/api/**` | high | think harder |
| `scripts/**` | low | think |

## Project-Specific Instructions

```
# Example:
# - Use uv for Python package management
# - Run tests with: pytest
# - Prefer structured logging
```
'''

PROJECT_LOGGING_MD = '''# Project Logging Guide

## Standard Event Types

### Request Lifecycle
| Event | When | Required Fields |
|-------|------|-----------------|
| `request.received` | Handler entry | `method`, `path`, `correlation_id` |
| `request.completed` | Handler exit | `status`, `duration_ms`, `correlation_id` |

### Agent Hooks
| Event | When | Required Fields |
|-------|------|-----------------|
| `hook.pre_tool` | Before tool use | `tool_name`, `tool_input` |
| `hook.post_tool` | After tool use | `tool_name`, `tool_result`, `duration_ms` |

### Context Management
| Event | When | Required Fields |
|-------|------|-----------------|
| `context.checkpoint` | Before compaction | `tokens_used`, `summary` |
| `context.compacted` | After compaction | `tokens_saved`, `preserved_decisions` |

## Python Example (with Hooks)

```python
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude/lib"))

from logger import get_logger, HookType

log = get_logger(agent_id="spec:backend:auth01")

# Register hook
@log.hook(HookType.PRE_TOOL)
def before_tool(tool_name: str, tool_input: dict):
    log.log("debug", "hook.pre_tool", f"Calling {tool_name}")

# Task logging
log.task_started("Implementing feature")
log.decision_made("Using JWT", rationale="Industry standard")
log.task_completed("Feature complete")
```

## What to Log

| Category | Examples | Level |
|----------|----------|-------|
| Decisions | Route selection, cache hit/miss | INFO |
| Errors | Exceptions, validation failures | ERROR |
| Boundaries | External API calls, DB queries | INFO |
| Hooks | Tool pre/post execution | DEBUG |

## What NOT to Log

| Never Log | Why |
|-----------|-----|
| Passwords, tokens, API keys | Security |
| PII | Compliance |
| Full tool outputs | Volume |
| Raw context windows | Size |
'''

LOGGER_PY = '''"""
Logging library for meta-agent architecture v2.0.

Features:
- JSONL format with correlation tracking
- Hook support (PreToolUse, PostToolUse, SessionStart, SessionEnd)
- Context compaction logging
- Session continuity across agents
"""
from __future__ import annotations

import json
import os
import secrets
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, Literal

LogLevel = Literal["debug", "info", "warn", "error", "fatal"]


class HookType(Enum):
    """Hook types aligned with Claude Agent SDK."""
    PRE_TOOL = "pre_tool"
    POST_TOOL = "post_tool"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    CONTEXT_COMPACT = "context_compact"


@dataclass
class HookRegistry:
    """Registry for hook callbacks."""
    hooks: dict[HookType, list[Callable]] = field(default_factory=dict)

    def register(self, hook_type: HookType, callback: Callable) -> None:
        if hook_type not in self.hooks:
            self.hooks[hook_type] = []
        self.hooks[hook_type].append(callback)

    async def trigger(self, hook_type: HookType, **kwargs) -> None:
        for callback in self.hooks.get(hook_type, []):
            if asyncio_available():
                import asyncio
                if asyncio.iscoroutinefunction(callback):
                    await callback(**kwargs)
                else:
                    callback(**kwargs)
            else:
                callback(**kwargs)


def asyncio_available() -> bool:
    try:
        import asyncio
        return True
    except ImportError:
        return False


# Module-level session tracking
_current_session: str | None = None
_hook_registry = HookRegistry()


def _get_home() -> Path:
    return Path(os.environ.get("HOME", Path.home()))


def _generate_session_id() -> str:
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    random_part = secrets.token_hex(4)
    return f"sess_{date_part}_{random_part}"


def get_current_session() -> str:
    global _current_session
    if _current_session is None:
        _current_session = _generate_session_id()
    return _current_session


def set_current_session(session_id: str) -> None:
    global _current_session
    _current_session = session_id


def is_project_context() -> bool:
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        project_claude = parent / ".claude"
        if project_claude.is_dir() and parent != _get_home():
            return True
    return False


def get_project_root() -> Path | None:
    cwd = Path.cwd()
    home = _get_home()
    for parent in [cwd, *cwd.parents]:
        project_claude = parent / ".claude"
        if project_claude.is_dir() and parent != home:
            return parent
    return None


class AgentLogger:
    """
    JSONL logger with hooks support for meta-agent architecture.

    Usage:
        log = get_logger(agent_id="spec:backend:auth01")

        # Register hooks
        @log.hook(HookType.PRE_TOOL)
        def before_tool(tool_name, tool_input):
            print(f"Calling {tool_name}")

        # Log events
        log.task_started("Implementing auth")
        log.decision_made("Using JWT", rationale="Industry standard")
    """

    def __init__(
        self,
        session_id: str | None = None,
        agent_id: str = "orch:default",
    ) -> None:
        if session_id is None:
            self.session_id = get_current_session()
        else:
            self.session_id = session_id
            set_current_session(session_id)

        self.agent_id = agent_id
        self._seq = 0
        self._log_dir = self._get_log_dir()
        self._log_file = self._log_dir / f"{self.session_id}.jsonl"
        self._ensure_dir()
        self._local_hooks = HookRegistry()
        self._start_time = datetime.now(timezone.utc)
        self._tokens_used = 0

    def _get_log_dir(self) -> Path:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return _get_home() / ".claude" / "logs" / date_str

    def _ensure_dir(self) -> None:
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def _next_correlation_id(self) -> str:
        self._seq += 1
        return f"corr_{self.session_id}_{self._seq:03d}"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def hook(self, hook_type: HookType) -> Callable:
        """Decorator to register a hook callback."""
        def decorator(func: Callable) -> Callable:
            self._local_hooks.register(hook_type, func)
            return func
        return decorator

    def log(
        self,
        lvl: LogLevel,
        evt: str,
        msg: str,
        *,
        cid: str | None = None,
        **kwargs: Any,
    ) -> str:
        if len(msg) > 100:
            msg = msg[:97] + "..."

        correlation_id = cid or self._next_correlation_id()

        entry = {
            "ts": self._now(),
            "lvl": lvl,
            "cid": correlation_id,
            "aid": self.agent_id,
            "evt": evt,
            "msg": msg,
            **kwargs,
        }

        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + chr(10))

        return correlation_id

    # Hook-aware logging methods
    def log_pre_tool(self, tool_name: str, tool_input: Any) -> str:
        """Log before tool execution (hook.pre_tool)."""
        return self.log(
            "debug", "hook.pre_tool", f"Executing {tool_name}",
            tool_name=tool_name,
            tool_input=str(tool_input)[:500]  # Truncate large inputs
        )

    def log_post_tool(
        self,
        tool_name: str,
        tool_result: Any,
        duration_ms: int | None = None
    ) -> str:
        """Log after tool execution (hook.post_tool)."""
        extra = {"tool_name": tool_name}
        if duration_ms is not None:
            extra["duration_ms"] = duration_ms
        return self.log(
            "debug", "hook.post_tool", f"Completed {tool_name}",
            tool_result=str(tool_result)[:500],
            **extra
        )

    def log_context_compact(
        self,
        tokens_before: int,
        tokens_after: int,
        preserved_decisions: list[str] | None = None
    ) -> str:
        """Log context compaction event."""
        return self.log(
            "info", "context.compacted",
            f"Compacted context: {tokens_before} → {tokens_after}",
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            tokens_saved=tokens_before - tokens_after,
            preserved_decisions=preserved_decisions or []
        )

    # Standard logging methods
    def task_started(self, description: str, **kwargs: Any) -> str:
        return self.log("info", "task.started", description, **kwargs)

    def task_completed(self, description: str, **kwargs: Any) -> str:
        return self.log("info", "task.completed", description, **kwargs)

    def decision_made(
        self,
        decision: str,
        *,
        rationale: str | None = None,
        alternatives: list[str] | None = None,
        thinking_budget: int | None = None,
        **kwargs: Any,
    ) -> str:
        extra: dict[str, Any] = {}
        if rationale:
            extra["rationale"] = rationale
        if alternatives:
            extra["alternatives"] = alternatives
        if thinking_budget:
            extra["thinking_budget"] = thinking_budget
        return self.log("info", "decision.made", decision, **extra, **kwargs)

    def agent_spawned(
        self,
        child_agent_id: str,
        *,
        task: str | None = None,
        thinking_trigger: str | None = None,
        **kwargs: Any,
    ) -> str:
        msg = f"Spawned {child_agent_id}"
        extra: dict[str, Any] = {"child_aid": child_agent_id}
        if task:
            extra["task"] = task
        if thinking_trigger:
            extra["thinking_trigger"] = thinking_trigger
        return self.log("info", "agent.spawned", msg, **extra, **kwargs)

    def handoff(
        self,
        target_agent_id: str,
        *,
        critical_decisions: list[str] | None = None,
        open_questions: list[str] | None = None,
        files_to_review: list[str] | None = None,
        summary_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        msg = f"Handoff to {target_agent_id}"
        extra: dict[str, Any] = {"target_aid": target_agent_id}
        if critical_decisions:
            extra["critical_decisions"] = critical_decisions
        if open_questions:
            extra["open_questions"] = open_questions
        if files_to_review:
            extra["files_to_review"] = files_to_review
        if summary_tokens:
            extra["summary_tokens"] = summary_tokens
        return self.log("info", "handoff.initiated", msg, **extra, **kwargs)

    def escalation(
        self,
        reason: str,
        *,
        severity: Literal["blocked", "uncertain", "security"] = "blocked",
        context: str | None = None,
        **kwargs: Any,
    ) -> str:
        lvl: LogLevel = "error" if severity == "security" else "warn"
        extra: dict[str, Any] = {"severity": severity}
        if context:
            extra["context"] = context
        return self.log(lvl, "escalation.raised", reason, **extra, **kwargs)

    def __enter__(self) -> AgentLogger:
        self._start_time = datetime.now(timezone.utc)
        self.log("info", "hook.session_start", f"Session {self.session_id} started")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        duration_ms = int(
            (datetime.now(timezone.utc) - self._start_time).total_seconds() * 1000
        )
        if exc_type is not None:
            self.log(
                "error", "hook.session_end",
                f"Session ended with error: {exc_type.__name__}",
                error=str(exc_val),
                duration_ms=duration_ms
            )
        else:
            self.log(
                "info", "hook.session_end",
                f"Session {self.session_id} ended",
                duration_ms=duration_ms
            )
        return False

    def query(
        self,
        jq_filter: str,
        *,
        session_id: str | None = None,
        date: str | None = None,
    ) -> list[dict[str, Any]]:
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        sid = session_id or self.session_id
        log_path = _get_home() / ".claude" / "logs" / date / f"{sid}.jsonl"

        if not log_path.exists():
            return []

        try:
            result = subprocess.run(
                ["jq", "-c", jq_filter, str(log_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            entries = []
            for line in result.stdout.strip().splitlines():
                if line:
                    entries.append(json.loads(line))
            return entries
        except FileNotFoundError:
            raise RuntimeError("jq not found. Install with: brew install jq (macOS) or apt install jq (Linux)")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"jq query failed: {e.stderr}")


class ProjectLogger(AgentLogger):
    """Logger for project-scoped logs at project/.claude/logs/"""

    def __init__(
        self,
        session_id: str | None = None,
        agent_id: str = "orch:default",
        *,
        project_root: Path | None = None,
    ) -> None:
        self._project_root = project_root or get_project_root()
        if self._project_root is None:
            raise ValueError(
                "Not in a project context. Use AgentLogger for global logging."
            )
        super().__init__(session_id, agent_id)

    def _get_log_dir(self) -> Path:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._project_root / ".claude" / "logs" / date_str


def get_logger(
    session_id: str | None = None,
    agent_id: str = "orch:default",
    *,
    prefer_project: bool = True,
    auto_cleanup: bool = True,
) -> AgentLogger:
    """
    Factory function to get appropriate logger.

    Args:
        session_id: Optional session ID. Auto-generated if not provided.
        agent_id: Agent identifier (e.g., "spec:backend:auth01")
        prefer_project: If True and in project context, use ProjectLogger
        auto_cleanup: If True, run cleanup on initialization

    Returns:
        AgentLogger or ProjectLogger instance
    """
    if auto_cleanup:
        cleanup_logs(quiet=True)

    if prefer_project and is_project_context():
        return ProjectLogger(session_id, agent_id)
    return AgentLogger(session_id, agent_id)


# =============================================================================
# Log Management & Cleanup
# =============================================================================

# Configuration defaults
LOG_RETENTION_DAYS = 7          # Keep logs for 7 days
LOG_MAX_SIZE_MB = 50            # Max total log size in MB
LOG_MAX_FILES = 100             # Max number of log files
COMPACT_AFTER_DAYS = 3          # Compact logs older than 3 days


def get_log_stats(log_dir: Path | None = None) -> dict[str, Any]:
    """Get statistics about current log storage."""
    if log_dir is None:
        log_dir = _get_home() / ".claude" / "logs"

    if not log_dir.exists():
        return {"total_files": 0, "total_size_bytes": 0, "total_size_mb": 0.0, "oldest_date": None, "newest_date": None}

    files = list(log_dir.rglob("*.jsonl"))
    total_size = sum(f.stat().st_size for f in files)
    dates = sorted(set(f.parent.name for f in files if f.parent.name.startswith("20")))

    return {
        "total_files": len(files),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "oldest_date": dates[0] if dates else None,
        "newest_date": dates[-1] if dates else None,
        "dates": dates,
    }


def cleanup_logs(
    log_dir: Path | None = None,
    retention_days: int = LOG_RETENTION_DAYS,
    max_size_mb: float = LOG_MAX_SIZE_MB,
    max_files: int = LOG_MAX_FILES,
    dry_run: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
    """
    Clean up old logs based on retention policy.

    Args:
        log_dir: Log directory (default: ~/.claude/logs)
        retention_days: Delete logs older than this many days
        max_size_mb: Maximum total size before cleanup
        max_files: Maximum number of log files to keep
        dry_run: If True, report what would be deleted without deleting
        quiet: If True, suppress output

    Returns:
        Dict with cleanup statistics
    """
    if log_dir is None:
        log_dir = _get_home() / ".claude" / "logs"

    if not log_dir.exists():
        return {"deleted_files": 0, "freed_bytes": 0, "reason": "no_logs"}

    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=retention_days)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")

    files_to_delete: list[Path] = []
    reasons: dict[Path, str] = {}

    # Get all log files sorted by date (oldest first)
    all_files = sorted(log_dir.rglob("*.jsonl"), key=lambda f: f.stat().st_mtime)

    # 1. Mark files older than retention period
    for f in all_files:
        date_dir = f.parent.name
        if date_dir < cutoff_str:
            files_to_delete.append(f)
            reasons[f] = f"older than {retention_days} days"

    # 2. Check total size and mark oldest files if over limit
    total_size = sum(f.stat().st_size for f in all_files)
    max_size_bytes = max_size_mb * 1024 * 1024

    if total_size > max_size_bytes:
        remaining = [f for f in all_files if f not in files_to_delete]
        current_size = sum(f.stat().st_size for f in remaining)

        for f in remaining:
            if current_size <= max_size_bytes * 0.8:  # Clean to 80% of limit
                break
            if f not in files_to_delete:
                files_to_delete.append(f)
                reasons[f] = f"over size limit ({max_size_mb}MB)"
                current_size -= f.stat().st_size

    # 3. Check file count and mark oldest if over limit
    remaining = [f for f in all_files if f not in files_to_delete]
    if len(remaining) > max_files:
        excess = len(remaining) - int(max_files * 0.8)  # Clean to 80% of limit
        for f in remaining[:excess]:
            if f not in files_to_delete:
                files_to_delete.append(f)
                reasons[f] = f"over file limit ({max_files})"

    # Calculate stats
    freed_bytes = sum(f.stat().st_size for f in files_to_delete)

    if not quiet and files_to_delete:
        print(f"Log cleanup: {len(files_to_delete)} files, {freed_bytes / 1024:.1f}KB")

    # Perform deletion
    deleted_files = 0
    if not dry_run:
        for f in files_to_delete:
            try:
                f.unlink()
                deleted_files += 1
            except OSError:
                pass

        # Remove empty date directories
        for date_dir in log_dir.iterdir():
            if date_dir.is_dir() and not any(date_dir.iterdir()):
                try:
                    date_dir.rmdir()
                except OSError:
                    pass

    return {
        "deleted_files": deleted_files if not dry_run else len(files_to_delete),
        "freed_bytes": freed_bytes,
        "freed_mb": round(freed_bytes / (1024 * 1024), 2),
        "dry_run": dry_run,
        "files": [str(f) for f in files_to_delete] if dry_run else [],
        "reasons": {str(k): v for k, v in reasons.items()} if dry_run else {},
    }


def compact_old_sessions(
    log_dir: Path | None = None,
    days_threshold: int = COMPACT_AFTER_DAYS,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Compact old session logs by keeping only decision events.

    Preserves: decision.made, escalation.raised, handoff.initiated, session_start/end
    Removes: hook events, debug logs, verbose tool outputs

    Args:
        log_dir: Log directory (default: ~/.claude/logs)
        days_threshold: Compact sessions older than this many days
        dry_run: If True, report what would be compacted

    Returns:
        Dict with compaction statistics
    """
    if log_dir is None:
        log_dir = _get_home() / ".claude" / "logs"

    if not log_dir.exists():
        return {"compacted_files": 0, "saved_bytes": 0}

    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=days_threshold)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")

    # Events to preserve (critical for memory)
    preserve_events = {
        "decision.made", "escalation.raised", "handoff.initiated",
        "hook.session_start", "hook.session_end",
        "task.started", "task.completed", "context.compacted"
    }

    compacted = 0
    saved_bytes = 0

    for log_file in log_dir.rglob("*.jsonl"):
        date_dir = log_file.parent.name
        if date_dir >= cutoff_str:
            continue  # Skip recent logs

        # Check if already compacted
        if log_file.stem.endswith("_compacted"):
            continue

        original_size = log_file.stat().st_size
        preserved_lines = []

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        evt = entry.get("evt", "")
                        lvl = entry.get("lvl", "")
                        # Keep important events and errors
                        if evt in preserve_events or lvl in ("error", "fatal", "warn"):
                            preserved_lines.append(line)
                    except json.JSONDecodeError:
                        continue

            if not dry_run and preserved_lines:
                # Write compacted version
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(chr(10).join(preserved_lines) + chr(10))

                new_size = log_file.stat().st_size
                saved_bytes += original_size - new_size
                compacted += 1

        except (OSError, IOError):
            continue

    return {
        "compacted_files": compacted,
        "saved_bytes": saved_bytes,
        "saved_mb": round(saved_bytes / (1024 * 1024), 2),
        "dry_run": dry_run,
    }


# Import timedelta for cleanup functions
from datetime import timedelta
'''

INIT_PROJECT_PY = '''#!/usr/bin/env python3
"""
init-project - Bootstrap project manifest for Claude meta-agent system.

Usage: init-project [project-path]
Creates project/.claude/manifest.md and project/.claude/logs/
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def get_template() -> str:
    template_path = Path.home() / ".claude" / "templates" / "project-manifest.md"
    if not template_path.exists():
        print(f"error: template not found at {template_path}", file=sys.stderr)
        sys.exit(1)
    return template_path.read_text()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap a project with Claude meta-agent manifest."
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Path to project root (default: current directory)"
    )
    args = parser.parse_args()

    project_dir = Path(args.project_path).resolve()
    claude_dir = project_dir / ".claude"
    manifest_path = claude_dir / "manifest.md"

    if manifest_path.exists():
        print(f"exists: {manifest_path}", file=sys.stderr)
        sys.exit(0)

    # Create directories
    (claude_dir / "logs").mkdir(parents=True, exist_ok=True)
    (claude_dir / "skills").mkdir(exist_ok=True)

    # Generate manifest from template
    template = get_template()
    project_name = project_dir.name
    manifest_content = template.replace("{project-name}", project_name)
    manifest_content = manifest_content.replace("{project-root}", str(project_dir))

    manifest_path.write_text(manifest_content)

    print(f"initialized: {manifest_path}")
    print(f"  project: {project_name}")
    print(f"  logs: {claude_dir / 'logs'}/")
    print(f"  skills: {claude_dir / 'skills'}/")


if __name__ == "__main__":
    main()
'''

QUERY_LOGS_PY = '''#!/usr/bin/env python3
"""
query-logs - Search JSONL logs with jq filters.

Usage: query-logs <jq-filter> [session-id] [--global|--project]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def find_logs(log_dir: Path, session_filter: str | None = None) -> list[Path]:
    """Find all JSONL log files, optionally filtered by session."""
    if not log_dir.exists():
        return []

    files = list(log_dir.rglob("*.jsonl"))
    if session_filter:
        files = [f for f in files if session_filter.lower() in f.name.lower()]
    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search Claude agent JSONL logs with jq filters."
    )
    parser.add_argument("jq_filter", help="jq expression")
    parser.add_argument("session_id", nargs="?", help="Optional session ID filter")
    parser.add_argument("--global", dest="search_global", action="store_true",
                        help="Search only ~/.claude/logs/")
    parser.add_argument("--project", dest="search_project", action="store_true",
                        help="Search only ./.claude/logs/")
    args = parser.parse_args()

    # Check jq availability
    try:
        subprocess.run(["jq", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        print("error: jq required. Install: brew install jq (macOS) or apt install jq (Linux)",
              file=sys.stderr)
        sys.exit(1)

    # Determine search locations
    search_global = not args.search_project
    search_project = not args.search_global

    log_files: list[Path] = []

    if search_global:
        global_logs = Path.home() / ".claude" / "logs"
        log_files.extend(find_logs(global_logs, args.session_id))

    if search_project:
        project_logs = Path.cwd() / ".claude" / "logs"
        log_files.extend(find_logs(project_logs, args.session_id))

    if not log_files:
        print("no log files found", file=sys.stderr)
        sys.exit(0)

    for log_file in log_files:
        print(f"# {log_file}", file=sys.stderr)
        try:
            result = subprocess.run(
                ["jq", "-c", args.jq_filter, str(log_file)],
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                print(result.stdout.strip())
            if result.returncode != 0 and result.stderr:
                print(f"  warning: {result.stderr.strip()}", file=sys.stderr)
        except Exception as e:
            print(f"  error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
'''

CLEANUP_LOGS_PY = '''#!/usr/bin/env python3
"""
cleanup-logs - Manage log retention and storage for the orchestration hub.

Usage:
    cleanup-logs                    # Run cleanup with defaults
    cleanup-logs --status           # Show log statistics
    cleanup-logs --dry-run          # Preview what would be deleted
    cleanup-logs --compact          # Compact old logs (keep decisions only)
    cleanup-logs --retention 14     # Keep logs for 14 days
    cleanup-logs --max-size 100     # Max 100MB total
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


# Defaults
DEFAULT_RETENTION_DAYS = 7
DEFAULT_MAX_SIZE_MB = 50
DEFAULT_MAX_FILES = 100
DEFAULT_COMPACT_DAYS = 3


def get_log_dir() -> Path:
    return Path.home() / ".claude" / "logs"


def get_stats(log_dir: Path) -> dict:
    if not log_dir.exists():
        return {"files": 0, "size_mb": 0, "oldest": None, "newest": None}

    files = list(log_dir.rglob("*.jsonl"))
    if not files:
        return {"files": 0, "size_mb": 0, "oldest": None, "newest": None}

    total_size = sum(f.stat().st_size for f in files)
    dates = sorted(set(f.parent.name for f in files if f.parent.name.startswith("20")))

    return {
        "files": len(files),
        "size_mb": round(total_size / (1024 * 1024), 2),
        "size_kb": round(total_size / 1024, 1),
        "oldest": dates[0] if dates else None,
        "newest": dates[-1] if dates else None,
        "dates": dates,
    }


def cleanup(
    log_dir: Path,
    retention_days: int,
    max_size_mb: float,
    max_files: int,
    dry_run: bool = False,
) -> dict:
    if not log_dir.exists():
        return {"deleted": 0, "freed_kb": 0}

    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=retention_days)).strftime("%Y-%m-%d")

    files = sorted(log_dir.rglob("*.jsonl"), key=lambda f: f.stat().st_mtime)
    to_delete = []
    reasons = {}

    # 1. Old files
    for f in files:
        if f.parent.name < cutoff:
            to_delete.append(f)
            reasons[f] = f"older than {retention_days}d"

    # 2. Size limit
    remaining = [f for f in files if f not in to_delete]
    total = sum(f.stat().st_size for f in remaining)
    limit = max_size_mb * 1024 * 1024

    if total > limit:
        for f in remaining:
            if total <= limit * 0.8:
                break
            to_delete.append(f)
            reasons[f] = "size limit"
            total -= f.stat().st_size

    # 3. File count limit
    remaining = [f for f in files if f not in to_delete]
    if len(remaining) > max_files:
        for f in remaining[:len(remaining) - int(max_files * 0.8)]:
            to_delete.append(f)
            reasons[f] = "file limit"

    freed = sum(f.stat().st_size for f in to_delete)

    if not dry_run:
        for f in to_delete:
            try:
                f.unlink()
            except OSError:
                pass
        # Remove empty dirs
        for d in log_dir.iterdir():
            if d.is_dir() and not any(d.iterdir()):
                try:
                    d.rmdir()
                except OSError:
                    pass

    return {
        "deleted": len(to_delete),
        "freed_kb": round(freed / 1024, 1),
        "freed_mb": round(freed / (1024 * 1024), 2),
        "dry_run": dry_run,
        "files": [(str(f), reasons.get(f, "")) for f in to_delete] if dry_run else [],
    }


def compact(log_dir: Path, days_threshold: int, dry_run: bool = False) -> dict:
    if not log_dir.exists():
        return {"compacted": 0, "saved_kb": 0}

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_threshold)).strftime("%Y-%m-%d")

    # Events to keep (critical memory)
    keep_events = {
        "decision.made", "escalation.raised", "handoff.initiated",
        "hook.session_start", "hook.session_end",
        "task.started", "task.completed", "context.compacted"
    }

    compacted = 0
    saved = 0

    for f in log_dir.rglob("*.jsonl"):
        if f.parent.name >= cutoff:
            continue
        if f.stem.endswith("_compacted"):
            continue

        orig_size = f.stat().st_size
        kept = []

        try:
            for line in f.read_text().splitlines():
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    evt = entry.get("evt", "")
                    lvl = entry.get("lvl", "")
                    if evt in keep_events or lvl in ("error", "fatal", "warn"):
                        kept.append(line)
                except json.JSONDecodeError:
                    continue

            if not dry_run and kept:
                f.write_text("\\n".join(kept) + "\\n")
                saved += orig_size - f.stat().st_size
                compacted += 1

        except OSError:
            continue

    return {
        "compacted": compacted,
        "saved_kb": round(saved / 1024, 1),
        "dry_run": dry_run,
    }


def main():
    parser = argparse.ArgumentParser(description="Manage orchestration hub log storage")
    parser.add_argument("--status", action="store_true", help="Show log statistics")
    parser.add_argument("--dry-run", action="store_true", help="Preview without deleting")
    parser.add_argument("--compact", action="store_true", help="Compact old logs")
    parser.add_argument("--retention", type=int, default=DEFAULT_RETENTION_DAYS,
                        help=f"Days to retain (default: {DEFAULT_RETENTION_DAYS})")
    parser.add_argument("--max-size", type=float, default=DEFAULT_MAX_SIZE_MB,
                        help=f"Max size in MB (default: {DEFAULT_MAX_SIZE_MB})")
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES,
                        help=f"Max files (default: {DEFAULT_MAX_FILES})")
    parser.add_argument("--compact-days", type=int, default=DEFAULT_COMPACT_DAYS,
                        help=f"Compact logs older than N days (default: {DEFAULT_COMPACT_DAYS})")
    args = parser.parse_args()

    log_dir = get_log_dir()

    if args.status:
        stats = get_stats(log_dir)
        print(f"Log Statistics:")
        print(f"  Files: {stats['files']}")
        print(f"  Size: {stats['size_mb']}MB ({stats.get('size_kb', 0)}KB)")
        print(f"  Oldest: {stats['oldest'] or 'N/A'}")
        print(f"  Newest: {stats['newest'] or 'N/A'}")
        if stats.get('dates'):
            print(f"  Dates: {len(stats['dates'])} days of logs")
        return

    if args.compact:
        result = compact(log_dir, args.compact_days, args.dry_run)
        action = "Would compact" if args.dry_run else "Compacted"
        print(f"{action} {result['compacted']} files, saved {result['saved_kb']}KB")
        return

    # Default: cleanup
    result = cleanup(log_dir, args.retention, args.max_size, args.max_files, args.dry_run)
    action = "Would delete" if args.dry_run else "Deleted"
    print(f"{action} {result['deleted']} files, freed {result['freed_kb']}KB")

    if args.dry_run and result['files']:
        print("\\nFiles to delete:")
        for path, reason in result['files'][:10]:
            print(f"  {path} ({reason})")
        if len(result['files']) > 10:
            print(f"  ... and {len(result['files']) - 10} more")


if __name__ == "__main__":
    main()
'''


# =============================================================================
# Installation Logic
# =============================================================================

def check_existing() -> tuple[bool, bool, bool]:
    """Check for existing installation."""
    home = get_home()
    claude_dir = home / ".claude"
    claude_md = home / "CLAUDE.md"

    existing_dir = claude_dir.exists()
    existing_md_symlink = claude_md.is_symlink()
    existing_md_file = claude_md.is_file() and not claude_md.is_symlink()

    return existing_dir, existing_md_file, existing_md_symlink


def backup_existing(backup_dir: Path) -> None:
    """Create backup of existing installation."""
    home = get_home()
    claude_dir = home / ".claude"
    claude_md = home / "CLAUDE.md"

    if claude_dir.exists() or (claude_md.exists() and not claude_md.is_symlink()):
        print_info(f"Creating backup at {backup_dir}")
        backup_dir.mkdir(parents=True, exist_ok=True)

        if claude_dir.exists():
            shutil.copytree(claude_dir, backup_dir / ".claude")
            print_success("Backed up ~/.claude")

        if claude_md.exists() and not claude_md.is_symlink():
            shutil.copy2(claude_md, backup_dir / "CLAUDE.md")
            print_success("Backed up ~/CLAUDE.md")

        print_success(f"Backup complete: {backup_dir}")


def remove_existing() -> None:
    """Remove existing installation."""
    home = get_home()
    claude_dir = home / ".claude"
    claude_md = home / "CLAUDE.md"

    if claude_dir.exists():
        shutil.rmtree(claude_dir)
        print_info("Removed existing ~/.claude")

    if claude_md.is_symlink():
        claude_md.unlink()
        print_info("Removed existing ~/CLAUDE.md symlink")
    elif claude_md.exists():
        claude_md.unlink()
        print_info("Removed ~/CLAUDE.md")


def create_symlink() -> None:
    """Create ~/CLAUDE.md symlink (or copy on Windows without admin)."""
    home = get_home()
    claude_md = home / "CLAUDE.md"
    target = home / ".claude" / "CLAUDE.md"

    if not claude_md.exists():
        try:
            claude_md.symlink_to(target)
            print_success("Created ~/CLAUDE.md -> ~/.claude/CLAUDE.md symlink")
        except OSError:
            # Windows without admin privileges - fall back to copy
            shutil.copy2(target, claude_md)
            print_warning("Created ~/CLAUDE.md as copy (symlinks require admin on Windows)")


def install_files(mode: str) -> None:
    """Install all architecture files."""
    home = get_home()
    base = home / ".claude"

    # Create directory structure
    for subdir in ["docs", "templates", "skills/example", "lib", "bin", "logs"]:
        (base / subdir).mkdir(parents=True, exist_ok=True)

    # Write files
    files = {
        "CLAUDE.md": CLAUDE_MD,
        "README.md": README_MD,
        "docs/dev-philosophy.md": DEV_PHILOSOPHY_MD,
        "docs/pr-standards.md": PR_STANDARDS_MD,
        "docs/testing.md": TESTING_MD,
        "docs/error-handling.md": ERROR_HANDLING_MD,
        "docs/message-protocol.md": MESSAGE_PROTOCOL_MD,
        "docs/log-format.md": LOG_FORMAT_MD,
        "docs/thinking-triggers.md": THINKING_TRIGGERS_MD,
        "docs/context-management.md": CONTEXT_MANAGEMENT_MD,
        "docs/agent-virtualization.md": AGENT_VIRTUALIZATION_MD,
        "skills/example/SKILL.md": EXAMPLE_SKILL_MD,
        "templates/project-manifest.md": PROJECT_MANIFEST_MD,
        "templates/project-logging.md": PROJECT_LOGGING_MD,
        "lib/logger.py": LOGGER_PY,
        "bin/init-project": INIT_PROJECT_PY,
        "bin/query-logs": QUERY_LOGS_PY,
        "bin/cleanup-logs": CLEANUP_LOGS_PY,
    }

    for path, content in files.items():
        file_path = base / path
        file_path.write_text(content.strip() + "\n")

        # Make bin files executable
        if path.startswith("bin/"):
            file_path.chmod(0o755)

        print_success(path)

    # Write version file
    version_info = {
        "version": VERSION,
        "installed": get_iso_date(),
        "mode": mode
    }
    (base / ".version").write_text(json.dumps(version_info, indent=2) + "\n")
    print_success(".version")


def cmd_clean(skip_confirm: bool = False) -> None:
    """Clean install with backup."""
    show_banner()
    print()

    existing_dir, existing_md, _ = check_existing()
    backup_dir = get_backup_dir()

    if existing_dir or existing_md:
        print("Existing installation found:")
        if existing_dir:
            print("  - ~/.claude/")
        if existing_md:
            print("  - ~/CLAUDE.md")
        print()

        if not skip_confirm:
            response = input(f"{YELLOW}This will backup and replace. Continue? [y/N]{NC} ")
            if response.lower() not in ('y', 'yes'):
                print("Cancelled.")
                return
        print()
        backup_existing(backup_dir)

    remove_existing()
    install_files("clean")
    create_symlink()

    print()
    print_success("Clean installation complete!")
    print()
    print("Next steps:")
    print("  1. Review ~/.claude/README.md")
    print("  2. For projects: python ~/.claude/bin/init-project /path/to/project")


def cmd_update(skip_confirm: bool = False) -> None:
    """Update while preserving logs."""
    show_banner()
    print()

    existing_dir, _, _ = check_existing()

    if not existing_dir:
        print_error("No existing installation found. Use 'clean' for first install.")
        sys.exit(1)

    if not skip_confirm:
        response = input(f"{YELLOW}Update files? Logs preserved. [y/N]{NC} ")
        if response.lower() not in ('y', 'yes'):
            print("Cancelled.")
            return
    print()

    home = get_home()
    backup_dir = get_backup_dir()

    # Preserve logs
    logs_dir = home / ".claude" / "logs"
    temp_logs = None
    if logs_dir.exists():
        import tempfile
        temp_logs = Path(tempfile.mkdtemp())
        shutil.copytree(logs_dir, temp_logs / "logs")
        print_info("Preserving logs directory")

    backup_existing(backup_dir)
    remove_existing()
    install_files("update")

    # Restore logs
    if temp_logs and (temp_logs / "logs").exists():
        shutil.copytree(temp_logs / "logs", home / ".claude" / "logs", dirs_exist_ok=True)
        log_count = len(list((home / ".claude" / "logs").rglob("*.jsonl")))
        print_success(f"Restored {log_count} log file(s)")
        shutil.rmtree(temp_logs)

    create_symlink()

    print()
    print_success("Update complete!")


def cmd_status() -> None:
    """Show installation status."""
    show_banner()
    print()

    home = get_home()
    claude_dir = home / ".claude"

    if not claude_dir.exists():
        print(f"{YELLOW}Status: NOT INSTALLED{NC}")
        print()
        print("Run 'python install.py clean' to install.")
        return

    print(f"{GREEN}Status: INSTALLED{NC}")
    print()

    # Version info
    version_file = claude_dir / ".version"
    if version_file.exists():
        print(f"{BOLD}Version Information{NC}")
        version_data = json.loads(version_file.read_text())
        for k, v in version_data.items():
            print(f"    {k}: {v}")
        print()

    # File integrity
    print(f"{BOLD}File Integrity{NC}")
    expected_files = [
        "README.md", "CLAUDE.md",
        "docs/dev-philosophy.md", "docs/pr-standards.md", "docs/testing.md",
        "docs/error-handling.md", "docs/message-protocol.md", "docs/log-format.md",
        "docs/thinking-triggers.md", "docs/context-management.md",
        "docs/agent-virtualization.md",
        "templates/project-manifest.md", "templates/project-logging.md",
        "lib/logger.py", "bin/init-project", "bin/query-logs", "bin/cleanup-logs",
        "skills/example/SKILL.md"
    ]

    missing = 0
    for f in expected_files:
        if (claude_dir / f).exists():
            print(f"    {GREEN}[OK]{NC} {f}")
        else:
            print(f"    {RED}[X]{NC} {f} {DIM}(missing){NC}")
            missing += 1
    print()

    if missing > 0:
        print(f"{YELLOW}    {missing} file(s) missing. Run 'python install.py update' to repair.{NC}")
        print()

    # Logs stats
    print(f"{BOLD}Logs Directory{NC}")
    logs_dir = claude_dir / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.rglob("*.jsonl"))
        total_size = sum(f.stat().st_size for f in log_files)
        size_str = f"{total_size / 1024:.1f}KB" if total_size < 1024*1024 else f"{total_size / (1024*1024):.1f}MB"
        print(f"    Location: ~/.claude/logs/")
        print(f"    Files: {len(log_files)} session log(s)")
        print(f"    Size: {size_str}")
    else:
        print(f"    {DIM}No logs directory{NC}")
    print()


def cmd_uninstall(skip_confirm: bool = False, no_backup: bool = False) -> None:
    """Remove installation."""
    show_banner()
    print()

    existing_dir, _, _ = check_existing()

    if not existing_dir:
        print_warning("No installation found at ~/.claude/")
        return

    backup_dir = get_backup_dir()

    if no_backup:
        if not skip_confirm:
            response = input(f"{RED}Permanently delete ~/.claude/ without backup? [y/N]{NC} ")
            if response.lower() not in ('y', 'yes'):
                print("Cancelled.")
                return
    else:
        if not skip_confirm:
            response = input(f"{YELLOW}Backup and remove ~/.claude/? [y/N]{NC} ")
            if response.lower() not in ('y', 'yes'):
                print("Cancelled.")
                return
        backup_existing(backup_dir)

    remove_existing()
    print_success("Uninstalled ~/.claude/")

    if not no_backup:
        print()
        print(f"Backup saved at: {backup_dir}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Meta-Agent Architecture Installer v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  clean      Clean install with backup (recommended for first install)
  update     Update architecture files, preserve logs
  status     Show current installation status
  uninstall  Remove installation (with backup option)
  help       Show this help message

Examples:
  python install.py clean
  python install.py update -y
  python install.py status
"""
    )
    parser.add_argument("command", nargs="?", default="help",
                        choices=["clean", "update", "status", "uninstall", "help"])
    parser.add_argument("-y", "--yes", action="store_true",
                        help="Skip confirmation prompts")
    parser.add_argument("--no-backup", action="store_true",
                        help="(uninstall) Remove without backup")

    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
    elif args.command == "clean":
        cmd_clean(args.yes)
    elif args.command == "update":
        cmd_update(args.yes)
    elif args.command == "status":
        cmd_status()
    elif args.command == "uninstall":
        cmd_uninstall(args.yes, args.no_backup)


if __name__ == "__main__":
    main()
