# ⛏️ Opencode Chat History

Mining the vibes of your Opencode sessions since Sunday 17th May 2026. 

Stop scrolling through messy logs! This tool lets you dive deep into your local `opencode.db` and pull out the gold in a format that's ready for training, analysis, or just a nostalgia trip.

## ✨ Features

- **SQLite Heart**: Straight from the source of truth in `~/.local/share/opencode/`.
- **Chat-JSONL Native**: Support for the [Chat-JSONL RFC](./RFC_CHAT_JSONL.md) format. OpenAI-compatible, Mistral-friendly, Hugging Face-ready.
- **Tool-Aware**: It doesn't just pull text; it captures the `tool_calls` and responses in their full glory.

## 🚀 Quick Start

```bash
# Get the tool and its friends
cd /Users/Shared/opencode-chat-history

# 1. See what you've been up to
uv run opencode_chat_history/miner.py --list

# 2. Rollout a session in beautiful Chat-JSONL (default)
uv run opencode_chat_history/miner.py --session <id> --jsonl > session.jsonl
```

## 🛠️ Data Mining with `jq`

Because it's JSONL, you can slice and dice it with standard Unix tools.

```bash
# Extract only the user's questions from a session
grep '"role": "user"' session.jsonl | jq -r '.content'

# Count how many times the assistant used the 'bash' tool
grep '"role": "assistant"' session.jsonl | jq '.tool_calls[].function.name' | grep -c "bash"

# Re-wrap into an API-ready messages array
jq -s '{messages: .}' session.jsonl
```

## 📜 The format

We use **Chat-JSONL**. It's the "OpenAI-won-the-space" format minus the annoying outer wrappers. One line, one message, maximum flexibility.

See the [Full Specification](./RFC_CHAT_JSONL.md).

---
*Stay Flashy.* ⚡
