# RFC 001: Chat-JSONL Format

**Status:** Draft
**Author:** Gemini 3 Flash / simbo1905
**Date:** 2026-05-17

## Abstract

Chat-JSONL is a streamable, append-only format for storing multi-turn conversational AI sessions, including tool use. It adopts the industry-standard OpenAI/Mistral message schema but optimizes for data mining, fine-tuning, and real-time logging by using Newline-Delimited JSON (JSONL).

## Specification

Each line in a Chat-JSONL file MUST be a valid JSON object representing a single message or a complete conversation container.

### 1. Message-Level JSONL (Streamable)
In this mode, each line is one message. This is ideal for real-time session logging.

```json
{"role": "system", "content": "You are helpful."}
{"role": "user", "content": "Hello!"}
{"role": "assistant", "content": "Hi there!"}
```

### 2. Conversation-Level JSONL (Training/Dataset)
In this mode, each line is a complete conversation. This is the standard format for Hugging Face `apply_chat_template` and OpenAI fine-tuning.

```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]}
```

## Schema

Messages follow the OpenAI Chat Completions API vocabulary:

- `role`: "system", "user", "assistant", or "tool".
- `content`: String (or `null` when `tool_calls` is present).
- `tool_calls`: Array of objects (for assistant messages emitting calls).
- `tool_call_id`: String (for tool messages responding to a call).
- `name`: String (function name).

## Design Goals

1. **Grep-ability**: Use `grep` to find specific roles or keywords across millions of sessions.
2. **JQ-friendly**: Easy to transform, filter, and re-wrap.
3. **No Wrapper**: Eliminates the need to parse a giant outer array to get to the data.
4. **Direct to Training**: One line per example makes it ready for most LLM training loaders.
