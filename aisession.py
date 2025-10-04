#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Session Management CLI Tool
Based on AI_agent_comm_guidelines.md

Usage:
    python ai_session.py --start [topic]
    python ai_session.py --generate-summary [theme]
    python ai_session.py --help
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


def get_session_start_prompt():
    """Return the session start instructions for AI agents."""
    return """
# AI Agent Session Guidelines

## Communication Preferences:
1. **Be Direct**: No apologies, no praise, no filler language
2. **Action-Oriented**: Do not create scripts/files until explicitly requested
3. **Factual Responses**: State what is, what was done, what's next
4. **No Assumptions**: Ask clarifying questions instead of guessing
5. **Code Focus**: Show code changes, not explanations of obvious things
6. **Error Focus**: When errors occur, state the error and solution only

## Session Rules:
- Wait for explicit "create", "generate", "implement", or "write" commands before generating code
- Do not offer suggestions unless specifically asked
- Keep responses concise and technical
- Use numbered bullet points for clarity
- Only explain complex logic, not basic operations
- No encouragement phrases like "Great!", "Excellent!", "Well done!"

## Current Session Focus:
Please acknowledge these guidelines and wait for the main task.
"""


def get_summary_generation_prompt(theme: Optional[str] = None):
    """Return the prompt for generating an end-of-session summary."""
    today = datetime.now().strftime("%Y%m%d")
    theme_text = theme if theme else "main-theme"
    
    return f"""
Generate an end-of-session markdown summary in /docs following these requirements:

## File Details:
- **Filename**: `docs/{today}-{theme_text}.md`
- **Title**: `{today.replace('20', '').replace('25', '25')}-{theme_text}`

## Required Sections:

### 1. Session Overview
- Date: {datetime.now().strftime("%B %d, %Y")}
- Main theme/focus of this session
- Files modified
- Key objectives achieved

### 2. Problems Encountered
List each error/issue with:
- **Error**: Exact error message or problem description
- **Context**: Where/when it occurred
- **Root Cause**: Why it happened
- **Solution**: How it was resolved
- **Status**: ✓ Resolved / ⚠ Needs follow-up

### 3. Code Changes
For each significant change:
- **File**: path/to/file
- **Change Type**: Added/Modified/Removed
- **Purpose**: Brief technical reason
- **Code Snippet** (if relevant):
```language
key code here
```

### 4. Command Line Actions
List all significant terminal commands executed:
```bash
command executed
# Brief note on purpose/result
```

### 5. Technical Takeaways
- Key learnings for future reference
- Patterns that worked well
- Pitfalls to avoid
- Dependencies or prerequisites discovered

### 6. Next Steps
- Unresolved issues
- Follow-up tasks identified
- Future improvements noted

## Style Requirements:
- ✓ Factual, technical tone
- ✓ Mask all API keys, passwords, sensitive data
- ✓ Include actual error messages and solutions
- ✓ Use code snippets for clarity
- ✗ No praise, encouragement, or filler
- ✗ No "great job" or "well done"
- ✗ No unnecessary explanations

## Format:
Use markdown with proper headers, code blocks, and lists.
Keep it concise but complete - focus on technical facts.

Please create this summary now based on our session.
"""


def get_git_changes() -> Dict[str, List[str]]:
    """Get git changes from current session (unstaged + staged)."""
    try:
        # Get staged changes
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-status'],
            capture_output=True,
            text=True,
            check=True
        )
        staged = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Get unstaged changes
        result = subprocess.run(
            ['git', 'diff', '--name-status'],
            capture_output=True,
            text=True,
            check=True
        )
        unstaged = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Get last commit files if no current changes
        if not staged and not unstaged:
            result = subprocess.run(
                ['git', 'diff', '--name-status', 'HEAD~1', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            staged = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Parse changes
        changes = {'added': [], 'modified': [], 'deleted': []}
        all_lines = staged + unstaged
        
        for line in all_lines:
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) == 2:
                status, filename = parts
                if status.startswith('A'):
                    changes['added'].append(filename)
                elif status.startswith('M'):
                    changes['modified'].append(filename)
                elif status.startswith('D'):
                    changes['deleted'].append(filename)
        
        # Remove duplicates
        changes['added'] = list(set(changes['added']))
        changes['modified'] = list(set(changes['modified']))
        changes['deleted'] = list(set(changes['deleted']))
        
        return changes
    except:
        return {'added': [], 'modified': [], 'deleted': []}


def get_last_commit_message() -> str:
    """Get the last git commit message."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return ""


def create_summary_file(theme: Optional[str] = None, from_notes: Optional[str] = None):
    """Create a summary file with actual session data or from notes file."""
    today = datetime.now().strftime("%Y%m%d")
    theme_display = theme if theme else "main-theme"
    
    # Ensure docs directory exists
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Create filename
    filename = f"{today}-{theme_display}.md"
    filepath = docs_dir / filename
    
    # Generate summary
    date_display = datetime.now().strftime("%B %d, %Y")
    short_date = today.replace('20', '').replace('25', '25')
    
    # Option B: Load from notes file
    if from_notes and Path(from_notes).exists():
        with open(from_notes, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = f"""# {short_date}-{theme_display}

{content}
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print("=" * 70)
        print("SUMMARY CREATED FROM NOTES")
        print("=" * 70)
        print(f"\n Date: {date_display}")
        print(f" Source: {from_notes}")
        print(f" Output: {filepath}\n")
        return
    
    # Option A: Generate from git changes
    changes = get_git_changes()
    last_commit = get_last_commit_message()
    
    # Build files modified section
    files_section = ""
    if changes['added']:
        files_section += "**Added Files**:\n"
        for f in sorted(changes['added']):
            files_section += f"- `{f}`\n"
        files_section += "\n"
    
    if changes['modified']:
        files_section += "**Modified Files**:\n"
        for f in sorted(changes['modified']):
            files_section += f"- `{f}`\n"
        files_section += "\n"
    
    if changes['deleted']:
        files_section += "**Deleted Files**:\n"
        for f in sorted(changes['deleted']):
            files_section += f"- `{f}`\n"
        files_section += "\n"
    
    if not files_section:
        files_section = "- No file changes detected\n"
    
    # Parse commit message for theme
    commit_theme = last_commit.split('\n')[0] if last_commit else theme_display
    
    summary = f"""# {short_date}-{theme_display}

## 1. Session Overview

**Date**: {date_display}

**Main Theme**: {commit_theme}

{files_section}

**Key Objectives Achieved**:
- [Describe main objectives - fill in manually]

## 2. Problems Encountered

### Problem 1: [Title]

- **Error**: [Exact error message or problem description]
- **Context**: [Where/when it occurred]
- **Root Cause**: [Why it happened]
- **Solution**: [How it was resolved]
- **Status**: ✓ Resolved / ⚠ Needs follow-up

## 3. Code Changes

"""
    
    # Add code change sections for each modified file
    if changes['modified']:
        for file in sorted(changes['modified']):
            file_ext = Path(file).suffix
            lang = 'python' if file_ext == '.py' else 'markdown' if file_ext == '.md' else 'text'
            summary += f"""### File: `{file}`

- **Change Type**: Modified
- **Purpose**: [Brief technical reason]
- **Code Snippet**:

```{lang}
# Key changes here
```

"""
    
    if changes['added']:
        for file in sorted(changes['added']):
            file_ext = Path(file).suffix
            lang = 'python' if file_ext == '.py' else 'markdown' if file_ext == '.md' else 'text'
            summary += f"""### File: `{file}`

- **Change Type**: Added
- **Purpose**: [Brief technical reason]
- **Code Snippet**:

```{lang}
# Key code here
```

"""
    
    summary += """
## 4. Command Line Actions

```bash
# [List commands executed during session]
git add -A
git commit -m "..."
git push
```

## 5. Technical Takeaways

**Key Learnings**:
- [Learning 1]
- [Learning 2]

**Patterns That Worked**:
- [Pattern 1]
- [Pattern 2]

**Pitfalls to Avoid**:
- [Pitfall 1]
- [Pitfall 2]

**Dependencies**:
- [Dependency or prerequisite discovered]

## 6. Next Steps

**Unresolved Issues**:
- [Issue 1]

**Follow-up Tasks**:
- [Task 1]
- [Task 2]

**Future Improvements**:
- [Improvement 1]
- [Improvement 2]
"""
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("=" * 70)
    print("SUMMARY FILE CREATED")
    print("=" * 70)
    print(f"\n Date: {date_display}")
    print(f" File: {filepath}\n")
    print("-" * 70)
    print("Auto-populated data:")
    print(f"  Main Theme: {commit_theme}")
    print(f"  Files Added: {len(changes['added'])}")
    print(f"  Files Modified: {len(changes['modified'])}")
    print(f"  Files Deleted: {len(changes['deleted'])}")
    print("-" * 70)
    print(f"\n Created: {filepath}")
    print(" Status: Review and fill in [placeholders]\n")


def display_start_instructions(topic: Optional[str] = None):
    """Display session start instructions."""
    print("=" * 70)
    print("AI AGENT SESSION START")
    print("=" * 70)
    
    if topic:
        print(f"\n📋 Session Topic: {topic}\n")
    
    print("Copy the text below and paste it to start your AI session:\n")
    print("-" * 70)
    print(get_session_start_prompt())
    print("-" * 70)
    
    if topic:
        print(f"\nThen follow with:\n")
        print(f"# Session Topic: {topic}")
        print("- Focus: [Describe the specific focus]")
        print("- Goal: [State the objective]")
        print("- Files: [List relevant files]")
    
    print("\n✓ Instructions copied above. Paste into your AI chat to begin.\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Session Management Tool - Based on AI_agent_comm_guidelines.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python aisession.py --start
  python aisession.py --start "Refactor Pipeline Logging"
  python aisession.py --generate-summary
  python aisession.py --generate-summary "emoji-removal-log-cleanup"
  
Based on: docs/AI_agent_comm_guidelines.md
        """
    )
    
    parser.add_argument(
        '--start',
        nargs='?',
        const=True,
        metavar='TOPIC',
        help='Start a new AI session with guidelines. Optional: specify session topic.'
    )
    
    parser.add_argument(
        '--generate-summary',
        nargs='?',
        const=True,
        metavar='THEME',
        help='Generate end-of-session summary with git changes. Optional: specify theme for filename.'
    )
    
    parser.add_argument(
        '--from-notes',
        type=str,
        metavar='FILE',
        help='Generate summary from notes file (use with --generate-summary).'
    )
    
    args = parser.parse_args()
    
    # Check if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Handle --start
    if args.start is not None:
        topic = args.start if isinstance(args.start, str) else None
        display_start_instructions(topic)
    
    # Handle --generate-summary
    elif args.generate_summary is not None:
        theme = args.generate_summary if isinstance(args.generate_summary, str) else None
        from_notes = args.from_notes if hasattr(args, 'from_notes') else None
        create_summary_file(theme, from_notes)


if __name__ == '__main__':
    main()
