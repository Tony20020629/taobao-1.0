# -*- coding: utf-8 -*-
"""数据库连接管理模块"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "taobao_monitor.db")


def get_db():
    """获取数据库连接，使用row_factory返回字典格式"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库，创建所有必要的表"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 创建商品监测表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT '待采集商品',
            url TEXT NOT NULL UNIQUE,
            current_price REAL DEFAULT 0,
            avg_price REAL DEFAULT 0,
            min_price REAL DEFAULT 0,
            max_price REAL DEFAULT 0,
            frequency INTEGER DEFAULT 60,
            status TEXT DEFAULT 'stopped',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建价格历史记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goods_id INTEGER NOT NULL,
            price REAL NOT NULL,
            promotion_info TEXT DEFAULT '',
            change_type TEXT DEFAULT 'unchanged',
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (goods_id) REFERENCES goods(id)
        )
    """)
    
    # 创建对话历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("[数据库] 初始化成功")
