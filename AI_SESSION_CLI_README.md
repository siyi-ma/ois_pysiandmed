# AI Session Management CLI Tool

Command-line tool for managing AI agent sessions based on `AI_agent_comm_guidelines.md`.

## Purpose

This tool helps you:
1. Start AI sessions with consistent communication guidelines
2. Generate end-of-session technical summaries
3. Enforce direct, factual communication (no praise/filler)

## Installation

No installation needed. The script is standalone Python.

## Usage

### Start a New AI Session

```bash
# Start with default guidelines
python ai_session.py --start

# Start with a specific topic
python ai_session.py --start "Pipeline Logging Refactor"
```

**Output**: Displays formatted text to copy/paste into your AI chat that:
- Sets communication preferences (no praise, no assumptions)
- Enforces action-oriented behavior (wait for explicit commands)
- Establishes session rules (factual, concise, technical)

### Generate End-of-Session Summary

```bash
# Generate summary with default theme
python ai_session.py --generate-summary

# Generate summary with specific theme
python ai_session.py --generate-summary "emoji-removal-log-cleanup"
```

**Output**: Creates a markdown file in `docs/[YYYYMMDD]-[theme].md` with:
- Pre-filled template with all required sections
- Ready-to-edit structure (overview, problems, solutions, takeaways)
- Proper markdown formatting with code blocks and lists

**Example**: 
```bash
python ai_session.py --generate-summary "cli-feature"
# Creates: docs/20251002-cli-feature.md
```

## Communication Preferences Enforced

When you use `--start`, the AI agent will:
- ✓ Be direct and factual
- ✓ Wait for explicit "create" or "implement" commands
- ✓ Avoid apologies and praise
- ✓ Ask clarifying questions instead of guessing
- ✓ Focus on code changes, not obvious explanations

## Summary Format

When you use `--generate-summary`, a markdown file is created in `docs/` with:

```markdown
# [YYYYMMDD]-[theme]

## 1. Session Overview
- Date, main theme, files modified, objectives achieved

## 2. Problems Encountered
- Error messages, context, root causes, solutions, status

## 3. Code Changes
- Files modified with change types, purposes, code snippets

## 4. Command Line Actions
- Terminal commands executed with results

## 5. Technical Takeaways
- Key learnings, patterns that worked, pitfalls to avoid, dependencies

## 6. Next Steps
- Unresolved issues, follow-up tasks, future improvements
```

**Template Placeholders**: All sections include `[placeholder text]` for you to fill in.

## Examples

### Example 1: Starting a Pipeline Refactor Session

```bash
python ai_session.py --start "Remove Emoji Icons from Pipeline"
```

Copy the output and paste into your AI chat. Then specify:
```
# Session Topic: Remove Emoji Icons from Pipeline
- Focus: Clean up log messages in pipeline.py
- Goal: Remove all emoji icons and shorten verbose messages
- Files: pipeline.py, README.md
```

### Example 2: Generating a Summary

After your session, run:
```bash
python ai_session.py --generate-summary "emoji-removal-log-cleanup"
```

Copy the output and paste into your AI chat. The AI will create:
`docs/20251002-emoji-removal-log-cleanup.md`

## Benefits

- **Consistency**: Same communication style across sessions
- **Efficiency**: No time wasted on apologies or praise
- **Documentation**: Structured, factual summaries for future reference
- **Clarity**: Direct technical communication only

## Tips

1. **Always start sessions with `--start`** to set expectations
2. **Use descriptive themes** for summaries (e.g., "database-migration-fix")
3. **Keep the output handy** - copy and use it at the beginning of each AI conversation
4. **Generate summaries regularly** - document as you go, not just at the end

## Based On

- `docs/AI_agent_comm_guidelines.md` - Communication guidelines for AI agents
- Created: October 2, 2025

---

**Note**: This tool doesn't interact with AI directly. It generates prompts for you to copy/paste into your AI chat interface.
