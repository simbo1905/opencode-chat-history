# Opencode Chat History

Tooling for mining and exploring local `opencode` session history from the SQLite database.

## Usage

```bash
# List recent sessions
uv run opencode_chat_history/miner.py --list

# Rollout a specific session
uv run opencode_chat_history/miner.py --session <SESSION_ID>
```

## Structure

- `opencode_chat_history/miner.py`: Main CLI tool (Python + `uv`).
- `opencode_chat_history/skills/SKILL.md`: Context7/Opencode skill definition for session mining.
