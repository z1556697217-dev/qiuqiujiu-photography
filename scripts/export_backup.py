#!/usr/bin/env python3
"""自动导出聊天记录为 HTML（每周日凌晨自动执行）"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "assistant.db")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "backup")

def export_weekly():
    """导出最近一周的所有客户对话"""
    week_label = datetime.now().strftime("%Y-%m-%d_weekly")
    week_dir = os.path.join(BACKUP_DIR, week_label)
    os.makedirs(week_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 按客户分组取本周消息
    since = int((datetime.now() - timedelta(days=7)).timestamp())
    c.execute("""
        SELECT sender, timestamp, content, chat_type
        FROM raw_messages
        WHERE timestamp >= ?
          AND chat_type != 'hermes_admin'
        ORDER BY sender, timestamp
    """, (since,))

    rows = c.fetchall()
    customers = {}
    for r in rows:
        sender = r["sender"]
        customers.setdefault(sender, []).append(r)

    for sender, msgs in customers.items():
        # 取客户备注名
        c.execute("SELECT name FROM customer_profile WHERE wechat_id=?", (sender,))
        profile = c.fetchone()
        name = profile["name"] if profile else sender

        html = _render_html(name, msgs)
        safe_name = name.replace("/", "_").replace("\\", "_")
        path = os.path.join(week_dir, f"{safe_name}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    # 索引页
    index_html = _render_index(week_label, list(customers.items()))
    with open(os.path.join(week_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    conn.close()
    print(f"✅ 导出完成: {week_dir}")
    return week_dir

def _render_html(name, msgs):
    """渲染单个客户对话 HTML（仿微信聊天界面）"""
    messages_html = ""
    for m in msgs:
        ts = datetime.fromtimestamp(m["timestamp"]).strftime("%m/%d %H:%M")
        content = m["content"] or "[非文字消息]"
        is_self = m["chat_type"] == "hermes_admin"  # Bot 发出的

        messages_html += f"""
        <div class="msg {'self' if is_self else 'other'}">
            <div class="bubble">{content}</div>
            <div class="time">{ts}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>与 {name} 的聊天记录</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; background:#ededed; padding:20px; }}
h1 {{ text-align:center; color:#666; font-size:14px; margin-bottom:20px; }}
.msg {{ margin-bottom:16px; display:flex; flex-direction:column; }}
.self {{ align-items:flex-end; }}
.other {{ align-items:flex-start; }}
.bubble {{ max-width:70%; padding:10px 14px; border-radius:12px; font-size:15px; line-height:1.5; word-break:break-all; }}
.self .bubble {{ background:#95ec69; }}
.other .bubble {{ background:#fff; }}
.time {{ font-size:11px; color:#999; margin-top:4px; }}
</style>
</head>
<body>
<h1>与 {name} 的聊天记录<br>导出时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}</h1>
{messages_html}
</body>
</html>"""

def _render_index(week_label, customers):
    """渲染索引页"""
    links = ""
    for sender, msgs in customers:
        name = sender
        count = len(msgs)
        first_ts = datetime.fromtimestamp(msgs[0]["timestamp"]).strftime("%m/%d")
        last_ts = datetime.fromtimestamp(msgs[-1]["timestamp"]).strftime("%m/%d")
        safe_name = name.replace("/", "_").replace("\\", "_")
        links += f'<li><a href="{safe_name}.html">{name}</a> — {count} 条消息 ({first_ts} ~ {last_ts})</li>'

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>聊天记录备份 — {week_label}</title>
<style>
body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; max-width:600px; margin:40px auto; padding:20px; }}
h1 {{ font-size:18px; margin-bottom:20px; }}
li {{ margin:8px 0; }}
a {{ color:#07c160; text-decoration:none; }}
</style>
</head>
<body>
<h1>📋 聊天记录备份 — {week_label}</h1>
<ul>{links}</ul>
</body>
</html>"""

if __name__ == "__main__":
    export_weekly()
