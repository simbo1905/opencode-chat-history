---
name: opencode-chat-history
description: Mine and explore local opencode session history from the SQLite database. Use this skill to list recent sessions, roll out full conversation history in Chat-JSONL or text format, and filter output with jq.
---
 
# Opencode Chat History
 
The `opencode` TUI stores all session state in:
`~/.local/share/opencode/opencode.db`
 
The miner script is at:
`/Users/consensussolutions/opencode-chat-history/opencode_chat_history/miner.py`
 
It runs zero-install via `uv run` — no venv or pip needed.
 
## List recent sessions
 
```bash
uv run /Users/consensussolutions/opencode-chat-history/opencode_chat_history/miner.py --list
```
 
Add `--limit N` to see more than the default 20.
 
## Roll out a session as Chat-JSONL (default)
 
OpenAI-compatible, one message per line:
 
```bash
uv run /Users/consensussolutions/opencode-chat-history/opencode_chat_history/miner.py --session <id>
```
 
## Roll out a session as human-readable text
 
```bash
uv run /Users/consensussolutions/opencode-chat-history/opencode_chat_history/miner.py --session <id> --text
```
 
## Save a session to a file
 
```bash
uv run /Users/consensussolutions/opencode-chat-history/opencode_chat_history/miner.py --session <id> > session.jsonl
```
 
## Filter with jq
 
Extract only user messages:
```bash
uv run /Users/consensussolutions/opencode-chat-history/opencode_chat_history/miner.py --session <id> | jq 'select(.role=="user") | .content'
```
 
Count bash tool calls:
```bash
uv run /Users/consensussolutions/opencode-chat-history/opencode_chat_history/miner.py --session <id> | jq 'select(.role=="assistant") | .tool_calls[]?.function.name' | grep -c '"bash"'
```
 
Wrap into an API-ready messages array:
```bash
uv run /Users/consensussolutions/opencode-chat-history/opencode_chat_history/miner.py --session <id> | jq -s '{messages: .}'
```
 
