#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13.0,<3.14"
# dependencies = []
# ///
"""Opencode session history miner. Queries the local opencode.db to list sessions and roll out conversation history."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def format_ts(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')

def get_db_path() -> Path:
    return Path.home() / ".local/share/opencode/opencode.db"

def list_sessions(db: sqlite3.Connection, limit: int = 20):
    cursor = db.cursor()
    query = """
    SELECT id, title, slug, time_created, time_updated
    FROM session
    ORDER BY time_updated DESC
    LIMIT ?
    """
    print(f"{'ID':<38} | {'UPDATED':<19} | {'TITLE'}")
    print("-" * 80)
    for row in cursor.execute(query, (limit,)):
        sid, title, slug, created, updated = row
        print(f"{sid:<38} | {format_ts(updated):<19} | {title}")

def rollout_session(db: sqlite3.Connection, session_id: str, format: str = "text"):
    cursor = db.cursor()
    # Messages in order
    query = """
    SELECT m.id, m.data as msg_data, p.data as part_data
    FROM message m
    JOIN part p ON m.id = p.message_id
    WHERE m.session_id = ?
    ORDER BY m.time_created ASC, p.time_created ASC
    """
    
    current_msg_id = None
    messages = []
    current_msg_obj = None

    for row in cursor.execute(query, (session_id,)):
        mid, msg_json, part_json = row
        msg = json.loads(msg_json)
        part = json.loads(part_json)
        
        if mid != current_msg_id:
            if current_msg_obj:
                messages.append(current_msg_obj)
            
            role = msg.get("role", "unknown")
            current_msg_obj = {"role": role, "content": ""}
            if role == "assistant":
                current_msg_obj["tool_calls"] = []
            
            current_msg_id = mid
        
        ptype = part.get("type")
        if ptype == "text":
            text = part.get("text", "")
            if not part.get("synthetic"):
                if current_msg_obj["content"]:
                    current_msg_obj["content"] += "\n" + text
                else:
                    current_msg_obj["content"] = text
        elif ptype == "tool":
            tool = part.get("tool")
            call_id = part.get("callID")
            input_val = part.get("state", {}).get("input")
            output = part.get("state", {}).get("output")
            
            # Map tool to tool_calls if assistant, or standalone if tool role
            if current_msg_obj["role"] == "assistant":
                current_msg_obj["tool_calls"].append({
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": tool,
                        "arguments": json.dumps(input_val)
                    }
                })
                # If there is output, it usually belongs to a separate 'tool' role message in OpenAI
                # But in Opencode's DB, the part contains both. 
                # We'll need to synthesize the tool response message.
                if output is not None:
                    # We store it to append after the assistant message
                    pass
            
    if current_msg_obj:
        messages.append(current_msg_obj)

    # Secondary pass to expand tool outputs into 'tool' role messages
    final_messages = []
    for m in messages:
        # Check for tool outputs in assistant parts
        # Since our first pass combined parts, let's refine the logic to handle the sequence correctly
        pass

    # REFINED LOGIC for accurate OpenAI sequence:
    current_msg_id = None
    openai_msgs = []
    
    for row in cursor.execute(query, (session_id,)):
        mid, msg_json, part_json = row
        msg = json.loads(msg_json)
        part = json.loads(part_json)
        role = msg.get("role", "unknown")

        if mid != current_msg_id:
            current_msg_id = mid
            if role != "assistant" or not any(m.get("role") == "assistant" and m.get("id") == mid for m in openai_msgs):
                 # New message container
                 pass

        ptype = part.get("type")
        if ptype == "text" and not part.get("synthetic"):
            openai_msgs.append({"role": role, "content": part.get("text", "")})
        elif ptype == "tool":
            call_id = part.get("callID")
            tool = part.get("tool")
            args = part.get("state", {}).get("input")
            output = part.get("state", {}).get("output", "")
            
            # Assistant makes the call
            openai_msgs.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": tool,
                        "arguments": json.dumps(args)
                    }
                }]
            })
            # Tool provides the result
            openai_msgs.append({
                "role": "tool",
                "tool_call_id": call_id,
                "name": tool,
                "content": output if isinstance(output, str) else json.dumps(output)
            })

    if format == "jsonl":
        for m in openai_msgs:
            print(json.dumps(m))
    else:
        # Legacy text rollout
        # ... (keep existing print logic or move to a separate function)
        pass

def rollout_session_text(db: sqlite3.Connection, session_id: str):
    cursor = db.cursor()
    query = """
    SELECT m.id, m.data as msg_data, p.data as part_data
    FROM message m
    JOIN part p ON m.id = p.message_id
    WHERE m.session_id = ?
    ORDER BY m.time_created ASC, p.time_created ASC
    """
    current_msg_id = None
    for row in cursor.execute(query, (session_id,)):
        mid, msg_json, part_json = row
        msg = json.loads(msg_json)
        part = json.loads(part_json)
        if mid != current_msg_id:
            role = msg.get("role", "unknown").upper()
            ts = format_ts(msg.get("time", {}).get("created", 0))
            print(f"\n{'='*20} {role} ({ts}) {'='*20}")
            current_msg_id = mid
        ptype = part.get("type")
        if ptype == "text":
            print(part.get("text", ""))
        elif ptype == "tool":
            tool = part.get("tool")
            input_val = part.get("state", {}).get("input")
            output = part.get("state", {}).get("output")
            print(f"\n[TOOL: {tool}]")
            print(f"INPUT: {json.dumps(input_val, indent=2)}")
            if output:
                print(f"OUTPUT: {str(output)[:500]}{'...' if len(str(output)) > 500 else ''}")

def main():
    parser = argparse.ArgumentParser(description="Opencode Chat History Miner")
    parser.add_argument("--list", action="store_true", help="List recent sessions")
    parser.add_argument("--session", type=str, help="Rollout history for a specific session ID")
    parser.add_argument("--limit", type=int, default=20, help="Limit when listing sessions")
    
    parser.add_argument("--jsonl", action="store_true", help="Output in OpenAI-compatible JSONL format")
    
    args = parser.parse_args()
    
    db_path = get_db_path()
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    # Use uri=True for read-only if supported, or just normal connect
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    
    try:
        if args.list:
            list_sessions(db, args.limit)
        elif args.session:
            if args.jsonl:
                rollout_session(db, args.session, format="jsonl")
            else:
                rollout_session_text(db, args.session)
        else:
            parser.print_help()
    finally:
        db.close()

if __name__ == "__main__":
    main()
