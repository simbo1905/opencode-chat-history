# Opencode Chat History Skill

This skill allows an agent to explore and mine the local `opencode` session history.

## Environment

The `opencode` TUI stores its state in a SQLite database:
`~/.local/share/opencode/opencode.db`

## Capabilities

- **List Sessions**: Find recent conversation IDs and titles.
- **Rollout Session**: Retrieve the full text and tool interactions of a specific conversation.
- **Analyze Usage**: Extract metrics like token counts and costs from the `session` table.

## Commands

### List Recent Sessions
```bash
uv run /Users/Shared/opencode-chat-history/opencode_chat_history/miner.py --list
```

### Rollout Session History
```bash
uv run /Users/Shared/opencode-chat-history/opencode_chat_history/miner.py --session <id>
```
