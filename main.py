from flask import Flask, render_template_string, request, redirect, url_for, session, Response
import sqlite3
from datetime import datetime
import csv
import io
import os

app = Flask(__name__)
app.secret_key = 'attendance_secret_key_2026'

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f6f9; margin: 0; padding: 15px; text-align: center; }
        .top-bar { background: #2c3e50; padding: 10px 15px; border-radius: 8px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
        .top-bar span { color: white; font-weight: bold; font-size: 14px; }
        .container { max-width: 650px; margin: 0 auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; font-size: 18px; }
        input, select { width: 100%; padding: 12px; font-size: 15px; margin: 8px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; text-align: center; }
        button { width: 100%; background-color: #27ae60; color: white; border: none; padding: 12px; font-size: 16px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 5px; }
        button:hover { background-color: #219653; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px; overflow-x: auto; display: block; }
        th, td { border: 1px solid #ddd; padding: 6px; text-align: center; white-space: nowrap; vertical-align: middle; }
        th { background-color: #34495e; color: white; }
        .msg { margin-top: 10px; font-weight: bold; font-size: 13px; }
        .btn-action { padding: 4px 8px; font-size: 11px; text-decoration: none; border-radius: 4px; color: white; font-weight: bold; display: inline-block; margin: 1px; }
        .btn-edit { background-color: #f39c12; }
        .btn-del { background-color: #e74c3c; }
    </style>
</head>
<body>
    <div class="top-bar">
        <span>🕒 نظام الحضور والرواتب</span>
        <details style="position: relative;">
            <summary style="background: #34495e; color: white; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 13px; list-style: none;">☰ القائمة</summary>
            <div style="position: absolute; left: 0; background: white; min-width: 160px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); border-radius: 6px; margin-top: 5px; z-index: 10; text-align: right;">
                <a href="/" style="display: block; padding: 10px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 12px;">🏠 تسجيل الحضور</a>
                <a href="/admin_dashboard" style="display: block; padding: 10px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 12px;">⚙️ لوحة الإدارة</a>
                <a href="/employees_list" style="display: block; padding: 10px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 12px;">👥 إدارة الموظفين والرواتب</a>
                <a href="/reports" style="display: block; padding: 10px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 12px;">📊 التقارير المالية</a>
                <a href="/logout" style="display: block; padding: 10px; color: #e74c3c; text-decoration: none; font-size: 12px;">🚪 خروج المدير</a>
            </div>
        </details>
    </div>
    
    <div class="container">
        {{ content | safe }}
    </div>
</body>
</html>
"""

def init_db():
    conn = sqlite3.connect('attendance_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            pin_code TEXT NOT NULL,
            standard_hours REAL DEFAULT 8.0,
            monthly_salary REAL DEFAULT 0.0,
            pay_day TEXT DEFAULT 'نهاية الشهر'
        )
    ''')
    try: cursor.execute("ALTER TABLE employees ADD COLUMN monthly_salary REAL DEFAULT 0.0")
    except: pass
    try: cursor.execute("ALTER TABLE employees ADD COLUMN pay_day TEXT DEFAULT 'نهاية الشهر'")
    except: pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            type TEXT NOT NULL,
            method TEXT NOT NULL,
            FOREIGN KEY (emp_id) REFERENCES employees (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    cursor.execute("SELECT value FROM settings WHERE key='admin_pin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO settings (key, value) VALUES ('admin_pin', '9999')")

    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
