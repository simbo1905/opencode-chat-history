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

def rollout_session(db: sqlite3.Connection, session_id: str):
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
                print(f"OUTPUT: {output[:500]}{'...' if len(output) > 500 else ''}")

def main():
    parser = argparse.ArgumentParser(description="Opencode Chat History Miner")
    parser.add_argument("--list", action="store_true", help="List recent sessions")
    parser.add_argument("--session", type=str, help="Rollout history for a specific session ID")
    parser.add_argument("--limit", type=int, default=20, help="Limit when listing sessions")
    
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
            rollout_session(db, args.session)
        else:
            parser.print_help()
    finally:
        db.close()

if __name__ == "__main__":
    main()
