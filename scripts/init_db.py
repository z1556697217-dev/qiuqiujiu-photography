#!/usr/bin/env python3
"""初始化数据库 — 创建所有表"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "assistant.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 原始消息流水（完整保留，永久）
    c.execute("""
        CREATE TABLE IF NOT EXISTS raw_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            msg_id      TEXT UNIQUE,
            timestamp   INTEGER NOT NULL,
            sender      TEXT NOT NULL,
            receiver    TEXT NOT NULL,
            type        INTEGER DEFAULT 1,
            content     TEXT,
            chat_type   TEXT DEFAULT 'private',
            is_deleted  INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    # AI 对话分析层
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id   TEXT NOT NULL,
            raw_msg_id    TEXT,
            turn          INTEGER,
            intent        TEXT,
            confidence    REAL,
            bot_reply     TEXT,
            tags_added    TEXT,
            risk_score    INTEGER DEFAULT 0,
            timestamp     INTEGER NOT NULL
        )
    """)

    # 客户档案
    c.execute("""
        CREATE TABLE IF NOT EXISTS customer_profile (
            wechat_id           TEXT PRIMARY KEY,
            name                TEXT,
            first_contact       INTEGER,
            status              TEXT DEFAULT '咨询中',
            package             TEXT,
            schedule            TEXT,
            deposit             INTEGER,
            tags                TEXT,
            risk_score          INTEGER DEFAULT 0,
            notes               TEXT,
            conversation_summary TEXT,
            is_deleted          INTEGER DEFAULT 0
        )
    """)

    # 档期表
    c.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL,
            time_slot   TEXT NOT NULL,
            customer_id TEXT,
            package     TEXT,
            deposit     INTEGER DEFAULT 0,
            status      TEXT DEFAULT '已预约',
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(date, time_slot)
        )
    """)

    # 秋秋私聊指令日志
    c.execute("""
        CREATE TABLE IF NOT EXISTS admin_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   INTEGER NOT NULL,
            command     TEXT,
            response    TEXT,
            action      TEXT
        )
    """)

    # 索引
    c.execute("CREATE INDEX IF NOT EXISTS idx_raw_sender ON raw_messages(sender)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_raw_time ON raw_messages(timestamp)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_conv_customer ON conversations(customer_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_schedule_date ON schedule(date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_schedule_status ON schedule(status)")

    conn.commit()
    conn.close()

    print(f"✅ 数据库初始化完成: {DB_PATH}")
    return DB_PATH

if __name__ == "__main__":
    init_db()
