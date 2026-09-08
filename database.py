import sqlite3
import json
from datetime import datetime

DB_PATH = "ship_qa.db"


def get_conn():
    """获取数据库连接，并启用 Row 方式取值"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库，创建所有表（程序启动时调用一次）"""
    conn = get_conn()
    cursor = conn.cursor()

    # 表1：用户操作日志（每次问答都记一条）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operation_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT    NOT NULL,
            user_input      TEXT    NOT NULL,
            system_response TEXT    NOT NULL,
            response_time   REAL,
            input_type      TEXT DEFAULT 'text'
        )
    """)

    # 表2：故障记录（确认过的故障才存这里）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fault_record (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp         TEXT NOT NULL,
            equipment_type    TEXT,
            fault_description TEXT,
            fault_cause       TEXT,
            solution          TEXT,
            is_confirmed      INTEGER DEFAULT 0
        )
    """)

    # 表3：完整对话主题会话
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_session (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id        TEXT UNIQUE,
            topic             TEXT,
            created_at        TEXT,
            updated_at        TEXT,
            ship_imo          TEXT,
            language          TEXT,
            messages_json     TEXT,
            report_text       TEXT DEFAULT '',
            report_generated  INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 数据库初始化完成")


def log_operation(user_input: str, response: str, response_time: float = 0.0, input_type: str = "text"):
    """记录一次问答到日志表"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO operation_log (timestamp, user_input, system_response, response_time, input_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_input,
            response,
            response_time,
            input_type
        )
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_logs():
    """查询所有日志（给故障记录页面用）"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operation_log ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def save_fault_record(equipment_type: str, description: str, cause: str, solution: str):
    """保存一条故障记录"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO fault_record (
            timestamp, equipment_type, fault_description, fault_cause, solution, is_confirmed
        ) VALUES (?, ?, ?, ?, ?, 1)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            equipment_type,
            description,
            cause,
            solution
        )
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_fault_records():
    """查询所有故障记录"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fault_record ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# =========================
# 完整会话主题相关函数
# =========================

def save_chat_session(session_id, topic, created_at, updated_at, ship_imo, language, messages):
    """保存或更新会话"""
    conn = get_conn()
    cursor = conn.cursor()

    messages_json = json.dumps(messages or [], ensure_ascii=False)

    cursor.execute("""
        INSERT INTO chat_session (
            session_id, topic, created_at, updated_at,
            ship_imo, language, messages_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            topic = excluded.topic,
            updated_at = excluded.updated_at,
            ship_imo = excluded.ship_imo,
            language = excluded.language,
            messages_json = excluded.messages_json
    """, (
        session_id,
        topic,
        created_at,
        updated_at,
        ship_imo,
        language,
        messages_json
    ))

    conn.commit()
    cursor.close()
    conn.close()


def get_all_chat_sessions():
    """查询所有历史主题会话"""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            session_id,
            topic,
            created_at,
            updated_at,
            ship_imo,
            language,
            messages_json,
            report_text,
            report_generated
        FROM chat_session
        ORDER BY updated_at DESC
    """)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def get_chat_session_by_id(session_id: str):
    """根据 session_id 查询单个主题会话"""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            session_id,
            topic,
            created_at,
            updated_at,
            ship_imo,
            language,
            messages_json,
            report_text,
            report_generated
        FROM chat_session
        WHERE session_id = ?
    """, (session_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()
    return row


def update_chat_session_report(session_id: str, report_text: str):
    """更新会话的 AI 报告内容"""
    if not session_id:
        print("update_chat_session_report: session_id 为空")
        return False

    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE chat_session
            SET report_text = ?, report_generated = ?, updated_at = ?
            WHERE session_id = ?
            """,
            (
                str(report_text or ""),
                1,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                session_id
            )
        )

        conn.commit()
        ok = cursor.rowcount > 0
        print("update_chat_session_report rowcount =", cursor.rowcount)

        cursor.close()
        conn.close()
        return ok

    except Exception as e:
        print(f"update_chat_session_report 出错: {e}")
        return False


def delete_chat_session(session_id: str):
    """删除某个历史会话"""
    if not session_id:
        return False

    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_session WHERE session_id = ?", (session_id,))
        conn.commit()

        deleted = cursor.rowcount > 0

        cursor.close()
        conn.close()
        return deleted

    except Exception as e:
        print(f"删除历史会话失败: {e}")
        return False


def convert_session_row(row):
    """把单条数据库记录转成 dict"""
    if not row:
        return None

    # Row/dict 风格
    if isinstance(row, sqlite3.Row) or hasattr(row, "keys"):
        keys = set(row.keys())

        def safe_get(key, default=None):
            return row[key] if key in keys else default

        try:
            messages = json.loads(safe_get("messages_json", "") or "[]")
        except Exception:
            messages = []

        return {
            "id": safe_get("id", None),
            "session_id": safe_get("session_id", ""),
            "topic": safe_get("topic", ""),
            "created_at": safe_get("created_at", ""),
            "updated_at": safe_get("updated_at", ""),
            "ship_imo": safe_get("ship_imo", ""),
            "language": safe_get("language", "中文"),
            "messages": messages,
            "report_text": safe_get("report_text", "") or "",
            "report_generated": safe_get("report_generated", 0) or 0,
        }

    # tuple/list 风格兼容
    try:
        messages = json.loads(row[7]) if len(row) > 7 and row[7] else []
    except Exception:
        messages = []

    return {
        "id": row[0] if len(row) > 0 else None,
        "session_id": row[1] if len(row) > 1 else "",
        "topic": row[2] if len(row) > 2 else "",
        "created_at": row[3] if len(row) > 3 else "",
        "updated_at": row[4] if len(row) > 4 else "",
        "ship_imo": row[5] if len(row) > 5 else "",
        "language": row[6] if len(row) > 6 else "中文",
        "messages": messages,
        "report_text": row[8] if len(row) > 8 and row[8] else "",
        "report_generated": row[9] if len(row) > 9 and row[9] else 0,
    }


def convert_session_rows(rows):
    """把多条数据库记录转成 dict 列表"""
    return [convert_session_row(r) for r in rows if r]


# 直接运行这个文件可以测试数据库是否正常
if __name__ == "__main__":
    init_db()

    # 插入测试日志数据
    log_operation(
        user_input="发动机冒黑烟是什么原因？",
        response="可能原因：1.燃油雾化不良 2.供油量过多 3.空气不足",
        response_time=1.23
    )

    # 插入测试故障记录
    save_fault_record(
        equipment_type="发动机",
        description="发动机冒黑烟",
        cause="燃油雾化不良",
        solution="检查喷油器，必要时更换"
    )

    # 插入测试会话主题
    test_messages = [
        {"role": "user", "content": "发动机启动困难，并伴随黑烟"},
        {"role": "assistant", "content": "可能与燃油雾化不良、供气不足有关，请先检查喷油器和进气系统。"}
    ]

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_chat_session(
        session_id="TEST-SESSION-001",
        topic="发动机启动困难并黑烟",
        created_at=now_str,
        updated_at=now_str,
        ship_imo="IMO1234567",
        language="中文",
        messages=test_messages
    )

    print("✅ 测试数据插入成功")
    print("日志记录：", get_all_logs())
    print("故障记录：", get_all_fault_records())
    print("会话主题：", convert_session_rows(get_all_chat_sessions()))
