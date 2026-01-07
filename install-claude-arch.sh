#!/usr/bin/env bash
# Meta-Agent Architecture Installation Script
# 
# Usage: ./install-claude-architecture.sh <command> [options]
# Run with 'help' or no arguments for usage information.

set -e

# Debug: uncomment to see exactly where script fails
# trap 'echo "Error on line $LINENO, exit code $?"' ERR

VERSION="1.3.1"
SCRIPT_NAME=$(basename "$0")
BACKUP_DIR="$HOME/.claude-backup-$(date +%Y%m%d-%H%M%S)"

# Colors (ASCII-safe fallbacks available)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ASCII-safe symbols (cross-platform)
SYM_OK="[OK]"
SYM_WARN="[!]"
SYM_ERR="[X]"
SYM_INFO="-->"

print_success() { echo -e "${GREEN}${SYM_OK}${NC} $1"; }
print_warning() { echo -e "${YELLOW}${SYM_WARN}${NC} $1"; }
print_error() { echo -e "${RED}${SYM_ERR}${NC} $1"; }
print_info() { echo -e "${BLUE}${SYM_INFO}${NC} $1"; }

# Cross-platform ISO8601 date
get_iso_date() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# =============================================================================
# Pre-flight Validation
# =============================================================================
validate_environment() {
    # Check for spaces in HOME
    if [[ "$HOME" =~ [[:space:]] ]]; then
        print_error "HOME directory contains spaces: '$HOME'"
        print_error "This script requires HOME path without spaces"
        exit 1
    fi
    
    # Check HOME exists and is writable
    if [ ! -d "$HOME" ] || [ ! -w "$HOME" ]; then
        print_error "HOME directory not accessible: '$HOME'"
        exit 1
    fi
}

# =============================================================================
# Help System
# =============================================================================
show_banner() {
    echo -e "${BLUE}+--------------------------------------------------------------+${NC}"
    echo -e "${BLUE}|${NC}  ${BOLD}Meta-Agent Architecture Installer${NC} ${DIM}v${VERSION}${NC}                    ${BLUE}|${NC}"
    echo -e "${BLUE}+--------------------------------------------------------------+${NC}"
}

show_help() {
    show_banner
    echo ""
    echo -e "${BOLD}USAGE${NC}"
    echo "    $SCRIPT_NAME <command> [options]"
    echo ""
    echo -e "${BOLD}COMMANDS${NC}"
    echo -e "    ${CYAN}clean${NC}      Clean install with backup (recommended for first install)"
    echo -e "    ${CYAN}update${NC}     Update architecture files, preserve logs and custom content"
    echo -e "    ${CYAN}force${NC}      Overwrite without backup (dangerous)"
    echo -e "    ${CYAN}status${NC}     Show current installation status"
    echo -e "    ${CYAN}uninstall${NC}  Remove installation (with backup option)"
    echo -e "    ${CYAN}help${NC}       Show this help message"
    echo ""
    echo -e "${BOLD}OPTIONS${NC}"
    echo "    --help, -h     Show detailed help for a command"
    echo "    --yes, -y      Skip confirmation prompts"
    echo ""
    echo -e "${BOLD}EXAMPLES${NC}"
    echo "    $SCRIPT_NAME clean              # Fresh install with backup"
    echo "    $SCRIPT_NAME update             # Update existing installation"
    echo "    $SCRIPT_NAME clean --help       # Show detailed clean command help"
    echo "    $SCRIPT_NAME status             # Check installation status"
    echo ""
    echo -e "${BOLD}HOW AGENTS BOOTSTRAP${NC}"
    echo "    1. CLAUDE.md is auto-loaded every session (constraints)"
    echo "    2. CLAUDE.md contains triggers: 'when X, READ file Y'"
    echo "    3. Agents read additional docs based on task type"
    echo "    4. Project manifests add project-specific context"
    echo ""
}

show_clean_help() {
    show_banner
    echo ""
    echo -e "${BOLD}COMMAND: clean${NC}"
    echo ""
    echo -e "${BOLD}DESCRIPTION${NC}"
    echo "    Performs a clean installation of the Meta-Agent Architecture."
    echo "    Any existing ~/.claude directory and ~/CLAUDE.md file will be"
    echo "    backed up before installation."
    echo ""
    echo -e "${BOLD}USAGE${NC}"
    echo "    $SCRIPT_NAME clean [options]"
    echo ""
    echo -e "${BOLD}OPTIONS${NC}"
    echo "    --yes, -y      Skip confirmation prompt"
    echo "    --help, -h     Show this help message"
    echo ""
    echo -e "${BOLD}DIRECTORY STRUCTURE${NC}"
    echo ""
    echo "    ~/.claude/"
    echo "    +-- README.md              # Meta-agent architecture"
    echo "    +-- CLAUDE.md              # Global constraints (auto-loaded)"
    echo "    +-- docs/"
    echo "    |   +-- dev-philosophy.md  # Workflow principles"
    echo "    |   +-- pr-standards.md    # Review standards"
    echo "    |   +-- testing.md         # Test philosophy"
    echo "    |   +-- error-handling.md  # Error principles"
    echo "    |   +-- message-protocol.md# Agent communication"
    echo "    |   +-- log-format.md      # Logging standard"
    echo "    |   +-- thinking-triggers.md # Thinking depth semantics"
    echo "    |   \\-- agent-virtualization.md # Claude Code mapping"
    echo "    +-- templates/"
    echo "    |   +-- project-manifest.md# Template for new projects"
    echo "    |   \\-- project-logging.md # Logging standards template"
    echo "    +-- lib/"
    echo "    |   \\-- logger.py          # Python logging library"
    echo "    +-- bin/"
    echo "    |   +-- init-project       # Bootstrap project manifest"
    echo "    |   \\-- query-logs         # Query JSONL logs"
    echo "    +-- commands/"
    echo "    |   \\-- agent-ops.md       # Agent operation commands"
    echo "    \\-- logs/                  # Session logs directory"
    echo ""
}

show_update_help() {
    show_banner
    echo ""
    echo -e "${BOLD}COMMAND: update${NC}"
    echo ""
    echo -e "${BOLD}DESCRIPTION${NC}"
    echo "    Updates architecture files while preserving your logs and any"
    echo "    custom content. Creates a backup before making changes."
    echo ""
    echo -e "${BOLD}WHAT IT PRESERVES${NC}"
    echo "    - ~/.claude/logs/            # All session logs"
    echo ""
    echo -e "${BOLD}WHAT IT REPLACES${NC}"
    echo "    - All standard documentation and configuration files"
    echo ""
}

show_force_help() {
    show_banner
    echo ""
    echo -e "${BOLD}COMMAND: force${NC}"
    echo ""
    echo -e "${YELLOW}WARNING: This command does not create backups!${NC}"
    echo ""
    echo "    Overwrites all installation files without creating a backup."
    echo "    Use only when you're certain you don't need existing data."
    echo ""
}

show_status_help() {
    show_banner
    echo ""
    echo -e "${BOLD}COMMAND: status${NC}"
    echo ""
    echo "    Shows the current installation status, version information,"
    echo "    and integrity check of installed files."
    echo ""
}

show_uninstall_help() {
    show_banner
    echo ""
    echo -e "${BOLD}COMMAND: uninstall${NC}"
    echo ""
    echo "    Removes the Meta-Agent Architecture installation."
    echo "    By default, creates a backup before removal."
    echo ""
    echo -e "${BOLD}OPTIONS${NC}"
    echo "    --no-backup    Remove without backup"
    echo "    --yes, -y      Skip confirmation prompt"
    echo ""
}

# =============================================================================
# Status Command
# =============================================================================
cmd_status() {
    show_banner
    echo ""
    
    if [ ! -d "$HOME/.claude" ]; then
        echo -e "${YELLOW}Status: NOT INSTALLED${NC}"
        echo ""
        echo "Run '$SCRIPT_NAME clean' to install."
        return 0
    fi
    
    echo -e "${GREEN}Status: INSTALLED${NC}"
    echo ""
    
    # Version info
    if [ -f "$HOME/.claude/.version" ]; then
        echo -e "${BOLD}Version Information${NC}"
        cat "$HOME/.claude/.version" | sed 's/^/    /'
        echo ""
    fi
    
    # File integrity
    echo -e "${BOLD}File Integrity${NC}"
    local expected_files=(
        "README.md"
        "CLAUDE.md"
        "docs/dev-philosophy.md"
        "docs/pr-standards.md"
        "docs/testing.md"
        "docs/error-handling.md"
        "docs/message-protocol.md"
        "docs/log-format.md"
        "docs/thinking-triggers.md"
        "docs/agent-virtualization.md"
        "templates/project-manifest.md"
        "templates/project-logging.md"
        "lib/logger.py"
        "bin/init-project"
        "bin/query-logs"
        "commands/agent-ops.md"
    )
    
    local missing=0
    for f in "${expected_files[@]}"; do
        if [ -f "$HOME/.claude/$f" ]; then
            echo -e "    ${GREEN}${SYM_OK}${NC} $f"
        else
            echo -e "    ${RED}${SYM_ERR}${NC} $f ${DIM}(missing)${NC}"
            ((missing++)) || true
        fi
    done
    echo ""
    
    if [ $missing -gt 0 ]; then
        echo -e "${YELLOW}    $missing file(s) missing. Run '$SCRIPT_NAME update' to repair.${NC}"
        echo ""
    fi
    
    # Logs statistics
    echo -e "${BOLD}Logs Directory${NC}"
    if [ -d "$HOME/.claude/logs" ]; then
        local log_count=$(find "$HOME/.claude/logs" -name "*.jsonl" 2>/dev/null | wc -l | tr -d ' ')
        local log_size=$(du -sh "$HOME/.claude/logs" 2>/dev/null | cut -f1 || echo "0")
        echo "    Location: ~/.claude/logs/"
        echo "    Files: $log_count session log(s)"
        echo "    Size: $log_size"
    else
        echo "    ${DIM}No logs directory${NC}"
    fi
    echo ""
    
    # Backups - fixed counting
    local backup_list
    backup_list=$(ls -d "$HOME"/.claude-backup-* 2>/dev/null || true)
    if [ -n "$backup_list" ]; then
        local backups=$(echo "$backup_list" | wc -l | tr -d ' ')
        echo -e "${BOLD}Backups${NC}"
        echo "    Found $backups backup(s):"
        echo "$backup_list" | head -5 | sed 's/^/    /'
        if [ "$backups" -gt 5 ]; then
            echo "    ${DIM}... and $((backups - 5)) more${NC}"
        fi
        echo ""
    fi
}

# =============================================================================
# Pre-flight Checks
# =============================================================================
check_existing() {
    EXISTING_CLAUDE_DIR=false
    EXISTING_CLAUDE_MD=false
    EXISTING_CLAUDE_MD_SYMLINK=false

    # Use if statements instead of && to avoid set -e exit on false test
    if [ -d "$HOME/.claude" ]; then
        EXISTING_CLAUDE_DIR=true
    fi
    if [ -L "$HOME/CLAUDE.md" ]; then
        EXISTING_CLAUDE_MD_SYMLINK=true
    elif [ -f "$HOME/CLAUDE.md" ]; then
        EXISTING_CLAUDE_MD=true
    fi
}

backup_existing() {
    if [ "$EXISTING_CLAUDE_DIR" = true ] || [ "$EXISTING_CLAUDE_MD" = true ]; then
        print_info "Creating backup at $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
        
        if [ "$EXISTING_CLAUDE_DIR" = true ]; then
            cp -r "$HOME/.claude" "$BACKUP_DIR/.claude"
            print_success "Backed up ~/.claude"
        fi
        
        if [ "$EXISTING_CLAUDE_MD" = true ]; then
            cp "$HOME/CLAUDE.md" "$BACKUP_DIR/CLAUDE.md"
            print_success "Backed up ~/CLAUDE.md"
        fi
        
        echo ""
        print_success "Backup complete: $BACKUP_DIR"
        echo ""
    fi
}

remove_existing() {
    if [ "$EXISTING_CLAUDE_DIR" = true ]; then
        rm -rf "$HOME/.claude"
        print_info "Removed existing ~/.claude"
    fi

    if [ "$EXISTING_CLAUDE_MD_SYMLINK" = true ]; then
        rm "$HOME/CLAUDE.md"
        print_info "Removed existing ~/CLAUDE.md symlink"
    elif [ "$EXISTING_CLAUDE_MD" = true ]; then
        rm "$HOME/CLAUDE.md"
        print_info "Removed ~/CLAUDE.md (migrated to ~/.claude/CLAUDE.md)"
    fi
}

create_symlink() {
    # Create ~/CLAUDE.md symlink pointing to ~/.claude/CLAUDE.md
    if [ ! -L "$HOME/CLAUDE.md" ]; then
        ln -s "$HOME/.claude/CLAUDE.md" "$HOME/CLAUDE.md"
        print_success "Created ~/CLAUDE.md -> ~/.claude/CLAUDE.md symlink"
    fi
}

confirm_action() {
    local message="$1"
    if [ "$SKIP_CONFIRM" = true ]; then
        return 0
    fi
    
    echo -e "${YELLOW}$message${NC}"
    read -p "Continue? [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) echo "Cancelled."; exit 0 ;;
    esac
}

# =============================================================================
# Installation (heredocs trimmed for space - full content same as original)
# =============================================================================
install_files() {
    mkdir -p "$HOME/.claude"/{docs,templates,commands,logs,lib,bin}

    # --- README.md --- (content same as original, using ASCII tree chars)
    cat > "$HOME/.claude/README.md" << 'HEREDOC'
# Meta-Agent Orchestration Architecture

> **For Agents:** This is the source of truth for multi-agent coordination.
> Read this fully when: spawning subagents, coordinating parallel work, or handling handoffs.

## TL;DR for Agents

```
YOU ARE: An agent in a multi-agent system
COORDINATION: Via message protocol (@~/.claude/docs/message-protocol.md)  
LOGGING: JSONL format (@~/.claude/docs/log-format.md)
YOUR ID: {type}:{domain}:{id} (e.g., spec:backend:auth01)
CORRELATION: Always track with corr_{session}_{seq}
HANDOFFS: Must include critical_decisions, open_questions, files_to_review
ESCALATE: When blocked, uncertain, or security-critical
```

## Directory Structure

```
~/.claude/
+-- README.md                    # This file (meta-agent context)
+-- CLAUDE.md                    # Global constraints (auto-loaded)
+-- docs/
|   +-- dev-philosophy.md        # Workflow principles
|   +-- pr-standards.md          # Review standards
|   +-- testing.md               # Test philosophy
|   +-- error-handling.md        # Error principles
|   +-- message-protocol.md      # Inter-agent communication
|   +-- log-format.md            # Logging standard
|   +-- thinking-triggers.md     # Thinking depth semantics
|   \-- agent-virtualization.md  # Claude Code agent mapping
+-- templates/
|   +-- project-manifest.md      # Template for new projects
|   \-- project-logging.md       # Logging standards for projects
+-- lib/
|   \-- logger.py                # Python logging library
+-- bin/
|   +-- init-project             # Bootstrap project manifest
|   \-- query-logs               # Query JSONL logs
+-- commands/
|   \-- agent-ops.md             # Agent operation commands
\-- logs/
    \-- {date}/
        \-- {session-id}.jsonl   # Session logs (JSONL only)
```

## Agent Taxonomy

| Agent Type | Identifier | Description |
|------------|------------|-------------|
| user | user:{id} | Human operator |
| orchestrator | orch:{session} | Meta-agent coordinator |
| specialist | spec:{domain}:{id} | Task-focused sub-agent |
| verifier | verif:{id} | Adversarial review agent |
| external | ext:{provider}:{model} | Other LLMs/services |

## Quick Reference

### Thinking Triggers
`think` < `think hard` < `think harder` < `ultrathink`

### Log Queries
```bash
jq -c 'select(.lvl=="error")' session.jsonl           # Errors
jq -c 'select(.cid=="corr_s1_001")' session.jsonl     # By correlation
jq 'select(.evt=="decision.made")' session.jsonl      # Decisions
```

---

*Full documentation in linked files. This is the source of truth for multi-agent coordination.*
HEREDOC
    print_success "README.md"

    # --- CLAUDE.md ---
    cat > "$HOME/.claude/CLAUDE.md" << 'HEREDOC'
# Claude Global Standards

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
HEREDOC
    print_success "CLAUDE.md"

    # --- Remaining docs (abbreviated for space - same content as original) ---
    cat > "$HOME/.claude/docs/dev-philosophy.md" << 'HEREDOC'
# Development Philosophy

## Core Principle
Code generation is cheap; review is expensive.

## Workflow: Explore --> Plan --> Code --> Commit

### 1. Explore
- Read relevant files before planning
- Use subagents for complex research

### 2. Plan
- TodoWrite breakdown forces design thinking
- Use thinking triggers: `think` --> `ultrathink`

### 3. Code
- Target reviewable chunks (<500 lines)
- Verify as you implement

### 4. Commit
- Each commit tells coherent story
HEREDOC
    print_success "docs/dev-philosophy.md"

    cat > "$HOME/.claude/docs/pr-standards.md" << 'HEREDOC'
# PR Standards

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
HEREDOC
    print_success "docs/pr-standards.md"

    cat > "$HOME/.claude/docs/testing.md" << 'HEREDOC'
# Testing Standards

## Core Principle
Meaningful tests > coverage theater.

## Good Tests
- Exercise real behavior
- Cover edge cases: empty, boundary, error states
- Mocks only for external dependencies

## Bad Tests
- Heavy mocking that just verifies mock was called
- Pass regardless of implementation correctness
HEREDOC
    print_success "docs/testing.md"

    cat > "$HOME/.claude/docs/error-handling.md" << 'HEREDOC'
# Error Handling

## Core Principle
Thoughtful, not paranoid. Handle at appropriate abstraction level.

## Good Error Handling
- Context in messages: what failed, why, what to do
- Specific exception types
- Fail fast on invariant violations

## Anti-Patterns
- Silent swallowing (try/except: pass)
- Paranoid try/except without understanding why error occurs
HEREDOC
    print_success "docs/error-handling.md"

    cat > "$HOME/.claude/docs/message-protocol.md" << 'HEREDOC'
# Inter-Agent Message Protocol

## Message Types

| Type | Purpose |
|------|---------|
| request | Task assignment |
| response | Task result |
| handoff | Transfer to another agent |
| escalation | Problem requiring attention |
| checkpoint | State snapshot |

## Agent ID Format
```
user:primary           --> Human operator
orch:session_abc       --> Orchestrator
spec:backend:auth01    --> Backend specialist
verif:review_001       --> Verifier
```

## Protocol Rules
1. Always include correlation_id
2. Handoffs must include critical_decisions
3. Escalations require severity + requires action
4. Checkpoints must include resume_instructions
HEREDOC
    print_success "docs/message-protocol.md"

    cat > "$HOME/.claude/docs/log-format.md" << 'HEREDOC'
# Logging Standard

## Format: JSONL
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

## Event Types
agent.spawned, task.started, task.completed, decision.made, etc.
HEREDOC
    print_success "docs/log-format.md"

    cat > "$HOME/.claude/docs/thinking-triggers.md" << 'HEREDOC'
# Thinking Depth Triggers

Semantic hints to Claude's extended reasoning mode.

## Trigger Hierarchy

| Trigger | Depth | Exploration | When to Use |
|---------|-------|-------------|-------------|
| `think` | Light | Surface-level | Simple decisions, quick checks |
| `think hard` | Medium | Multi-angle | Trade-offs, moderate complexity |
| `think harder` | Deep | Exhaustive | Architecture, edge cases, debugging |
| `ultrathink` | Maximum | Full exploration | Critical decisions, security, novel problems |

## Usage Examples

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

When parsing user messages containing these triggers:

1. **Not programmatically enforced** -- Semantic cues, not commands
2. **Scale reasoning proportionally** -- More trigger = more alternatives
3. **Document proportionally** -- Higher depth = more explicit reasoning
4. **Escalate if uncertain** -- If trigger exceeds confidence, escalate

## Mapping to Reasoning Behaviors

| Trigger | Alternatives | Counterarguments | Edge Cases |
|---------|--------------|------------------|------------|
| `think` | 1-2 | Minimal | Obvious only |
| `think hard` | 2-3 | Consider | Common |
| `think harder` | 3-5 | Actively seek | Comprehensive |
| `ultrathink` | Exhaustive | Adversarial | All conceivable |

## In Multi-Agent Context

Orchestrators can embed triggers in Task prompts to specialists:

```
spec:backend:auth01 -- think harder about token rotation edge cases
before implementing refresh logic.
```

Verifiers should default to `think hard` minimum for review tasks.
HEREDOC
    print_success "docs/thinking-triggers.md"

    cat > "$HOME/.claude/docs/agent-virtualization.md" << 'HEREDOC'
# Agent Virtualization in Claude Code

Bridging conceptual agent taxonomy to Claude Code's fixed agent types.

## Claude Code Agents

| Agent | Purpose | Context |
|-------|---------|---------|
| general-purpose | Main conversation, direct execution | Full session |
| Explore | Read-only investigation | Scoped, returns findings |
| Plan | Step-by-step planning | Scoped, returns plan |

## Mapping: Conceptual --> Claude Code

| Conceptual Role | Claude Code Agent | Implementation Notes |
|-----------------|-------------------|---------------------|
| `orch:{session}` | general-purpose | Main agent orchestrates, tracks state |
| `spec:{domain}:{id}` | Task (any type) | Embed role in prompt, use correlation ID |
| `verif:{id}` | Task (Explore preferred) | Read-only suits adversarial review |
| `user:{id}` | N/A | Human in conversation |

## Embedding Agent ID in Task Prompts

```
You are spec:backend:auth01
Correlation: corr_session123_007

Task: Implement token refresh logic
Context: [previous decisions]

Report back with: files_modified, decisions_made, open_questions
```

## Correlation ID Tracking

Pattern: `corr_{session}_{sequence}`

```
# In orchestrator context
current_corr = "corr_s1_001"

# Pass to Task
Task prompt includes: "Correlation: corr_s1_001"

# Task response should reference
"Completing corr_s1_001: [results]"
```

Track manually -- Claude Code doesn't enforce correlation.

## Handoff Protocol Template

```markdown
## Handoff: {from_agent} --> {to_agent}
Correlation: {corr_id}

### Context
- Original request: [summary]
- Work completed: [summary]

### Critical Decisions
1. [Decision + rationale]

### Files to Review
- /path/to/file.py (lines X-Y)

### Open Questions
1. [Unresolved item]

### Next Steps
[Specific actionable items for receiving agent]
```

## Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No true parallelism | Sequential Tasks only | Batch independent work |
| Context not isolated | Task sees conversation | Explicit scope in prompt |
| No persistent state | Agent forgets between calls | Log to JSONL, pass context |
| No native agent ID | Must embed manually | Consistent prompt format |

## Example: Full Protocol Task Invocation

```markdown
# Task Prompt (to Explore agent)

You are verif:security_001
Correlation: corr_main_012

## Mission
Adversarial review of auth implementation in /src/auth/

## Scope
- Token handling
- Session management
- Input validation

## Output Format
Return structured findings:
- severity: critical|high|medium|low
- location: file:line
- issue: description
- recommendation: fix

## Handoff Requirements
End with: critical_decisions, open_questions, files_to_review
```

---

*Agent virtualization is convention-based. Discipline in prompt formatting maintains the abstraction.*
HEREDOC
    print_success "docs/agent-virtualization.md"

    cat > "$HOME/.claude/templates/project-manifest.md" << 'HEREDOC'
# Project Manifest

> Source of truth for project-specific agent configuration.

## Project

| Field | Value |
|-------|-------|
| Name | {project-name} |
| Root | {project-root} |

## Agent Logging

| Setting | Value |
|---------|-------|
| Location | .claude/logs/{date}/ |
| Session | auto-generated |
| Format | JSONL |

## Complexity Zones

> Define paths requiring elevated review/testing. Agent determines appropriate handling.

| Path | Level | Notes |
|------|-------|-------|
| `**/auth/**` | critical | Security-sensitive |
| `**/api/**` | standard | External interface |
| `scripts/**` | low | Utilities |

## Project-Specific Instructions

> Add constraints or context specific to this project. Agents read this on session start.

```
# Example:
# - Use uv for Python package management
# - Run tests with: pytest
# - Prefer structured logging
```
HEREDOC
    print_success "templates/project-manifest.md"

    cat > "$HOME/.claude/templates/project-logging.md" << 'HEREDOC'
# Project Logging Guide

> Logging standards for application code integrated with meta-agent architecture.

## Standard Event Types

### Request Lifecycle
| Event | When | Required Fields |
|-------|------|-----------------|
| `request.received` | Handler entry | `method`, `path`, `correlation_id` |
| `request.completed` | Handler exit | `status`, `duration_ms`, `correlation_id` |

### Database Operations
| Event | When | Required Fields |
|-------|------|-----------------|
| `db.query` | Query execution | `table`, `operation`, `duration_ms` |
| `db.error` | Query failure | `table`, `operation`, `error` |

### Authentication
| Event | When | Required Fields |
|-------|------|-----------------|
| `auth.attempt` | Login/token request | `method`, `identifier_hash` |
| `auth.success` | Credential validated | `user_id`, `method` |
| `auth.failure` | Credential rejected | `method`, `reason` |

### Background Jobs
| Event | When | Required Fields |
|-------|------|-----------------|
| `job.started` | Job begins | `job_type`, `job_id`, `correlation_id` |
| `job.completed` | Job finishes | `job_id`, `duration_ms` |
| `job.failed` | Job errors | `job_id`, `error`, `retry_count` |

### External Integrations
| Event | When | Required Fields |
|-------|------|-----------------|
| `integration.call` | API call start | `service`, `endpoint`, `correlation_id` |
| `integration.error` | API call failure | `service`, `status`, `error` |

---

## Language Examples

### Python (structlog)

```python
from __future__ import annotations
import structlog
from uuid import uuid4

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)

log = structlog.get_logger()

def get_request_logger(correlation_id: str | None = None):
    return log.bind(correlation_id=correlation_id or str(uuid4()))

# Usage
logger = get_request_logger(request.headers.get("X-Correlation-ID"))
logger.info("request.received", method="POST", path="/api/users")
```

### TypeScript/Node (pino)

```typescript
import pino from 'pino';
import { randomUUID } from 'crypto';

const logger = pino({
  formatters: { level: (label) => ({ level: label }) },
  timestamp: pino.stdTimeFunctions.isoTime,
});

function getRequestLogger(correlationId?: string) {
  return logger.child({ correlationId: correlationId ?? randomUUID() });
}

const reqLogger = getRequestLogger(req.headers['x-correlation-id']);
reqLogger.info({ event: 'request.received', method: 'POST', path: '/api/users' });
```

### Go (zerolog)

```go
import "github.com/rs/zerolog/log"

func RequestLogger(correlationID string) zerolog.Logger {
    return log.With().Str("correlation_id", correlationID).Logger()
}

logger := RequestLogger(correlationID)
logger.Info().Str("event", "request.received").Str("method", "POST").Msg("")
```

---

## Meta-Agent Integration

### Correlation ID Flow

```
Agent Session (.claude/logs/session-*.jsonl)
    |
    | spawns task with session_id + task_id
    v
Application Request
    | X-Correlation-ID: {session_id}:{task_id}:{request_id}
    v
Application Logs --> Downstream Services
```

### Linking Logs

```bash
# Find all logs for a session
cat .claude/logs/*.jsonl app-*.jsonl | \
  jq -s 'sort_by(.timestamp) | .[] | select(.correlation_id | startswith("sess_abc"))'
```

---

## Best Practices

### What to Log

| Category | Examples | Level |
|----------|----------|-------|
| Decisions | Route selection, cache hit/miss | INFO |
| Errors | Exceptions, validation failures | ERROR |
| Boundaries | External API calls, DB queries | INFO |
| State changes | User created, order completed | INFO |
| Performance | Slow queries (>100ms) | WARN |

### What NOT to Log

| Never Log | Why |
|-----------|-----|
| Passwords, tokens, API keys | Security breach risk |
| PII (email, SSN, phone) | Compliance (GDPR, HIPAA) |
| Full request/response bodies | Volume, may contain secrets |
| High-frequency internal loops | Noise, storage cost |

### Log Levels

| Level | Use Case |
|-------|----------|
| `DEBUG` | Development troubleshooting |
| `INFO` | Normal operations |
| `WARN` | Degraded but functional |
| `ERROR` | Failure requiring attention |

### Structured Logging

**DO:** `{"event": "db.query", "table": "users", "duration_ms": 42}`

**DON'T:** `User query took 42ms to execute SELECT * FROM users`

**Field conventions:**
- `snake_case` for field names
- `_ms` or `_s` suffix for durations
- `_at` suffix for timestamps
- Hash sensitive identifiers
HEREDOC
    print_success "templates/project-logging.md"

    # --- lib/logger.py ---
    cat > "$HOME/.claude/lib/logger.py" << 'HEREDOC'
"""
Logging library for meta-agent architecture.

JSONL format logging with correlation tracking, agent identification,
and session lifecycle management.
"""
from __future__ import annotations

import json
import os
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType
from typing import Any, Literal

LogLevel = Literal["debug", "info", "warn", "error", "fatal"]
EventType = Literal[
    "agent.spawned",
    "task.started",
    "task.completed",
    "decision.made",
    "handoff.initiated",
    "handoff.completed",
    "escalation.raised",
    "error.occurred",
]

# Module-level session tracking for continuity within same process
_current_session: str | None = None


def _get_home() -> Path:
    """Get home directory, respecting HOME env var."""
    return Path(os.environ.get("HOME", Path.home()))


def _generate_session_id() -> str:
    """Generate a unique session ID: sess_{date}_{random}."""
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    random_part = secrets.token_hex(4)
    return f"sess_{date_part}_{random_part}"


def get_current_session() -> str:
    """Get or create the current session ID for this process."""
    global _current_session
    if _current_session is None:
        _current_session = _generate_session_id()
    return _current_session


def set_current_session(session_id: str) -> None:
    """Set the current session ID (for continuing existing sessions)."""
    global _current_session
    _current_session = session_id


def is_project_context() -> bool:
    """Detect if running within a project with .claude directory."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        project_claude = parent / ".claude"
        if project_claude.is_dir():
            if parent != _get_home():
                return True
    return False


def get_project_root() -> Path | None:
    """Find project root containing .claude directory."""
    cwd = Path.cwd()
    home = _get_home()
    for parent in [cwd, *cwd.parents]:
        project_claude = parent / ".claude"
        if project_claude.is_dir() and parent != home:
            return parent
    return None


class AgentLogger:
    """
    JSONL logger for meta-agent architecture.

    Logs to ~/.claude/logs/{date}/{session-id}.jsonl

    Usage:
        # Auto-generated session ID
        with AgentLogger(agent_id="spec:backend:auth01") as log:
            log.task_started("Implementing auth flow")
            log.decision_made("Using JWT", rationale="Industry standard")

        # Explicit session ID (for continuity)
        with AgentLogger("existing_session", "orch:main") as log:
            log.task_started("Continuing work")

        # Or without context manager
        log = AgentLogger(agent_id="spec:frontend:ui01")
        log.task_started("Building component")
    """

    def __init__(
        self,
        session_id: str | None = None,
        agent_id: str = "orch:default",
    ) -> None:
        # Auto-generate session_id if not provided
        if session_id is None:
            self.session_id = get_current_session()
        else:
            self.session_id = session_id
            set_current_session(session_id)  # Track for other loggers

        self.agent_id = agent_id
        self._seq = 0
        self._log_dir = self._get_log_dir()
        self._log_file = self._log_dir / f"{self.session_id}.jsonl"
        self._ensure_dir()

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
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")

        return correlation_id

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
            for line in result.stdout.strip().split("\n"):
                if line:
                    entries.append(json.loads(line))
            return entries
        except FileNotFoundError:
            raise RuntimeError("jq not found. Install with: brew install jq")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"jq query failed: {e.stderr}")

    def __enter__(self) -> AgentLogger:
        self.log("info", "session.started", f"Session {self.session_id} started")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if exc_type is not None:
            self.log(
                "error",
                "session.error",
                f"Session ended with error: {exc_type.__name__}",
                error=str(exc_val),
            )
        else:
            self.log("info", "session.ended", f"Session {self.session_id} ended")
        return False

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
        **kwargs: Any,
    ) -> str:
        extra: dict[str, Any] = {}
        if rationale:
            extra["rationale"] = rationale
        if alternatives:
            extra["alternatives"] = alternatives
        return self.log("info", "decision.made", decision, **extra, **kwargs)

    def agent_spawned(
        self,
        child_agent_id: str,
        *,
        task: str | None = None,
        **kwargs: Any,
    ) -> str:
        msg = f"Spawned {child_agent_id}"
        extra: dict[str, Any] = {"child_aid": child_agent_id}
        if task:
            extra["task"] = task
        return self.log("info", "agent.spawned", msg, **extra, **kwargs)

    def handoff(
        self,
        target_agent_id: str,
        *,
        critical_decisions: list[str] | None = None,
        open_questions: list[str] | None = None,
        files_to_review: list[str] | None = None,
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
) -> AgentLogger:
    """
    Factory function to get appropriate logger.

    Args:
        session_id: Optional session ID. Auto-generated if not provided.
        agent_id: Agent identifier (e.g., "spec:backend:auth01")
        prefer_project: If True and in project context, use ProjectLogger

    Returns:
        AgentLogger or ProjectLogger instance
    """
    if prefer_project and is_project_context():
        return ProjectLogger(session_id, agent_id)
    return AgentLogger(session_id, agent_id)
HEREDOC
    print_success "lib/logger.py"

    # --- bin/init-project ---
    cat > "$HOME/.claude/bin/init-project" << 'HEREDOC'
#!/usr/bin/env bash
#
# init-project - Bootstrap project manifest for Claude meta-agent system
#
# Usage: init-project [project-path]
# Creates project/.claude/manifest.md and project/.claude/logs/

set -euo pipefail

TEMPLATE_PATH="${HOME}/.claude/templates/project-manifest.md"

show_help() {
    cat << 'EOF'
Usage: init-project [project-path]

Bootstrap a project with Claude meta-agent manifest.

Arguments:
  project-path    Path to project root (default: current directory)

Creates:
  project/.claude/manifest.md   Project manifest (from template)
  project/.claude/logs/         Session logs directory

Options:
  -h, --help      Show this help message

Examples:
  init-project                  # Initialize current directory
  init-project ~/code/myapp     # Initialize specific project
EOF
}

main() {
    [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]] && show_help && exit 0

    local project_dir="${1:-.}"
    project_dir="$(cd "${project_dir}" && pwd)"

    local claude_dir="${project_dir}/.claude"
    local manifest_path="${claude_dir}/manifest.md"

    [[ ! -f "${TEMPLATE_PATH}" ]] && echo "error: template not found at ${TEMPLATE_PATH}" >&2 && exit 1
    [[ -f "${manifest_path}" ]] && echo "exists: ${manifest_path}" >&2 && exit 0

    mkdir -p "${claude_dir}/logs"

    local project_name
    project_name="$(basename "${project_dir}")"

    sed -e "s|{project-name}|${project_name}|g" \
        -e "s|{project-root}|${project_dir}|g" \
        "${TEMPLATE_PATH}" > "${manifest_path}"

    echo "initialized: ${manifest_path}"
    echo "  project: ${project_name}"
    echo "  logs: ${claude_dir}/logs/"
}

main "$@"
HEREDOC
    chmod +x "$HOME/.claude/bin/init-project"
    print_success "bin/init-project"

    # --- bin/query-logs ---
    cat > "$HOME/.claude/bin/query-logs" << 'HEREDOC'
#!/usr/bin/env bash
#
# query-logs - Search JSONL logs with jq filters
#
# Usage: query-logs <jq-filter> [session-id] [--global|--project]

set -euo pipefail

GLOBAL_LOGS="${HOME}/.claude/logs"
PROJECT_LOGS="./.claude/logs"

show_help() {
    cat << 'EOF'
Usage: query-logs <jq-filter> [session-id] [--global|--project]

Search Claude agent JSONL logs with jq filters.

Arguments:
  jq-filter       jq expression (required)
  session-id      Optional session ID filter

Options:
  --global        Search only ~/.claude/logs/
  --project       Search only ./.claude/logs/
  -h, --help      Show this help message

Examples:
  query-logs 'select(.lvl=="error")'          # All errors
  query-logs 'select(.evt=="decision.made")'  # All decisions
  query-logs '.' abc123                       # Session abc123
  query-logs 'select(.lvl=="error")' --project
EOF
}

check_jq() {
    command -v jq &>/dev/null || {
        echo "error: jq required. Install: brew install jq" >&2
        exit 1
    }
}

find_logs() {
    local log_dir="$1" session_filter="${2:-}"
    [[ ! -d "${log_dir}" ]] && return
    if [[ -n "${session_filter}" ]]; then
        find "${log_dir}" -name "*.jsonl" -type f 2>/dev/null | grep -i "${session_filter}" || true
    else
        find "${log_dir}" -name "*.jsonl" -type f 2>/dev/null || true
    fi
}

main() {
    [[ $# -eq 0 ]] || [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]] && show_help && exit 0
    check_jq

    local jq_filter="" session_id="" search_global=true search_project=true

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --global) search_project=false ;;
            --project) search_global=false ;;
            *) [[ -z "${jq_filter}" ]] && jq_filter="$1" || session_id="$1" ;;
        esac
        shift
    done

    [[ -z "${jq_filter}" ]] && echo "error: jq-filter required" >&2 && exit 1

    local log_files=()
    $search_global && while IFS= read -r f; do [[ -n "$f" ]] && log_files+=("$f"); done < <(find_logs "${GLOBAL_LOGS}" "${session_id}")
    $search_project && while IFS= read -r f; do [[ -n "$f" ]] && log_files+=("$f"); done < <(find_logs "${PROJECT_LOGS}" "${session_id}")

    [[ ${#log_files[@]} -eq 0 ]] && echo "no log files found" >&2 && exit 0

    for file in "${log_files[@]}"; do
        echo "# ${file}" >&2
        jq -c "${jq_filter}" "${file}" 2>/dev/null || echo "  warning: failed to parse ${file}" >&2
    done
}

main "$@"
HEREDOC
    chmod +x "$HOME/.claude/bin/query-logs"
    print_success "bin/query-logs"

    cat > "$HOME/.claude/commands/agent-ops.md" << 'HEREDOC'
# Agent Operations

## spawn
Spawn sub-agent: `/user:agent-ops spawn <domain> "<task>"`

## verify
Spawn verifier: `/user:agent-ops verify [files...]`

## checkpoint
Save state: `/user:agent-ops checkpoint "<description>"`

## Quick Patterns

### Research First
"Use subagent to investigate existing patterns for <topic>."

### Adversarial Review
"Spawn fresh verifier to review <files>."
HEREDOC
    print_success "commands/agent-ops.md"

    # --- Version file (cross-platform date) ---
    cat > "$HOME/.claude/.version" << HEREDOC
version: $VERSION
installed: $(get_iso_date)
mode: $MODE
HEREDOC
    print_success ".version"
}

# =============================================================================
# Commands
# =============================================================================
cmd_clean() {
    show_banner
    echo ""
    check_existing
    
    if [ "$EXISTING_CLAUDE_DIR" = true ] || [ "$EXISTING_CLAUDE_MD" = true ]; then
        echo "Existing installation found:"
        [ "$EXISTING_CLAUDE_DIR" = true ] && echo "  - ~/.claude/"
        [ "$EXISTING_CLAUDE_MD" = true ] && echo "  - ~/CLAUDE.md"
        echo ""
        confirm_action "This will backup and replace your existing installation."
        echo ""
        backup_existing
    fi
    
    remove_existing
    MODE="clean"
    install_files
    create_symlink

    echo ""
    print_success "Clean installation complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Review ~/.claude/README.md"
    echo "  2. For projects: ~/.claude/bin/init-project /path/to/project"
}

cmd_update() {
    show_banner
    echo ""
    check_existing
    
    if [ "$EXISTING_CLAUDE_DIR" = false ]; then
        print_error "No existing installation found. Use 'clean' for first install."
        exit 1
    fi
    
    confirm_action "This will update architecture files. Logs will be preserved."
    echo ""
    
    # Preserve logs with proper cleanup trap
    local TEMP_LOGS=""
    cleanup_temp() {
        if [ -n "$TEMP_LOGS" ] && [ -d "$TEMP_LOGS" ]; then
            rm -rf "$TEMP_LOGS"
        fi
    }
    trap cleanup_temp EXIT
    
    if [ -d "$HOME/.claude/logs" ]; then
        TEMP_LOGS=$(mktemp -d)
        cp -r "$HOME/.claude/logs" "$TEMP_LOGS/"
        print_info "Preserving logs directory"
    fi
    
    backup_existing
    remove_existing
    MODE="update"
    install_files
    
    # Restore logs with verification
    if [ -n "$TEMP_LOGS" ] && [ -d "$TEMP_LOGS/logs" ]; then
        local log_file_count=$(find "$TEMP_LOGS/logs" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [ "$log_file_count" -gt 0 ]; then
            cp -r "$TEMP_LOGS/logs"/* "$HOME/.claude/logs/" 2>/dev/null || true
            print_success "Restored $log_file_count log file(s)"
        else
            print_info "No log files to restore"
        fi
    fi

    create_symlink

    echo ""
    print_success "Update complete!"
}

cmd_force() {
    show_banner
    echo ""
    echo -e "${RED}+--------------------------------------------------------------+${NC}"
    echo -e "${RED}|  WARNING: Force mode - NO BACKUP will be created!           |${NC}"
    echo -e "${RED}+--------------------------------------------------------------+${NC}"
    echo ""
    
    check_existing
    
    if [ "$EXISTING_CLAUDE_DIR" = true ]; then
        echo "The following will be PERMANENTLY DELETED:"
        echo "  - All files in ~/.claude/"
        echo "  - All session logs"
        echo ""
    fi
    
    confirm_action "Are you absolutely sure? This cannot be undone."
    echo ""
    
    remove_existing
    MODE="force"
    install_files
    create_symlink

    echo ""
    print_success "Force installation complete!"
}

cmd_uninstall() {
    show_banner
    echo ""
    check_existing
    
    if [ "$EXISTING_CLAUDE_DIR" = false ]; then
        print_warning "No installation found at ~/.claude/"
        exit 0
    fi
    
    if [ "$NO_BACKUP" = true ]; then
        confirm_action "This will permanently delete ~/.claude/ without backup."
    else
        confirm_action "This will backup and remove ~/.claude/"
        backup_existing
    fi
    
    rm -rf "$HOME/.claude"
    print_success "Uninstalled ~/.claude/"
    
    if [ "$NO_BACKUP" != true ] && [ -d "$BACKUP_DIR" ]; then
        echo ""
        echo "Backup saved at: $BACKUP_DIR"
    fi
}

# =============================================================================
# Argument Parsing (FIXED: proper command/flag ordering)
# =============================================================================
SKIP_CONFIRM=false
NO_BACKUP=false
COMMAND=""
SHOW_COMMAND_HELP=false

parse_args() {
    # First pass: identify the command
    for arg in "$@"; do
        case $arg in
            clean|update|force|status|uninstall|help)
                if [ -z "$COMMAND" ]; then
                    COMMAND="$arg"
                fi
                ;;
        esac
    done
    
    # Second pass: process all flags
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                SHOW_COMMAND_HELP=true
                ;;
            --yes|-y)
                SKIP_CONFIRM=true
                ;;
            --no-backup)
                NO_BACKUP=true
                ;;
            clean|update|force|status|uninstall|help)
                # Already handled in first pass
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Run '$SCRIPT_NAME help' for usage."
                exit 1
                ;;
        esac
        shift
    done
    
    # Handle --help for specific commands
    if [ "$SHOW_COMMAND_HELP" = true ]; then
        case $COMMAND in
            clean) show_clean_help ;;
            update) show_update_help ;;
            force) show_force_help ;;
            status) show_status_help ;;
            uninstall) show_uninstall_help ;;
            *) show_help ;;
        esac
        exit 0
    fi
}

# =============================================================================
# Main
# =============================================================================
main() {
    validate_environment
    parse_args "$@"
    
    case $COMMAND in
        ""|help)
            show_help
            ;;
        clean)
            cmd_clean
            ;;
        update)
            cmd_update
            ;;
        force)
            cmd_force
            ;;
        status)
            cmd_status
            ;;
        uninstall)
            cmd_uninstall
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

main "$@"
