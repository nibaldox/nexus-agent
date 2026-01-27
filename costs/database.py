"""
Database schema and operations for cost tracking
Uses SQLite for persistence
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
from config import settings

# Database file location
DB_PATH = Path("costs_tracking.db")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=max(1, settings.sqlite_busy_timeout_ms / 1000))
    try:
        conn.execute(f"PRAGMA journal_mode={settings.sqlite_journal_mode}")
        conn.execute(f"PRAGMA busy_timeout={settings.sqlite_busy_timeout_ms}")
        conn.execute("PRAGMA synchronous=NORMAL")
    except Exception:
        pass
    return conn


def init_database():
    """Initialize the cost tracking database with schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS llm_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        session_id TEXT,
        agent_name TEXT NOT NULL,
        model TEXT NOT NULL,
        prompt_tokens INTEGER NOT NULL,
        completion_tokens INTEGER NOT NULL,
        total_tokens INTEGER NOT NULL,
        input_cost REAL NOT NULL,
        output_cost REAL NOT NULL,
        total_cost REAL NOT NULL,
        duration_ms INTEGER,
        purpose TEXT,
        metadata TEXT
    )
    """)
    
    # Create indexes
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_timestamp 
    ON llm_requests(timestamp)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_agent_name 
    ON llm_requests(agent_name)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_model 
    ON llm_requests(model)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_session_id 
    ON llm_requests(session_id)
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Cost tracking database initialized: {DB_PATH}")


def insert_request(
    agent_name: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    input_cost: float,
    output_cost: float,
    total_cost: float,
    session_id: str = None,
    duration_ms: int = None,
    purpose: str = None,
    metadata: dict = None
) -> int:
    """
    Insert a new LLM request record.
    
    Returns:
        ID of inserted record
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.utcnow().isoformat()
    metadata_json = json.dumps(metadata) if metadata else None
    
    cursor.execute("""
    INSERT INTO llm_requests (
        timestamp, session_id, agent_name, model,
        prompt_tokens, completion_tokens, total_tokens,
        input_cost, output_cost, total_cost,
        duration_ms, purpose, metadata
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, session_id, agent_name, model,
        prompt_tokens, completion_tokens, total_tokens,
        input_cost, output_cost, total_cost,
        duration_ms, purpose, metadata_json
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id


def get_total_cost(
    start_date: str = None,
    end_date: str = None,
    agent_name: str = None,
    model: str = None,
    session_id: str = None
) -> float:
    """
    Get total cost with optional filters.
    
    Args:
        start_date: ISO format timestamp
        end_date: ISO format timestamp
        agent_name: Filter by agent
        model: Filter by model
        session_id: Filter by session
        
    Returns:
        Total cost in USD
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT SUM(total_cost) FROM llm_requests WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    if agent_name:
        query += " AND agent_name = ?"
        params.append(agent_name)
    if model:
        query += " AND model = ?"
        params.append(model)
    if session_id:
        query += " AND session_id = ?"
        params.append(session_id)
    
    cursor.execute(query, params)
    result = cursor.fetchone()[0]
    conn.close()
    
    return result if result else 0.0


def get_request_count(
    start_date: str = None,
    end_date: str = None,
    agent_name: str = None
) -> int:
    """Get count of requests with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT COUNT(*) FROM llm_requests WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    if agent_name:
        query += " AND agent_name = ?"
        params.append(agent_name)
    
    cursor.execute(query, params)
    result = cursor.fetchone()[0]
    conn.close()
    
    return result


def get_recent_requests(limit: int = 50) -> List[Dict]:
    """Get most recent requests"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT * FROM llm_requests 
    ORDER BY timestamp DESC 
    LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_cost_by_agent(
    start_date: str = None,
    end_date: str = None
) -> Dict[str, float]:
    """Get total cost grouped by agent"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT agent_name, SUM(total_cost) as cost
    FROM llm_requests
    WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    
    query += " GROUP BY agent_name ORDER BY cost DESC"
    
    cursor.execute(query, params)
    results = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    
    return results


def get_cost_by_model(
    start_date: str = None,
    end_date: str = None
) -> Dict[str, float]:
    """Get total cost grouped by model"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT model, SUM(total_cost) as cost
    FROM llm_requests
    WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    
    query += " GROUP BY model ORDER BY cost DESC"
    
    cursor.execute(query, params)
    results = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    
    return results


def get_daily_costs(days: int = 30) -> List[Dict]:
    """Get daily cost totals for last N days"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        DATE(timestamp) as date,
        SUM(total_cost) as cost,
        COUNT(*) as requests,
        SUM(total_tokens) as tokens
    FROM llm_requests
    WHERE timestamp >= datetime('now', ? || ' days')
    GROUP BY DATE(timestamp)
    ORDER BY date DESC
    """, (f'-{days}',))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'date': row[0],
            'cost': row[1],
            'requests': row[2],
            'tokens': row[3]
        })
    
    conn.close()
    return results


def clear_old_records(days: int = 90):
    """Delete records older than N days"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    DELETE FROM llm_requests
    WHERE timestamp < datetime('now', ? || ' days')
    """, (f'-{days}',))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"Deleted {deleted} records older than {days} days")
    return deleted


# Initialize database on import
if not DB_PATH.exists():
    init_database()
