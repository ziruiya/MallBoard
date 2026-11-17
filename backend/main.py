import json
import hashlib
import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import pymysql
from pymysql.cursors import DictCursor
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parent.parent
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ["DB_NAME"],
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
    "connect_timeout": 10,
    "init_command": "SET time_zone = '+09:00'",
}

app = FastAPI(title="MallBoard", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS stores (
  id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120) NOT NULL, area VARCHAR(120) NOT NULL,
  opened_at DATE NULL
);
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120) NOT NULL, role VARCHAR(40) NOT NULL,
  store_id INT NULL, FOREIGN KEY (store_id) REFERENCES stores(id)
);
CREATE TABLE IF NOT EXISTS households (
  id INT AUTO_INCREMENT PRIMARY KEY, representative_name VARCHAR(120) NOT NULL, store_id INT,
  advisor_id INT, budget_band VARCHAR(120), area_pref VARCHAR(255), land_status VARCHAR(40),
  status VARCHAR(40) NOT NULL DEFAULT 'active', lost_reason TEXT, created_at DATETIME NOT NULL,
  household_code VARCHAR(24) UNIQUE,
  FOREIGN KEY (store_id) REFERENCES stores(id), FOREIGN KEY (advisor_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS persons (
  id INT AUTO_INCREMENT PRIMARY KEY, household_id INT NOT NULL, name VARCHAR(120) NOT NULL,
  relation VARCHAR(80), phone VARCHAR(50), email VARCHAR(255),
  FOREIGN KEY (household_id) REFERENCES households(id)
);
CREATE TABLE IF NOT EXISTS touches (
  id INT AUTO_INCREMENT PRIMARY KEY, household_id INT NOT NULL, touch_at DATETIME NOT NULL,
  channel VARCHAR(80) NOT NULL, campaign_id VARCHAR(255), creative_id VARCHAR(255), tracking_code VARCHAR(255),
  landing_referrer VARCHAR(500), store_id INT, capture_method VARCHAR(80),
  FOREIGN KEY (household_id) REFERENCES households(id), FOREIGN KEY (store_id) REFERENCES stores(id)
);
CREATE TABLE IF NOT EXISTS activities (
  id INT AUTO_INCREMENT PRIMARY KEY, household_id INT NOT NULL, user_id INT NOT NULL,
  type VARCHAR(80) NOT NULL, body TEXT NOT NULL, acted_at DATETIME NOT NULL,
  next_action TEXT, next_action_due DATE, FOREIGN KEY (household_id) REFERENCES households(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS stage_events (
  id INT AUTO_INCREMENT PRIMARY KEY, household_id INT NOT NULL, from_stage VARCHAR(80), to_stage VARCHAR(80) NOT NULL,
  changed_by INT, changed_at DATETIME NOT NULL, FOREIGN KEY (household_id) REFERENCES households(id),
  FOREIGN KEY (changed_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS partners (
  id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(160) NOT NULL, area VARCHAR(120),
  tags JSON NOT NULL, active TINYINT NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS partner_staff (
  id INT AUTO_INCREMENT PRIMARY KEY, partner_id INT NOT NULL, name VARCHAR(120) NOT NULL,
  branch_name VARCHAR(120),
  FOREIGN KEY (partner_id) REFERENCES partners(id)
);
CREATE TABLE IF NOT EXISTS fee_rules (
  id INT AUTO_INCREMENT PRIMARY KEY, version VARCHAR(80) NOT NULL, type VARCHAR(40) NOT NULL, params JSON NOT NULL,
  base VARCHAR(120) NOT NULL, effective_from DATE NOT NULL, effective_to DATE NULL, approved_by INT,
  FOREIGN KEY (approved_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS partner_agreements (
  id INT AUTO_INCREMENT PRIMARY KEY, partner_id INT NOT NULL, effective_from DATE NOT NULL,
  effective_to DATE, fee_rule_id INT NOT NULL, status VARCHAR(40) NOT NULL,
  FOREIGN KEY (partner_id) REFERENCES partners(id), FOREIGN KEY (fee_rule_id) REFERENCES fee_rules(id)
);
CREATE TABLE IF NOT EXISTS introductions (
  id INT AUTO_INCREMENT PRIMARY KEY, household_id INT NOT NULL, partner_id INT NOT NULL,
  partner_staff_id INT, advisor_id INT, introduced_at DATETIME NOT NULL, reception_confirmed_at DATETIME,
  status VARCHAR(80) NOT NULL, existing_customer_flag TINYINT NOT NULL DEFAULT 0, evidence_note TEXT,
  valid_until DATE NULL,
  FOREIGN KEY (household_id) REFERENCES households(id), FOREIGN KEY (partner_id) REFERENCES partners(id),
  FOREIGN KEY (partner_staff_id) REFERENCES partner_staff(id)
);
CREATE TABLE IF NOT EXISTS negotiations (
  id INT AUTO_INCREMENT PRIMARY KEY, introduction_id INT NOT NULL, status VARCHAR(80) NOT NULL,
  last_activity_at DATETIME NOT NULL, FOREIGN KEY (introduction_id) REFERENCES introductions(id)
);
CREATE TABLE IF NOT EXISTS contracts (
  id INT AUTO_INCREMENT PRIMARY KEY, negotiation_id INT NOT NULL, contract_date DATE NOT NULL,
  contract_amount BIGINT NOT NULL, builder_contact VARCHAR(120) NOT NULL,
  FOREIGN KEY (negotiation_id) REFERENCES negotiations(id)
);
CREATE TABLE IF NOT EXISTS construction_projects (
  id INT AUTO_INCREMENT PRIMARY KEY, contract_id INT NOT NULL, planned_start_date DATE,
  actual_start_date DATE, confirmed_start_date DATE, confirmation_evidence TEXT,
  confirmation_due_date DATE, confirmation_status VARCHAR(40) NOT NULL DEFAULT 'pending_review',
  delayed_note TEXT,
  FOREIGN KEY (contract_id) REFERENCES contracts(id)
);
CREATE TABLE IF NOT EXISTS fee_entitlements (
  id INT AUTO_INCREMENT PRIMARY KEY, contract_id INT NOT NULL, introduction_id INT NOT NULL,
  fee_rule_id INT NOT NULL, base_amount BIGINT NOT NULL, calculated_amount BIGINT NOT NULL,
  state VARCHAR(40) NOT NULL, dispute_reason TEXT, calculated_at DATETIME NOT NULL, confirmed_by INT,
  invoice_data_generated TINYINT NOT NULL DEFAULT 0, reference_amount BIGINT NOT NULL DEFAULT 0,
  FOREIGN KEY (contract_id) REFERENCES contracts(id), FOREIGN KEY (introduction_id) REFERENCES introductions(id),
  FOREIGN KEY (fee_rule_id) REFERENCES fee_rules(id), FOREIGN KEY (confirmed_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS referral_disputes (
  id INT AUTO_INCREMENT PRIMARY KEY, fee_entitlement_id INT NOT NULL, raised_by INT NOT NULL,
  reason TEXT NOT NULL, evidence_level VARCHAR(8) NOT NULL, status VARCHAR(40) NOT NULL, decided_by INT,
  decided_at DATETIME, decision_note TEXT, due_date DATE NULL,
  dispute_type VARCHAR(40) NOT NULL DEFAULT 'referral', reference_amount BIGINT NOT NULL DEFAULT 0,
  FOREIGN KEY (fee_entitlement_id) REFERENCES fee_entitlements(id),
  FOREIGN KEY (raised_by) REFERENCES users(id), FOREIGN KEY (decided_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS consents (
  id INT AUTO_INCREMENT PRIMARY KEY, household_id INT NOT NULL, purpose VARCHAR(255) NOT NULL,
  scope VARCHAR(40) NOT NULL, granted_at DATETIME NOT NULL, revoked_at DATETIME,
  FOREIGN KEY (household_id) REFERENCES households(id)
);
CREATE TABLE IF NOT EXISTS data_disclosures (
  id INT AUTO_INCREMENT PRIMARY KEY, household_id INT NOT NULL, disclosed_to VARCHAR(255) NOT NULL,
  scope VARCHAR(40) NOT NULL, disclosed_by INT NOT NULL, disclosed_at DATETIME NOT NULL,
  consent_id INT, FOREIGN KEY (household_id) REFERENCES households(id),
  FOREIGN KEY (disclosed_by) REFERENCES users(id), FOREIGN KEY (consent_id) REFERENCES consents(id)
);
CREATE TABLE IF NOT EXISTS tasks (
  id INT AUTO_INCREMENT PRIMARY KEY, assignee_id INT NOT NULL, title VARCHAR(255) NOT NULL, due_at DATE NOT NULL,
  source VARCHAR(40) NOT NULL, related_household_id INT, done TINYINT NOT NULL DEFAULT 0,
  task_type VARCHAR(40) NOT NULL DEFAULT 'followup', priority VARCHAR(20) NOT NULL DEFAULT 'normal',
  related_type VARCHAR(40) NOT NULL DEFAULT 'household', related_id INT, cancelled TINYINT NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'open',
  FOREIGN KEY (assignee_id) REFERENCES users(id), FOREIGN KEY (related_household_id) REFERENCES households(id)
);
CREATE TABLE IF NOT EXISTS daily_report_drafts (
  id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, report_date DATE NOT NULL,
  auto_summary TEXT NOT NULL, manual_note TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS audit_logs (
  id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, action VARCHAR(120) NOT NULL, target_type VARCHAR(120) NOT NULL,
  target_id INT, `at` DATETIME NOT NULL, detail TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS system_configs (
  config_key VARCHAR(120) PRIMARY KEY, value_json JSON NOT NULL, updated_at DATETIME NOT NULL,
  updated_by INT NULL
);
CREATE TABLE IF NOT EXISTS audit_chain (
  id TINYINT PRIMARY KEY, last_hash CHAR(64) NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
  id BIGINT AUTO_INCREMENT PRIMARY KEY, actor_id INT NULL, actor_role VARCHAR(40) NOT NULL,
  action VARCHAR(120) NOT NULL, object_type VARCHAR(120) NOT NULL, object_id INT NULL,
  reason TEXT NOT NULL, event_at DATETIME NOT NULL, previous_hash CHAR(64) NOT NULL,
  event_hash CHAR(64) NOT NULL UNIQUE,
  INDEX idx_audit_events_at(event_at), INDEX idx_audit_events_object(object_type, object_id)
);
CREATE TABLE IF NOT EXISTS seed_metadata (
  id TINYINT PRIMARY KEY, batch_key VARCHAR(80) NOT NULL, seeded_at DATETIME NOT NULL
);
CREATE TABLE IF NOT EXISTS user_preferences (
  user_id INT PRIMARY KEY, dashboard_widgets JSON NOT NULL, notification_preferences JSON NOT NULL,
  updated_at DATETIME NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS sla_settings (
  reminder_type VARCHAR(40) PRIMARY KEY, days_before INT NOT NULL, label_ja VARCHAR(120) NOT NULL,
  label_zh VARCHAR(120) NOT NULL
);
"""

TABLES = [
    "user_preferences", "audit_logs", "daily_report_drafts", "tasks", "data_disclosures", "consents", "referral_disputes",
    "fee_entitlements", "construction_projects", "contracts", "negotiations", "introductions",
    "partner_agreements", "fee_rules", "partner_staff", "partners", "stage_events", "activities",
    "touches", "persons", "households", "users", "stores", "seed_metadata", "sla_settings",
]

STORES = [
    ("店舗A", "東京"), ("店舗B", "東京"), ("店舗C", "東京"), ("店舗D", "神奈川"),
    ("店舗E", "神奈川"), ("店舗F", "埼玉"), ("店舗G", "千葉"), ("店舗H", "千葉"),
    ("店舗I", "愛知"), ("店舗J", "大阪"), ("店舗K", "兵庫"), ("店舗L", "福岡"),
]
STAGES = ["新規予約", "初回相談済", "FP診断済", "紹介済", "訪問・商談中", "契約", "着工", "完了・見送り"]
SEED_BATCH = "mallboard-demo-2026-11-full-v2"
SAMPLE_SURNAMES = ["佐藤", "田中", "鈴木", "高橋", "伊藤", "渡辺", "山本", "中村", "小林", "加藤", "吉田", "山田"]

SYSTEM_CONFIG_DEFAULTS = {
    "fee_rule.applicability_basis": "contract_date",
    "fee.bank_fee_tolerance_yen": 1000,
    "expense.approval_thresholds_yen": [10000, 50000],
    "expense.allowed_categories": ["交通費", "消耗品費", "会議費"],
    "retention.interview_online_years": 3,
    "retention.interview_archive_years": 5,
    "retention.daily_report_years": 3,
    "retention.monthly_report_years": 5,
    "retention.month_close_snapshot_years": 7,
    "retention.audit_years": 5,
    "attachment.allowed_extensions": ["pdf", "jpg", "jpeg", "png", "csv"],
    "attachment.max_file_mb": 10,
    "import.max_csv_rows": 50000,
    "construction.expected_start_months": 6,
    "search.alert_queries_per_minute": 30,
    "notification.email_retry_minutes": [1, 5, 15],
    "notification.quiet_hours": {"start": "21:00", "end": "07:00"},
    "calendar.retry_minutes": [1, 5, 15, 60],
    "calendar.max_retries": 4,
    "finance.sync_interval_minutes": 60,
    "finance.summary_stale_after_minutes": 120,
    "task.followup_sla_days": 3,
    "task.partner_feedback_sla_days": 5,
    "task.construction_evidence_sla_days": 7,
    # Provisional demo defaults; final SLA days require company confirmation.
    "sla.introduction_validity_days": 30,
    "sla.construction_evidence_days": 7,
    "sla.dispute_resolution_days": 14,
    "sla.agreement_renewal_days": 30,
    "sla.fee_rule_validity_days": 30,
    "month_close.lock_working_day": 5,
    "expense.max_receipt_mb": 10,
}

SYSTEM_CONFIG_RANGES = {
    "fee.bank_fee_tolerance_yen": (0, 100000),
    "retention.interview_online_years": (1, 10),
    "retention.interview_archive_years": (1, 20),
    "retention.daily_report_years": (1, 10),
    "retention.monthly_report_years": (1, 20),
    "retention.month_close_snapshot_years": (1, 20),
    "retention.audit_years": (1, 20),
    "attachment.max_file_mb": (1, 100),
    "import.max_csv_rows": (1, 50000),
    "construction.expected_start_months": (1, 24),
    "search.alert_queries_per_minute": (1, 10000),
    "calendar.max_retries": (1, 4),
    "finance.sync_interval_minutes": (5, 1440),
    "finance.summary_stale_after_minutes": (5, 10080),
    "task.followup_sla_days": (0, 365),
    "task.partner_feedback_sla_days": (0, 365),
    "task.construction_evidence_sla_days": (0, 365),
    "sla.introduction_validity_days": (0, 365),
    "sla.construction_evidence_days": (0, 365),
    "sla.dispute_resolution_days": (0, 365),
    "sla.agreement_renewal_days": (0, 365),
    "sla.fee_rule_validity_days": (0, 365),
    "month_close.lock_working_day": (1, 10),
    "expense.max_receipt_mb": (1, 100),
}


def connect():
    return Database(pymysql.connect(**DB_CONFIG))


SLA_CONFIG = [
    ("introduction_validity", "sla.introduction_validity_days", "紹介有効期間", "介绍有效期"),
    ("construction_evidence", "sla.construction_evidence_days", "着工証拠提出期限", "开工证据提交期限"),
    ("dispute_resolution", "sla.dispute_resolution_days", "争議処理期限", "争议处理期限"),
    ("agreement_renewal", "sla.agreement_renewal_days", "提携契約更新期限", "合作协议续约期限"),
    ("fee_rule_validity", "sla.fee_rule_validity_days", "FeeRule適用期限", "FeeRule 适用期限"),
]


class Row(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return tuple(self.values())[key]
        return super().__getitem__(key)


class Cursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def fetchone(self):
        row = self.cursor.fetchone()
        return Row(row) if row is not None else None

    def fetchall(self):
        return [Row(row) for row in self.cursor.fetchall()]

    def __iter__(self):
        return iter(self.fetchall())

    @property
    def lastrowid(self):
        return self.cursor.lastrowid


class Database:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query.replace("?", "%s"), params)
        return Cursor(cursor)

    def executemany(self, query, params):
        cursor = self.connection.cursor()
        cursor.executemany(query.replace("?", "%s"), params)
        return Cursor(cursor)

    def executescript(self, script):
        for statement in script.split(";"):
            if statement.strip():
                self.execute(statement)

    def commit(self):
        self.connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.connection.close()


def audit(db, user_id, action, target_type, target_id, detail):
    actor = db.execute("SELECT role FROM users WHERE id=?", (user_id,)).fetchone() if user_id else None
    event_at = datetime.now().isoformat(timespec="seconds")
    previous_hash = db.execute(
        "SELECT last_hash FROM audit_chain WHERE id=1 FOR UPDATE"
    ).fetchone()
    previous_hash = previous_hash["last_hash"] if previous_hash else "0" * 64
    event = {
        "actor_id": user_id,
        "actor_role": actor["role"] if actor else "system",
        "action": action,
        "object_type": target_type,
        "object_id": target_id,
        "reason": detail,
        "event_at": event_at,
        "previous_hash": previous_hash,
    }
    event_hash = hashlib.sha256(
        (previous_hash + json.dumps(event, ensure_ascii=False, sort_keys=True)).encode("utf-8")
    ).hexdigest()
    db.execute(
        "INSERT INTO audit_logs(user_id, action, target_type, target_id, `at`, detail) VALUES(?,?,?,?,?,?)",
        (user_id, action, target_type, target_id, event_at, detail),
    )
    db.execute(
        """INSERT INTO audit_events(actor_id,actor_role,action,object_type,object_id,reason,event_at,
           previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?,?)""",
        (user_id, event["actor_role"], action, target_type, target_id, detail, event_at, previous_hash, event_hash),
    )
    db.execute("UPDATE audit_chain SET last_hash=? WHERE id=1", (event_hash,))


def ensure_system_config(db):
    db.execute("INSERT IGNORE INTO audit_chain(id,last_hash) VALUES(1,?)", ("0" * 64,))
    now = datetime.now().isoformat(timespec="seconds")
    for key, value in SYSTEM_CONFIG_DEFAULTS.items():
        db.execute(
            "INSERT IGNORE INTO system_configs(config_key,value_json,updated_at) VALUES(?,?,?)",
            (key, json.dumps(value, ensure_ascii=False, sort_keys=True), now),
        )
    sync_sla_settings(db)
    verify_audit_chain(db)


def sync_sla_settings(db):
    for reminder_type, config_key, label_ja, label_zh in SLA_CONFIG:
        row = db.execute(
            "SELECT value_json FROM system_configs WHERE config_key=?", (config_key,)
        ).fetchone()
        if not row:
            continue
        days = json.loads(row["value_json"]) if isinstance(row["value_json"], str) else row["value_json"]
        db.execute(
            """INSERT INTO sla_settings(reminder_type,days_before,label_ja,label_zh)
               VALUES(?,?,?,?) ON DUPLICATE KEY UPDATE days_before=VALUES(days_before),
               label_ja=VALUES(label_ja),label_zh=VALUES(label_zh)""",
            (reminder_type, days, label_ja, label_zh),
        )


def verify_audit_chain(db):
    previous_hash = "0" * 64
    for row in db.execute("SELECT * FROM audit_events ORDER BY id"):
        event_at = row["event_at"]
        if isinstance(event_at, datetime):
            event_at = event_at.isoformat(timespec="seconds")
        event = {
            "actor_id": row["actor_id"],
            "actor_role": row["actor_role"],
            "action": row["action"],
            "object_type": row["object_type"],
            "object_id": row["object_id"],
            "reason": row["reason"],
            "event_at": event_at,
            "previous_hash": previous_hash,
        }
        expected_hash = hashlib.sha256(
            (previous_hash + json.dumps(event, ensure_ascii=False, sort_keys=True)).encode("utf-8")
        ).hexdigest()
        if row["previous_hash"] != previous_hash or row["event_hash"] != expected_hash:
            raise RuntimeError(f"Audit event chain verification failed at event {row['id']}")
        previous_hash = expected_hash
    head = db.execute("SELECT last_hash FROM audit_chain WHERE id=1").fetchone()
    if not head or head["last_hash"] != previous_hash:
        raise RuntimeError("Audit event chain head does not match the recorded events")


def ensure_schema(db):
    db.executescript(SCHEMA)
    migrations = {
        "households": {"household_code": "VARCHAR(24) NULL"},
        "stores": {"opened_at": "DATE NULL"},
        "partner_staff": {"branch_name": "VARCHAR(120) NULL"},
        "fee_rules": {"effective_to": "DATE NULL"},
        "introductions": {"advisor_id": "INT NULL", "valid_until": "DATE NULL"},
        "construction_projects": {
            "confirmation_due_date": "DATE NULL",
            "confirmation_status": "VARCHAR(40) NOT NULL DEFAULT 'pending_review'",
            "delayed_note": "TEXT NULL",
        },
        "fee_entitlements": {
            "invoice_data_generated": "TINYINT NOT NULL DEFAULT 0",
            "reference_amount": "BIGINT NOT NULL DEFAULT 0",
        },
        "referral_disputes": {
            "due_date": "DATE NULL",
            "dispute_type": "VARCHAR(40) NOT NULL DEFAULT 'referral'",
            "reference_amount": "BIGINT NOT NULL DEFAULT 0",
        },
        "tasks": {
            "task_type": "VARCHAR(40) NOT NULL DEFAULT 'followup'",
            "priority": "VARCHAR(20) NOT NULL DEFAULT 'normal'",
            "related_type": "VARCHAR(40) NOT NULL DEFAULT 'household'",
            "related_id": "INT NULL",
            "cancelled": "TINYINT NOT NULL DEFAULT 0",
            "status": "VARCHAR(20) NOT NULL DEFAULT 'open'",
        },
        "user_preferences": {
            "dashboard_widgets": "JSON NULL",
            "notification_preferences": "JSON NULL",
        },
    }
    for table, columns in migrations.items():
        for column, definition in columns.items():
            exists = db.execute(
                """SELECT COUNT(*) FROM information_schema.columns
                   WHERE table_schema=DATABASE() AND table_name=? AND column_name=?""",
                (table, column),
            ).fetchone()[0]
            if not exists:
                db.execute(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}")
    db.execute("UPDATE tasks SET status=IF(done=1,'done','open') WHERE status IS NULL")
def valid_config_value(key, value):
    default = SYSTEM_CONFIG_DEFAULTS[key]
    if type(value) is not type(default):
        return False
    if isinstance(default, dict):
        if value.keys() != default.keys():
            return False
        try:
            for item in value.values():
                datetime.strptime(item, "%H:%M")
        except (TypeError, ValueError):
            return False
    elif isinstance(default, list):
        if len(value) != len(default) or any(type(v) is not type(default[0]) for v in value):
            return False
        if all(type(v) is int for v in value) and value != sorted(value):
            return False
        if all(type(v) is str for v in value) and any(not v.strip() for v in value):
            return False
    if isinstance(value, int) and not isinstance(value, bool):
        minimum, maximum = SYSTEM_CONFIG_RANGES.get(key, (0, 100000))
        if not minimum <= value <= maximum:
            return False
    if key == "fee_rule.applicability_basis" and value not in (
        "contract_date", "agreement_date", "construction_confirmation_date"
    ):
        return False
    if key == "expense.allowed_categories" and not set(value).issubset(
        {"交通費", "消耗品費", "会議費", "通信費", "その他"}
    ):
        return False
    if key == "expense.approval_thresholds_yen" and value[0] >= value[1]:
        return False
    if key == "attachment.allowed_extensions" and not set(value).issubset(
        {"pdf", "jpg", "jpeg", "png", "csv", "xlsx"}
    ):
        return False
    if isinstance(value, list) and value and type(value[0]) is int:
        if any(v < 0 or v > 100000 for v in value):
            return False
    return True


def seed(db):
    ensure_schema(db)
    if db.execute("SELECT COUNT(*) FROM seed_metadata WHERE id=1").fetchone()[0]:
        return
    if db.execute("SELECT COUNT(*) FROM stores").fetchone()[0]:
        return
    now = datetime.now().replace(microsecond=0)
    today = date.today()
    db.executemany(
        "INSERT INTO stores(id,name,area,opened_at) VALUES(?,?,?,?)",
        [(index + 1, name, area, date(2020 + index % 5, index % 12 + 1, 1))
         for index, (name, area) in enumerate(STORES)],
    )
    users = {}
    for name, role, store_id in (
        ("デモ顧問A", "advisor", 1), ("デモ店長A", "manager", 3),
        ("デモ経理A", "hq_finance", None), ("デモ社長A", "executive", None),
    ):
        users[role] = db.execute(
            "INSERT INTO users(name,role,store_id) VALUES(?,?,?)", (name, role, store_id)
        ).lastrowid
    advisors = [users["advisor"]]
    for store_id in range(2, 13):
        advisors.append(db.execute(
            "INSERT INTO users(name,role,store_id) VALUES(?,?,?)",
            (f"デモ顧問{chr(64 + store_id)}", "advisor", store_id),
        ).lastrowid)

    month_counts = [(6, 7), (7, 8), (8, 10), (9, 12), (10, 14), (11, 9)]
    intake_dates = []
    for month, count in month_counts:
        start = date(2026, month, 1)
        next_month = date(2026 + (month == 12), month % 12 + 1, 1)
        days = (next_month - start).days
        intake_dates.extend(start + timedelta(days=(index * 3) % days) for index in range(count))
    intake_dates[-1] = date(2026, 11, 16)

    household_counts_by_store = [6, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4]
    store_ids = [store_id for store_id, count in enumerate(household_counts_by_store, 1)
                 for _ in range(count)]
    state_by_number = {
        **{i: "入金済" for i in range(1, 6)},
        **{i: "争議中" for i in range(6, 9)},
        **{i: "請求済" for i in range(9, 14)},
        **{i: "報酬承認待ち" for i in range(14, 18)},
        **{i: "着工確認待ち" for i in range(18, 23)},
        **{i: "契約済" for i in range(23, 29)},
        **{i: "紹介中" for i in range(29, 45)},
        **{i: "相談中" for i in range(45, 57)},
        **{i: "解約済" for i in range(57, 61)},
    }

    fee_rule_ids = {}
    partner_staff_ids = {}
    for partner_id in range(1, 13):
        letter = chr(64 + partner_id)
        db.execute(
            "INSERT INTO partners(id,name,area,tags,active) VALUES(?,?,?,?,1)",
            (partner_id, f"住宅会社{letter}", STORES[partner_id - 1][1],
             json.dumps(["価格", "性能"], ensure_ascii=False)),
        )
        for staff_letter, branch_letter in (("A", "A"), ("B", "A"), ("C", "B")):
            staff_id = db.execute(
                "INSERT INTO partner_staff(partner_id,name,branch_name) VALUES(?,?,?)",
                (partner_id, f"担当者{staff_letter}", f"支店{branch_letter}"),
            ).lastrowid
            partner_staff_ids.setdefault(partner_id, []).append(staff_id)
        old_rule = db.execute(
            """INSERT INTO fee_rules(version,type,params,base,effective_from,effective_to,approved_by)
               VALUES(?, 'rate', ?, '請負金額', '2025-01-01', '2025-12-31', ?)""",
            (f"2025.{letter}", '{"rate":0.018}', users["hq_finance"]),
        ).lastrowid
        current_rule = db.execute(
            """INSERT INTO fee_rules(version,type,params,base,effective_from,effective_to,approved_by)
               VALUES(?, 'rate', ?, '請負金額', '2026-01-01', ?, ?)""",
            (f"2026.{letter}", '{"rate":0.02}',
             today + timedelta(days=20) if partner_id == 1 else None, users["hq_finance"]),
        ).lastrowid
        fee_rule_ids[partner_id] = current_rule
        db.execute(
            "INSERT INTO partner_agreements(partner_id,effective_from,effective_to,fee_rule_id,status) VALUES(?,?,?,?,?)",
            (partner_id, "2025-01-01", "2025-12-31", old_rule, "expired"),
        )
        db.execute(
            "INSERT INTO partner_agreements(partner_id,effective_from,effective_to,fee_rule_id,status) VALUES(?,?,?,?,?)",
            (partner_id, "2026-01-01", today + timedelta(days=15) if partner_id == 1 else None,
             current_rule, "active"),
        )

    spread_households = {}
    for number in range(1, 61):
        code = f"HH-D{number:03}"
        store_id = store_ids[number - 1]
        advisor_id = advisors[store_id - 1]
        if number in (4, 17, 35, 44):
            advisor_id = None
        status_name = state_by_number[number]
        status = "lost" if status_name == "解約済" else "completed" if status_name == "入金済" else "active"
        intake_at = datetime.combine(intake_dates[number - 1], datetime.min.time())
        name = f"{SAMPLE_SURNAMES[(number - 1) % 12]}{chr(65 + (number - 1) // 12)}"
        household_id = db.execute(
            """INSERT INTO households(household_code,representative_name,store_id,advisor_id,budget_band,
               area_pref,land_status,status,created_at,lost_reason)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (code, name, store_id, advisor_id,
             ("4,000〜5,000万円", "5,000〜6,000万円", "6,000〜7,000万円")[number % 3],
             f"{STORES[store_id - 1][1]}エリア", ("有", "無", "検討中")[number % 3],
             status, intake_at, "デモ見送り" if status == "lost" else None),
        ).lastrowid
        spread_households[number] = {"id": household_id, "code": code, "store_id": store_id,
                                     "advisor_id": advisor_id, "name": name}
        db.execute(
            "INSERT INTO persons(household_id,name,relation,phone,email) VALUES(?,?,?,?,?)",
            (household_id, name, "本人", f"090-0000-{number:04}", f"demo{number:03}@example.test"),
        )
        for touch_index, channel in enumerate(("Web広告", "直接来店")):
            touch_at = intake_at + timedelta(days=touch_index * 3)
            db.execute(
                """INSERT INTO touches(household_id,touch_at,channel,campaign_id,creative_id,
                   tracking_code,landing_referrer,store_id,capture_method) VALUES(?,?,?,?,?,?,?,?,?)""",
                (household_id, touch_at, channel, "DEMO_2026", "DEMO_CREATIVE",
                 f"DEMO-{number:03}-{touch_index}", "demo.example.test", store_id,
                 "UTM" if touch_index == 0 else "手入力"),
            )
        stage_name = {
            "相談中": "初回相談済", "紹介中": "紹介済", "契約済": "契約",
            "着工確認待ち": "着工", "報酬承認待ち": "着工", "請求済": "着工",
            "入金済": "完了・見送り", "争議中": "紹介済", "解約済": "完了・見送り",
        }[status_name]
        db.execute(
            "INSERT INTO stage_events(household_id,from_stage,to_stage,changed_by,changed_at) VALUES(?,NULL,?,?,?)",
            (household_id, stage_name, advisors[store_id - 1], intake_at),
        )
        db.execute(
            "INSERT INTO consents(household_id,purpose,scope,granted_at) VALUES(?,?,?,?)",
            (household_id, "住宅会社への希望条件共有", "L3", intake_at + timedelta(days=2)),
        )
        db.execute(
            """INSERT INTO activities(household_id,user_id,type,body,acted_at,next_action,next_action_due)
               VALUES(?,?,'面談','ご希望条件を確認しました',?,?,?)""",
            (household_id, advisor_id or users["manager"], intake_at + timedelta(days=2),
             "次回相談の確認", intake_dates[number - 1] + timedelta(days=4)),
        )

    introduced_households = set(range(1, 45)) | set(range(52, 56))
    double_households = set(range(24, 36))
    triple_households = set(range(18, 24))
    introductions_by_household = {}
    for number in sorted(introduced_households):
        household = spread_households[number]
        count = 3 if number in triple_households else 2 if number in double_households else 1
        rows = []
        for position in range(count):
            partner_id = ((number + position * 4 - 1) % 12) + 1
            introduced_at = datetime.combine(
                intake_dates[number - 1] + timedelta(days=7 + position), datetime.min.time()
            )
            status = "受付確認済" if number % 4 else "紹介済"
            intro_id = db.execute(
                """INSERT INTO introductions(household_id,partner_id,partner_staff_id,advisor_id,
                   introduced_at,reception_confirmed_at,status,valid_until)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (household["id"], partner_id, partner_staff_ids[partner_id][0],
                 household["advisor_id"] if number % 13 else None, introduced_at,
                 introduced_at + timedelta(days=1) if status == "受付確認済" else None,
                 status, today + timedelta(days=5) if number == 11 else introduced_at.date() + timedelta(days=30)),
            ).lastrowid
            negotiation_id = db.execute(
                "INSERT INTO negotiations(introduction_id,status,last_activity_at) VALUES(?,?,?)",
                (intro_id, ("訪問予定", "商談中", "見積提示")[position % 3],
                 introduced_at + timedelta(days=position + 2)),
            ).lastrowid
            rows.append((intro_id, negotiation_id, partner_id))
        introductions_by_household[number] = rows

    def create_contract(number, position=0, amount=32_000_000, project=None,
                        fee_state=None, dispute=None, contract_date_override=None):
        intro_id, negotiation_id, partner_id = introductions_by_household[number][position]
        contract_date = contract_date_override or intake_dates[number - 1] + timedelta(days=45)
        db.execute("UPDATE negotiations SET status='契約' WHERE id=?", (negotiation_id,))
        contract_id = db.execute(
            "INSERT INTO contracts(negotiation_id,contract_date,contract_amount,builder_contact) VALUES(?,?,?,?)",
            (negotiation_id, contract_date, amount, "担当者A"),
        ).lastrowid
        if project is not None:
            planned, actual, confirmed, evidence, confirm_due, confirm_state, delayed_note = project
            db.execute(
                """INSERT INTO construction_projects(contract_id,planned_start_date,actual_start_date,
                   confirmed_start_date,confirmation_evidence,confirmation_due_date,confirmation_status,delayed_note)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (contract_id, planned, actual, confirmed, evidence, confirm_due, confirm_state, delayed_note),
            )
        entitlement_id = None
        if fee_state:
            fee_amount = round(amount * 0.02)
            if dispute:
                fee_amount = dispute["amount"]
            entitlement_id = db.execute(
                """INSERT INTO fee_entitlements(contract_id,introduction_id,fee_rule_id,base_amount,
                   calculated_amount,state,dispute_reason,calculated_at,confirmed_by,
                   invoice_data_generated,reference_amount) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (contract_id, intro_id, fee_rule_ids[partner_id], amount, fee_amount, fee_state,
                 dispute["reason"] if dispute else None, now, users["hq_finance"],
                 1 if fee_state in ("Invoiced", "Paid") else 0,
                 dispute["amount"] if dispute else 0),
            ).lastrowid
            if dispute:
                db.execute(
                    """INSERT INTO referral_disputes(fee_entitlement_id,raised_by,reason,evidence_level,
                       status,dispute_type,reference_amount,due_date) VALUES(?,?,?,?,'Open',?,?,?)""",
                    (entitlement_id, users["manager"], dispute["reason"], dispute["evidence"], dispute["type"],
                     dispute["amount"], today + timedelta(days=7)),
                )
                db.execute(
                    "UPDATE introductions SET status='帰属争議中',existing_customer_flag=1,evidence_note=? WHERE id=?",
                    (dispute["reason"], intro_id),
                )
        return contract_id, intro_id, partner_id, entitlement_id

    for number in range(1, 6):
        amount = 16_500_000 if number == 1 else 32_000_000 + number * 100_000
        create_contract(
            number, amount=amount,
            project=(intake_dates[number - 1] + timedelta(days=60),
                     intake_dates[number - 1] + timedelta(days=75),
                     intake_dates[number - 1] + timedelta(days=77), "着工写真を確認済み",
                     intake_dates[number - 1] + timedelta(days=76), "confirmed", None),
            fee_state="Paid",
        )

    dispute_cases = [
        {"number": 6, "amount": 16_500_000, "fee": 330_000, "type": "referral", "reason": "紹介帰属の確認", "evidence": "A"},
        {"number": 7, "amount": 11_000_000, "fee": 220_000, "type": "amount", "reason": "報酬金額の確認", "evidence": "C"},
        {"number": 8, "amount": 13_750_000, "fee": 275_000, "type": "construction", "reason": "着工証拠の確認", "evidence": "B"},
    ]
    construction_queue = []
    for case in dispute_cases:
        project = (today - timedelta(days=8), today - timedelta(days=5), None, None,
                   today - timedelta(days=2), "evidence_missing", None) if case["type"] == "construction" else None
        contract_id, intro_id, _, _ = create_contract(
            case["number"], amount=case["amount"], project=project, fee_state="Disputed",
            dispute={"reason": case["reason"], "type": case["type"], "amount": case["fee"],
                     "evidence": case["evidence"]},
        )
        if project:
            project_id = db.execute(
                "SELECT id FROM construction_projects WHERE contract_id=?", (contract_id,)
            ).fetchone()["id"]
            construction_queue.append((project_id, case["number"], "evidence_missing", today - timedelta(days=2)))

    for number in range(9, 14):
        create_contract(
            number, amount=32_000_000,
            project=(intake_dates[number - 1] + timedelta(days=60),
                     intake_dates[number - 1] + timedelta(days=75),
                     intake_dates[number - 1] + timedelta(days=77), "着工確認済み",
                     intake_dates[number - 1] + timedelta(days=76), "confirmed", None),
            fee_state="Invoiced",
        )
    for number in range(14, 18):
        create_contract(
            number, amount=30_000_000,
            project=(intake_dates[number - 1] + timedelta(days=60),
                     intake_dates[number - 1] + timedelta(days=75),
                     intake_dates[number - 1] + timedelta(days=77), "証跡確認済み",
                     intake_dates[number - 1] + timedelta(days=76), "confirmed", None),
            fee_state="Pending",
        )

    project_specs = [
        (18, 0, "planned_due", -2), (18, 1, "pending_review", 9),
        (19, 0, "planned_due", -1), (19, 1, "evidence_missing", -5),
        (20, 1, "planned_due_today", 0), (21, 0, "pending_review", -2),
        (22, 0, "delayed", 10),
    ]
    for number, position, state, days_late in project_specs:
        due_date = today + timedelta(days=days_late)
        planned = today - timedelta(days=2) if state == "planned_due" else (
            today if state == "planned_due_today" else today + timedelta(days=10)
            if state == "delayed" else today - timedelta(days=8)
        )
        actual = today - timedelta(days=5) if state in ("evidence_missing", "pending_review") else None
        evidence = "現場写真提出済・審査待ち" if state == "pending_review" else None
        contract_id, _, _, _ = create_contract(
            number, position, 27_500_000,
            project=(planned, actual, None, evidence, due_date, state,
                     "工程調整後に確認予定" if state == "delayed" else None),
        )
        project_id = db.execute(
            "SELECT id FROM construction_projects WHERE contract_id=?", (contract_id,)
        ).fetchone()["id"]
        construction_queue.append((project_id, number, state, due_date))

    for number in range(23, 29):
        project = None
        fee_state = None
        if number in (23, 24):
            project = (today - timedelta(days=10), today - timedelta(days=4),
                       today - timedelta(days=2), "確認証跡を審査済み", today - timedelta(days=3),
                       "confirmed", None)
            fee_state = "Confirmed"
        create_contract(number, amount=28_000_000, project=project, fee_state=fee_state,
                        contract_date_override=today - timedelta(days=2) if number == 28 else None)

    for index, overdue_days in enumerate([1, 2, 3, 5, 6, 9]):
        number = index * 4 + 1
        home = spread_households[number]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               priority,related_type,related_id) VALUES(?,?,?,'sla_auto',?,'followup',?,'household',?)""",
            (home["advisor_id"] or users["manager"], f"DEMO follow-up {home['code']}",
             today - timedelta(days=overdue_days), home["id"],
             "high" if index == 0 else "normal", home["id"]),
        )
    for index, number in enumerate((29, 30, 31, 32)):
        home = spread_households[number]
        intro_id = introductions_by_household[number][0][0]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               related_type,related_id) VALUES(?,?,?,'sla_auto',?,'partner_feedback','introduction',?)""",
            (users["manager"], f"DEMO partner feedback {home['code']}",
             today - timedelta(days=(2, 3, 5, 9)[index]), home["id"], intro_id),
        )
    for project_id, number, state, due in construction_queue:
        home = spread_households[number]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               related_type,related_id) VALUES(?,?,?,'sla_auto',?,'construction_queue','construction_project',?)""",
            (users["manager"], f"DEMO construction queue {project_id}", due, home["id"], project_id),
        )
    for number in (1, 14, 45, 46, 47):
        home = spread_households[number]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               related_type,related_id) VALUES(?,?,?,'sla_auto',?,'appointment','household',?)""",
            (home["advisor_id"] or users["manager"], f"DEMO appointment {home['code']}",
             today, home["id"], home["id"]),
        )
    home = spread_households[2]
    db.execute(
        """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
           related_type,related_id) VALUES(?,?,?,'sla_auto',?,'followup','household',?)""",
        (home["advisor_id"], f"DEMO follow-up {home['code']}", today, home["id"], home["id"]),
    )
    for number in (4, 17, 35, 44):
        home = spread_households[number]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               related_type,related_id) VALUES(?,?,?,'sla_auto',?,'unassigned','household',?)""",
            (users["manager"], f"DEMO unassigned {home['code']}", today, home["id"], home["id"]),
        )
    for number in (15, 25, 40):
        home = spread_households[number]
        intro_id = introductions_by_household[number][0][0]
        db.execute(
            "UPDATE introductions SET advisor_id=NULL WHERE id=?", (intro_id,)
        )
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               related_type,related_id) VALUES(?,?,?,'sla_auto',?,'unassigned','introduction',?)""",
            (users["manager"], f"DEMO unassigned introduction {home['code']}",
             today, home["id"], intro_id),
        )
    for number, task_type in (
        *((i, "fee_approval") for i in range(14, 18)),
        *((i, "invoice_generation") for i in (23, 24)),
        *((i, "invoice_unpaid") for i in range(9, 14)),
        *((i, "dispute") for i in range(6, 9)),
    ):
        home = spread_households[number]
        intro_id = introductions_by_household[number][0][0]
        entitlement = db.execute(
            "SELECT id FROM fee_entitlements WHERE introduction_id=?", (intro_id,)
        ).fetchone()
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               related_type,related_id) VALUES(?,?,?,'sla_auto',?,?,?,?)""",
            (users["hq_finance"], f"DEMO {task_type} {home['code']}", today, home["id"],
             task_type, "introduction" if task_type == "dispute" else "fee_entitlement",
             intro_id if task_type == "dispute" else entitlement["id"]),
        )

    for role, user_id in users.items():
        count = db.execute(
            "SELECT COUNT(*) FROM activities WHERE user_id=? AND DATE(acted_at)=CURRENT_DATE", (user_id,)
        ).fetchone()[0]
        db.execute(
            "INSERT INTO daily_report_drafts(user_id,report_date,auto_summary,manual_note) VALUES(?,?,?,?)",
            (user_id, today, f"本日の活動 {count} 件。デモデータを確認してください。", ""),
        )
    db.execute(
        "INSERT INTO seed_metadata(id,batch_key,seeded_at) VALUES(1,?,?)",
        (SEED_BATCH, now),
    )


for attempt in range(60):
    try:
        with connect() as db:
            seed(db)
            ensure_system_config(db)
        break
    except pymysql.MySQLError:
        if attempt == 59:
            raise
        time.sleep(2)


def role_guard(role, allowed):
    if role not in allowed:
        raise HTTPException(403, "この操作を行う権限がありません")


def require_household_access(db, role, user, household_id):
    household = db.execute(
        "SELECT id,store_id,advisor_id FROM households WHERE id=?", (household_id,)
    ).fetchone()
    if not household:
        raise HTTPException(404, "家庭が見つかりません")
    if role == "advisor" and household["advisor_id"] != user["id"]:
        raise HTTPException(403, "担当世帯以外は操作できません")
    if role == "manager" and household["store_id"] != user["store_id"]:
        raise HTTPException(403, "自店舗以外の世帯は操作できません")
    return household


def role_scope(role, user, household_alias="h"):
    if role == "advisor":
        return f"{household_alias}.advisor_id=?", (user["id"],)
    if role == "manager":
        return f"{household_alias}.store_id=?", (user["store_id"],)
    return "1=1", ()


def get_households(db, role, user):
    scope, args = role_scope(role, user)
    households = [dict(row) for row in db.execute(
        f"""SELECT h.*,s.name AS store_name,u.name AS advisor_name FROM households h
            LEFT JOIN stores s ON s.id=h.store_id LEFT JOIN users u ON u.id=h.advisor_id
            WHERE {scope} ORDER BY h.id""", args,
    )]
    for household in households:
        household_id = household["id"]
        household["persons"] = [dict(row) for row in db.execute(
            "SELECT * FROM persons WHERE household_id=? ORDER BY id", (household_id,)
        )]
        touches = [dict(row) for row in db.execute(
            "SELECT * FROM touches WHERE household_id=? ORDER BY touch_at,id", (household_id,)
        )]
        household["touches"] = touches
        household["first_touch"] = touches[0] if touches else None
        household["latest_touch"] = touches[-1] if touches else None
        household["stage_events"] = [dict(row) for row in db.execute(
            """SELECT e.*,u.name AS changed_by_name FROM stage_events e
               LEFT JOIN users u ON u.id=e.changed_by WHERE household_id=? ORDER BY changed_at,id""",
            (household_id,),
        )]
        household["activities"] = [dict(row) for row in db.execute(
            """SELECT a.*,u.name AS user_name FROM activities a LEFT JOIN users u ON u.id=a.user_id
               WHERE household_id=? ORDER BY acted_at DESC,id DESC""", (household_id,)
        )]
        household["introductions"] = [dict(row) for row in db.execute(
            """SELECT i.*,p.name AS partner_name,ps.name AS staff_name,ps.branch_name,
               n.id AS negotiation_id,n.status AS negotiation_status,n.last_activity_at,
               c.id AS contract_id,c.contract_date,c.contract_amount,cp.id AS project_id,
               cp.planned_start_date,cp.actual_start_date,cp.confirmed_start_date,
               cp.confirmation_evidence,cp.confirmation_due_date,cp.confirmation_status,
               cp.delayed_note,fe.id AS entitlement_id,fe.calculated_amount,
               fe.state AS entitlement_state,fe.dispute_reason,fe.invoice_data_generated,
               fe.reference_amount,fr.version AS rule_version,fr.params AS rule_params,fr.base AS rule_base,
               rd.id AS dispute_id,rd.dispute_type,rd.evidence_level,rd.status AS dispute_status,
               rd.due_date AS dispute_due_date,rd.decision_note
               FROM introductions i JOIN partners p ON p.id=i.partner_id
               LEFT JOIN partner_staff ps ON ps.id=i.partner_staff_id
               LEFT JOIN negotiations n ON n.introduction_id=i.id
               LEFT JOIN contracts c ON c.negotiation_id=n.id
               LEFT JOIN construction_projects cp ON cp.contract_id=c.id
               LEFT JOIN fee_entitlements fe ON fe.introduction_id=i.id
               LEFT JOIN fee_rules fr ON fr.id=fe.fee_rule_id
               LEFT JOIN referral_disputes rd ON rd.fee_entitlement_id=fe.id
               WHERE i.household_id=? ORDER BY i.id""", (household_id,)
        )]
        household["consents"] = [dict(row) for row in db.execute(
            "SELECT * FROM consents WHERE household_id=? ORDER BY granted_at DESC", (household_id,)
        )]
        household["disclosures"] = [dict(row) for row in db.execute(
            "SELECT * FROM data_disclosures WHERE household_id=? ORDER BY disclosed_at DESC", (household_id,)
        )]
    return households


@app.get("/api/bootstrap")
def bootstrap(x_demo_role: str = Header(default="advisor")):
    # This selector is demo-only; production must derive the role from the authenticated identity.
    roles = ("advisor", "manager", "hq_finance", "executive")
    if x_demo_role not in roles:
        raise HTTPException(400, "不明なデモロールです")
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "デモユーザーが見つかりません")
        return {
            "user": {"id": user["id"], "name": user["name"], "role": x_demo_role, "store_id": user["store_id"]},
            "role": x_demo_role,
            "roles": [
                {"id": "advisor", "name": "顧問"}, {"id": "manager", "name": "店長"},
                {"id": "hq_finance", "name": "本社・経理"}, {"id": "executive", "name": "社長"},
            ],
            "permissions": {
                "advisor": ["households.own", "activities.create", "introductions.create"],
                "manager": ["households.store", "construction.confirm", "tasks.store"],
                "hq_finance": ["fees.read", "fees.approve", "invoice_data.manage", "demo.reset"],
                "executive": ["dashboard.all", "management.all", "construction.confirm"],
            }[x_demo_role],
            "menus": ["dashboard", "households", "introductions", "revenue", "management", "settings"],
            "enums": {"stages": STAGES, "roles": list(roles)},
            "environment": {"demo": True, "seed_batch": SEED_BATCH},
        }


@app.get("/api/households")
def household_index(x_demo_role: str = Header(default="advisor")):
    if x_demo_role not in ("advisor", "manager", "hq_finance", "executive"):
        raise HTTPException(400, "不明なデモロールです")
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "デモユーザーが見つかりません")
        households = get_households(db, x_demo_role, user)
        scope, args = role_scope(x_demo_role, user)
        entitlements = [dict(row) for row in db.execute(
            f"""SELECT fe.*,fr.version AS rule_version,fr.type AS rule_type,fr.params,fr.base,
                h.id AS household_id,h.representative_name,h.household_code,p.name AS partner_name,
                c.contract_amount,rd.id AS dispute_id,rd.dispute_type,rd.evidence_level,rd.status AS dispute_status
                FROM fee_entitlements fe JOIN contracts c ON c.id=fe.contract_id
                JOIN introductions i ON i.id=fe.introduction_id JOIN households h ON h.id=i.household_id
                JOIN partners p ON p.id=i.partner_id JOIN fee_rules fr ON fr.id=fe.fee_rule_id
                LEFT JOIN referral_disputes rd ON rd.fee_entitlement_id=fe.id
                WHERE {scope} ORDER BY fe.id""", args,
        )]
        store_scope = "store_id=?" if x_demo_role in ("advisor", "manager") else "1=1"
        stores_scope = "id=?" if x_demo_role in ("advisor", "manager") else "1=1"
        store_args = (user["store_id"],) if x_demo_role in ("advisor", "manager") else ()
        audit_filter = "WHERE a.user_id=?" if x_demo_role in ("advisor", "manager") else ""
        audit_args = (user["id"],) if audit_filter else ()
        daily = db.execute(
            "SELECT * FROM daily_report_drafts WHERE user_id=? ORDER BY id DESC LIMIT 1", (user["id"],)
        ).fetchone()
        return {
            "user": {"id": user["id"], "name": user["name"], "role": x_demo_role, "store_id": user["store_id"]},
            "stores": [dict(row) for row in db.execute(f"SELECT * FROM stores WHERE {stores_scope} ORDER BY id", store_args)],
            "advisors": [dict(row) for row in db.execute(
                f"SELECT id,name,store_id FROM users WHERE role='advisor' AND {store_scope} ORDER BY id",
                store_args,
            )],
            "partners": [dict(row) for row in db.execute("SELECT * FROM partners WHERE active=1 ORDER BY name")],
            "partner_staff": [dict(row) for row in db.execute("SELECT * FROM partner_staff ORDER BY partner_id,id")],
            "households": households, "entitlements": entitlements,
            "audit_logs": [dict(row) for row in db.execute(
                f"""SELECT a.*,u.name AS user_name FROM audit_logs a LEFT JOIN users u ON u.id=a.user_id
                    {audit_filter} ORDER BY a.`at` DESC LIMIT 50""", audit_args,
            )],
            "daily_report": dict(daily) if daily else None,
            "seed_batch": SEED_BATCH,
        }


def request_user(db, role):
    if role not in ("advisor", "manager", "hq_finance", "executive"):
        raise HTTPException(400, "不明なデモロールです")
    user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (role,)).fetchone()
    if not user:
        raise HTTPException(400, "デモユーザーが見つかりません")
    return user


def dashboard_counter(key, label, count, target_page, filter_value, unit_type="items"):
    return {
        "key": key, "label": label, "unit_type": unit_type, "count": int(count),
        "target_page": target_page, "filter": filter_value,
    }


@app.get("/api/dashboard/summary")
def dashboard_summary(x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = request_user(db, x_demo_role)
        counters = []
        if x_demo_role == "advisor":
            counters.extend([
                dashboard_counter("today_followups", "今日フォロー", db.execute(
                    """SELECT COUNT(*) AS count FROM tasks WHERE assignee_id=? AND done=0 AND cancelled=0
                       AND due_at=CURRENT_DATE AND task_type='followup'""", (user["id"],)
                ).fetchone()["count"], "households", "tasks:today_followups"),
                dashboard_counter("overdue", "期限超過", db.execute(
                    """SELECT COUNT(*) AS count FROM tasks WHERE assignee_id=? AND done=0 AND cancelled=0
                       AND due_at<CURRENT_DATE""", (user["id"],)
                ).fetchone()["count"], "households", "tasks:overdue"),
                dashboard_counter("appointments", "本日来店", db.execute(
                    """SELECT COUNT(*) AS count FROM tasks WHERE assignee_id=? AND done=0 AND cancelled=0
                       AND due_at=CURRENT_DATE AND task_type='appointment'""", (user["id"],)
                ).fetchone()["count"], "households", "appointments:today"),
            ])
        elif x_demo_role == "manager":
            counters.extend([
                dashboard_counter("overdue", "店内期限超過", db.execute(
                    """SELECT COUNT(DISTINCT t.id) AS count FROM tasks t LEFT JOIN households h
                       ON h.id=t.related_household_id WHERE h.store_id=? AND t.done=0
                       AND t.cancelled=0 AND t.due_at<CURRENT_DATE""", (user["store_id"],)
                ).fetchone()["count"], "households", "tasks:overdue"),
                dashboard_counter("unassigned", "担当未割当", db.execute(
                    """SELECT COUNT(DISTINCT h.id) AS count FROM households h
                       LEFT JOIN introductions i ON i.household_id=h.id
                       WHERE h.store_id=? AND (h.advisor_id IS NULL OR i.advisor_id IS NULL)""",
                    (user["store_id"],),
                ).fetchone()["count"], "introductions", "unassigned"),
                dashboard_counter("appointments", "本日来店", db.execute(
                    """SELECT COUNT(DISTINCT t.id) AS count FROM tasks t JOIN households h ON h.id=t.related_household_id
                       WHERE h.store_id=? AND t.done=0 AND t.cancelled=0 AND t.task_type='appointment'
                       AND t.due_at=CURRENT_DATE""", (user["store_id"],)
                ).fetchone()["count"], "households", "appointments:today"),
            ])
        elif x_demo_role == "hq_finance":
            counters.extend([
                dashboard_counter("fee_approval", "報酬承認待ち", db.execute(
                    "SELECT COUNT(*) AS count FROM fee_entitlements WHERE state='Pending'"
                ).fetchone()["count"], "revenue", "entitlements:Pending"),
                dashboard_counter("invoice_generation", "請求データ生成待ち", db.execute(
                    """SELECT COUNT(*) AS count FROM fee_entitlements WHERE state='Confirmed'
                       AND invoice_data_generated=0"""
                ).fetchone()["count"], "revenue", "entitlements:invoice_data_pending"),
                dashboard_counter("invoice_unpaid", "請求済・未入金", db.execute(
                    "SELECT COUNT(*) AS count FROM fee_entitlements WHERE state='Invoiced'"
                ).fetchone()["count"], "revenue", "entitlements:Invoiced"),
            ])
        else:
            counters.extend([
                dashboard_counter("critical_risk", "重大業務リスク", db.execute(
                    """SELECT COUNT(*) AS count FROM tasks WHERE done=0 AND cancelled=0 AND priority='high'
                       AND due_at<CURRENT_DATE"""
                ).fetchone()["count"], "households", "tasks:critical"),
                dashboard_counter("disputes", "紹介帰属争議", db.execute(
                    "SELECT COUNT(*) AS count FROM introductions WHERE status='帰属争議中'"
                ).fetchone()["count"], "introductions", "disputed"),
                dashboard_counter("construction_queue", "着工確認滞留", db.execute(
                    """SELECT COUNT(*) AS count FROM construction_projects WHERE confirmed_start_date IS NULL
                       AND confirmation_status IN ('planned_due','planned_due_today','evidence_missing','pending_review','delayed')"""
                ).fetchone()["count"], "revenue", "construction:pending"),
            ])
        return {"role": x_demo_role, "generated_at": datetime.now().isoformat(timespec="seconds"),
                "counters": counters}


@app.get("/api/dashboard/my-tasks")
def dashboard_my_tasks(x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = request_user(db, x_demo_role)
        if x_demo_role == "advisor":
            where = "t.assignee_id=? AND t.done=0 AND t.cancelled=0"
            args = (user["id"],)
        elif x_demo_role == "manager":
            where = """h.store_id=? AND t.done=0 AND t.cancelled=0"""
            args = (user["store_id"],)
        elif x_demo_role == "hq_finance":
            where = """t.task_type IN ('fee_approval','invoice_generation','invoice_unpaid','dispute')
                       AND t.done=0 AND t.cancelled=0"""
            args = ()
        else:
            where = """((t.priority='high' AND t.due_at<CURRENT_DATE)
                       OR t.task_type IN ('dispute','construction_queue'))
                       AND t.done=0 AND t.cancelled=0"""
            args = ()
        rows = db.execute(
            f"""SELECT t.id AS task_id,t.title,t.related_type,t.related_id,t.related_household_id AS household_id,
                t.due_at,t.priority,t.status,
                DATEDIFF(CURRENT_DATE,t.due_at) AS days_overdue,t.task_type
                FROM tasks t LEFT JOIN households h ON h.id=t.related_household_id
                WHERE {where} ORDER BY (t.due_at<CURRENT_DATE) DESC,
                FIELD(t.priority,'high','normal','low'),t.due_at,t.id""", args,
        )
        return {"role": x_demo_role, "items": [
            {"task_id": row["task_id"], "title": row["title"], "related_type": row["related_type"],
             "related_id": row["related_id"], "due_at": row["due_at"],
             "household_id": row["household_id"],
             "days_overdue": max(0, int(row["days_overdue"] or 0)), "priority": row["priority"],
             "status": row["status"], "task_type": row["task_type"]}
            for row in rows
        ]}


@app.get("/api/dashboard/trends")
def dashboard_trends(metric: str = "inquiries", period: str = "7d",
                     x_demo_role: str = Header(default="advisor")):
    if metric not in ("inquiries", "visits", "introductions", "contracts", "construction"):
        raise HTTPException(422, "不明な指標です")
    if period not in ("7d", "30d", "90d", "180d", "365d"):
        raise HTTPException(422, "不明な期間です")
    with connect() as db:
        user = request_user(db, x_demo_role)
        scope, args = role_scope(x_demo_role, user)
        if metric == "inquiries":
            query = f"""SELECT DATE(h.created_at) AS bucket,COUNT(*) AS value FROM households h
                        WHERE {scope} AND h.created_at>=? GROUP BY DATE(h.created_at)"""
        elif metric == "visits":
            query = f"""SELECT DATE(t.acted_at) AS bucket,COUNT(*) AS value FROM activities t
                        JOIN households h ON h.id=t.household_id
                        WHERE {scope} AND t.type IN ('面談','訪問同行') AND t.acted_at>=?
                        GROUP BY DATE(t.acted_at)"""
        elif metric == "introductions":
            query = f"""SELECT DATE(i.introduced_at) AS bucket,COUNT(*) AS value FROM introductions i
                        JOIN households h ON h.id=i.household_id WHERE {scope} AND i.introduced_at>=?
                        GROUP BY DATE(i.introduced_at)"""
        elif metric == "contracts":
            query = f"""SELECT DATE(c.contract_date) AS bucket,COUNT(*) AS value FROM contracts c
                        JOIN negotiations n ON n.id=c.negotiation_id
                        JOIN introductions i ON i.id=n.introduction_id JOIN households h ON h.id=i.household_id
                        WHERE {scope} AND c.contract_date>=? GROUP BY DATE(c.contract_date)"""
        else:
            query = f"""SELECT DATE(cp.confirmed_start_date) AS bucket,COUNT(*) AS value
                        FROM construction_projects cp JOIN contracts c ON c.id=cp.contract_id
                        JOIN negotiations n ON n.id=c.negotiation_id
                        JOIN introductions i ON i.id=n.introduction_id JOIN households h ON h.id=i.household_id
                        WHERE {scope} AND cp.confirmed_start_date>=? GROUP BY DATE(cp.confirmed_start_date)"""
        days = int(period[:-1])
        current_start = date.today() - timedelta(days=days - 1)
        previous_start = current_start - timedelta(days=days)
        results = db.execute(query, (*args, previous_start)).fetchall()
        by_date = {row["bucket"].isoformat(): int(row["value"]) for row in results}
        current = [{"date": (current_start + timedelta(days=index)).isoformat(),
                    "value": by_date.get((current_start + timedelta(days=index)).isoformat(), 0)}
                   for index in range(days)]
        previous = sum(value for key, value in by_date.items() if key < current_start.isoformat())
        current_total = sum(point["value"] for point in current)
        if days >= 90:
            weeks = []
            for week in range((days + 6) // 7):
                start = current_start + timedelta(days=week * 7)
                end = min(start + timedelta(days=6), date.today())
                weeks.append({"start": start.isoformat(), "value": sum(
                    value for key, value in by_date.items() if start.isoformat() <= key <= end.isoformat()
                )})
            current = weeks
        return {"metric": metric, "period": period, "current": current,
                "current_total": current_total, "previous_total": previous}


@app.get("/api/management/overview")
def management_overview(x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("manager", "hq_finance", "executive"))
    with connect() as db:
        user = request_user(db, x_demo_role)
        store_filter = " AND h.store_id=?" if x_demo_role == "manager" else ""
        store_args = (user["store_id"],) if store_filter else ()
        store_clause = " WHERE s.id=?" if x_demo_role == "manager" else ""
        store_clause_args = (user["store_id"],) if store_clause else ()
        stores = db.execute(
            f"""SELECT s.id,s.name,s.opened_at,COUNT(DISTINCT h.id) AS households,
               COUNT(DISTINCT CASE WHEN e.to_stage IN ('紹介済','訪問・商談中') THEN h.id END) AS introductions,
               COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN h.id END) AS contracts
               FROM stores s LEFT JOIN households h ON h.store_id=s.id
               LEFT JOIN stage_events e ON e.household_id=h.id
               LEFT JOIN introductions i ON i.household_id=h.id
               LEFT JOIN negotiations n ON n.introduction_id=i.id
               LEFT JOIN contracts c ON c.negotiation_id=n.id
               {store_clause} GROUP BY s.id ORDER BY s.id""", store_clause_args,
        ).fetchall()
        dimensions = []
        if x_demo_role in ("hq_finance", "executive"):
            for row in db.execute(
                """SELECT h.store_id,COUNT(DISTINCT h.id) AS sample_size,
                   SUM(CASE WHEN h.representative_name<>'' AND h.area_pref<>'' AND
                     h.budget_band<>'' AND h.land_status<>'' THEN 1 ELSE 0 END) AS complete_households,
                   (SELECT COUNT(*) FROM tasks t JOIN households th ON th.id=t.related_household_id
                     WHERE th.store_id=h.store_id AND t.task_type='followup' AND t.cancelled=0) AS followup_total,
                   (SELECT COALESCE(SUM(t.done),0) FROM tasks t JOIN households th
                     ON th.id=t.related_household_id WHERE th.store_id=h.store_id
                     AND t.task_type='followup' AND t.cancelled=0) AS followup_complete,
                   COUNT(DISTINCT CASE WHEN EXISTS(SELECT 1 FROM activities a WHERE a.household_id=h.id
                     AND a.next_action IS NOT NULL AND a.next_action_due IS NOT NULL) THEN h.id END) AS next_action_set,
                   (SELECT COUNT(DISTINCT d.user_id) FROM daily_report_drafts d JOIN users u
                     ON u.id=d.user_id WHERE u.store_id=h.store_id AND d.report_date=CURRENT_DATE) AS report_submitted,
                   (SELECT COUNT(*) FROM users u WHERE u.store_id=h.store_id AND u.role='advisor') AS advisor_count,
                   COUNT(DISTINCT CASE WHEN EXISTS(SELECT 1 FROM activities a WHERE a.household_id=h.id)
                     THEN h.id END) AS responded
                   FROM households h GROUP BY h.store_id ORDER BY h.store_id"""
            ):
                sample_size = max(1, row["sample_size"])
                dimensions.append({
                    "store_id": row["store_id"], "sample_size": row["sample_size"],
                    "followup_rate": round(row["followup_complete"] / max(1, row["followup_total"]), 2),
                    "followup_sample_size": row["followup_total"],
                    "data_completeness": round(row["complete_households"] / sample_size, 2),
                    "next_action_rate": round(row["next_action_set"] / sample_size, 2),
                    "report_submission_rate": round(row["report_submitted"] / max(1, row["advisor_count"]), 2),
                    "response_rate": round(row["responded"] / sample_size, 2),
                })
        sla_days = {row["reminder_type"]: row["days_before"] for row in db.execute(
            "SELECT reminder_type,days_before FROM sla_settings"
        )}
        reminders = [
            {"key": "introduction_validity", "label": "紹介有効期間", "target_page": "introductions",
             "filter": "validity:due", "items": db.execute(
                f"""SELECT i.id,h.representative_name,i.valid_until AS due_at FROM introductions i
                    JOIN households h ON h.id=i.household_id WHERE i.valid_until BETWEEN CURRENT_DATE
                    AND DATE_ADD(CURRENT_DATE,INTERVAL ? DAY){store_filter}
                    ORDER BY i.valid_until LIMIT 20""", (sla_days["introduction_validity"],) + store_args).fetchall()},
            {"key": "construction_evidence", "label": "着工証拠提出期限", "target_page": "revenue",
             "filter": "construction:evidence_missing", "items": db.execute(
                f"""SELECT cp.id,h.representative_name,cp.confirmation_due_date AS due_at
                    FROM construction_projects cp JOIN contracts c ON c.id=cp.contract_id
                    JOIN negotiations n ON n.id=c.negotiation_id JOIN introductions i ON i.id=n.introduction_id
                    JOIN households h ON h.id=i.household_id WHERE cp.confirmation_status='evidence_missing'
                    AND cp.confirmation_due_date<=DATE_ADD(CURRENT_DATE,INTERVAL ? DAY)
                    {store_filter} ORDER BY cp.confirmation_due_date LIMIT 20""",
                (sla_days["construction_evidence"],) + store_args).fetchall()},
            {"key": "dispute_resolution", "label": "争議処理期限", "target_page": "revenue",
             "filter": "disputed", "items": db.execute(
                f"""SELECT d.id,h.representative_name,d.due_date AS due_at FROM referral_disputes d
                    JOIN fee_entitlements fe ON fe.id=d.fee_entitlement_id
                    JOIN introductions i ON i.id=fe.introduction_id JOIN households h ON h.id=i.household_id
                    WHERE d.status IN ('Open','UnderReview')
                    AND (d.due_date IS NULL OR d.due_date<=DATE_ADD(CURRENT_DATE,INTERVAL ? DAY)){store_filter}
                    ORDER BY d.due_date LIMIT 20""",
                (sla_days["dispute_resolution"],) + store_args).fetchall()},
            {"key": "agreement_renewal", "label": "提携契約更新期限", "target_page": "management",
             "filter": "agreements:expiring", "items": db.execute(
                """SELECT pa.id,p.name AS representative_name,pa.effective_to AS due_at
                   FROM partner_agreements pa JOIN partners p ON p.id=pa.partner_id
                   WHERE pa.effective_to BETWEEN CURRENT_DATE AND DATE_ADD(CURRENT_DATE,INTERVAL ? DAY)
                   ORDER BY pa.effective_to LIMIT 20""",
                (sla_days["agreement_renewal"],)).fetchall() if not store_filter else []},
            {"key": "fee_rule_validity", "label": "FeeRule適用期限", "target_page": "management",
             "filter": "fee_rules:expiring", "items": db.execute(
                """SELECT fr.id,fr.version AS representative_name,fr.effective_to AS due_at
                   FROM fee_rules fr WHERE fr.effective_to BETWEEN CURRENT_DATE
                   AND DATE_ADD(CURRENT_DATE,INTERVAL ? DAY) ORDER BY fr.effective_to LIMIT 20""",
                (sla_days["fee_rule_validity"],)).fetchall() if not store_filter else []},
        ]
        channels = [dict(row) for row in db.execute(
            f"""SELECT t.channel,COUNT(*) AS touches,COUNT(DISTINCT t.household_id) AS households,
               COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN t.household_id END) AS contracts
               FROM touches t JOIN households h ON h.id=t.household_id
               LEFT JOIN introductions i ON i.household_id=h.id LEFT JOIN negotiations n ON n.introduction_id=i.id
               LEFT JOIN contracts c ON c.negotiation_id=n.id WHERE 1=1{store_filter}
               GROUP BY t.channel ORDER BY touches DESC""", store_args,
        )]
        cohorts = [dict(row) for row in db.execute(
            f"""SELECT DATE_FORMAT(h.created_at,'%%Y-%%m') AS cohort,COUNT(DISTINCT h.id) AS inquiries,
               COUNT(DISTINCT i.id) AS introductions,COUNT(DISTINCT c.id) AS contracts
               FROM households h LEFT JOIN introductions i ON i.household_id=h.id
               LEFT JOIN negotiations n ON n.introduction_id=i.id
               LEFT JOIN contracts c ON c.negotiation_id=n.id WHERE 1=1{store_filter}
               GROUP BY cohort ORDER BY cohort""", store_args,
        )]
        partner_quality = [dict(row) for row in db.execute(
            f"""SELECT p.id,p.name,COUNT(DISTINCT i.id) AS introductions,
               COUNT(DISTINCT CASE WHEN fe.state='Disputed' THEN fe.id END) AS disputes,
               COUNT(DISTINCT CASE WHEN fe.state='Paid' THEN fe.id END) AS paid,
               COALESCE(SUM(CASE WHEN fe.state='Paid' THEN fe.calculated_amount ELSE 0 END),0) AS paid_amount
               FROM partners p LEFT JOIN introductions i ON i.partner_id=p.id
               LEFT JOIN households h ON h.id=i.household_id
               LEFT JOIN fee_entitlements fe ON fe.introduction_id=i.id WHERE 1=1{store_filter}
               GROUP BY p.id ORDER BY p.id""", store_args,
        )]
        store_results = []
        for row in stores:
            item = dict(row)
            opened = item["opened_at"]
            if opened:
                item["tenure_months"] = max(0, (date.today().year - opened.year) * 12 + date.today().month - opened.month)
            else:
                item["tenure_months"] = None
            item["case_volume_band"] = f"{(item['households'] // 5) * 5}–{(item['households'] // 5) * 5 + 4}"
            store_results.append(item)
        return {
            "stores": store_results,
            "operations_dimensions": dimensions,
            "reminders": [{**item, "items": [dict(row) for row in item["items"]]} for item in reminders],
            "attribution": channels, "cohorts": cohorts, "partner_quality": partner_quality,
        }


@app.get("/api/preferences")
def get_preferences(x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = request_user(db, x_demo_role)
        row = db.execute("SELECT * FROM user_preferences WHERE user_id=?", (user["id"],)).fetchone()
        return {
            "dashboard_widgets": json.loads(row["dashboard_widgets"]) if row else (
                ["tasks", "report"] if x_demo_role == "advisor" else ["tasks", "overview", "trend"]
            ),
            "notification_preferences": json.loads(row["notification_preferences"]) if row else {"in_app": True, "email": False},
        }


class PreferencesInput(BaseModel):
    dashboard_widgets: list[str]
    notification_preferences: dict


@app.put("/api/preferences")
def put_preferences(payload: PreferencesInput, x_demo_role: str = Header(default="advisor")):
    allowed_widgets = {"tasks", "overview", "trend", "report"}
    if len(payload.dashboard_widgets) > 4 or not set(payload.dashboard_widgets).issubset(allowed_widgets):
        raise HTTPException(422, "ダッシュボード設定が正しくありません")
    if set(payload.notification_preferences) - {"in_app", "email"}:
        raise HTTPException(422, "通知設定が正しくありません")
    with connect() as db:
        user = request_user(db, x_demo_role)
        db.execute(
            """INSERT INTO user_preferences(user_id,dashboard_widgets,notification_preferences,updated_at)
               VALUES(?,?,?,?) ON DUPLICATE KEY UPDATE dashboard_widgets=VALUES(dashboard_widgets),
               notification_preferences=VALUES(notification_preferences),updated_at=VALUES(updated_at)""",
            (user["id"], json.dumps(payload.dashboard_widgets),
             json.dumps(payload.notification_preferences), datetime.now().isoformat(timespec="seconds")),
        )
        return {"ok": True}


class ActivityInput(BaseModel):
    household_id: int
    type: str
    body: str
    next_action: Optional[str] = None
    next_action_due: Optional[str] = None


@app.post("/api/activities")
def create_activity(payload: ActivityInput, x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=?", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        require_household_access(db, x_demo_role, user, payload.household_id)
        db.execute(
            """INSERT INTO activities(household_id,user_id,type,body,acted_at,next_action,next_action_due)
               VALUES(?,?,?,?,?,?,?)""",
            (payload.household_id, user["id"], payload.type, payload.body,
             datetime.now().isoformat(timespec="seconds"), payload.next_action, payload.next_action_due),
        )
        if payload.next_action and payload.next_action_due:
            overdue_task = db.execute(
                """SELECT id FROM tasks WHERE assignee_id=? AND related_household_id=?
                   AND task_type='followup' AND done=0 AND cancelled=0 AND due_at<CURRENT_DATE
                   ORDER BY due_at,id LIMIT 1""", (user["id"], payload.household_id),
            ).fetchone()
            if overdue_task:
                db.execute("UPDATE tasks SET done=1,status='done' WHERE id=?", (overdue_task["id"],))
        audit(db, user["id"], "activity.created", "household", payload.household_id, payload.type)
        db.commit()
    return {"ok": True}


class IntroductionInput(BaseModel):
    household_id: int
    partner_id: int
    partner_staff_id: int


@app.post("/api/introductions")
def create_introduction(payload: IntroductionInput, x_demo_role: str = Header(default="advisor")):
    if x_demo_role not in ("advisor", "manager", "hq_finance"):
        raise HTTPException(403, "権限がありません")
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=?", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        household = require_household_access(db, x_demo_role, user, payload.household_id)
        staff = db.execute("SELECT id FROM partner_staff WHERE id=? AND partner_id=?",
                           (payload.partner_staff_id, payload.partner_id)).fetchone()
        if not household or not staff:
            raise HTTPException(404, "家庭または住宅会社担当者が見つかりません")
        now = datetime.now().isoformat(timespec="seconds")
        intro_id = db.execute(
            """INSERT INTO introductions(household_id,partner_id,partner_staff_id,introduced_at,status)
               VALUES(?,?,?,?,'紹介済')""",
            (payload.household_id, payload.partner_id, payload.partner_staff_id, now),
        ).lastrowid
        db.execute("INSERT INTO negotiations(introduction_id,status,last_activity_at) VALUES(?,'訪問予定',?)", (intro_id, now))
        latest = db.execute("SELECT to_stage FROM stage_events WHERE household_id=? ORDER BY changed_at DESC LIMIT 1",
                            (payload.household_id,)).fetchone()
        if not latest or latest["to_stage"] != "紹介済":
            db.execute(
                "INSERT INTO stage_events(household_id,from_stage,to_stage,changed_by,changed_at) VALUES(?,?,?, ?,?)",
                (payload.household_id, latest["to_stage"] if latest else None, "紹介済",
                 user["id"], now),
            )
        user_id = user["id"]
        audit(db, user_id, "introduction.created", "introduction", intro_id, f"partner={payload.partner_id}")
        db.commit()
    return {"ok": True, "introduction_id": intro_id}


class ConfirmInput(BaseModel):
    confirmed_start_date: str
    evidence: str


@app.post("/api/construction/{project_id}/confirm")
def confirm_construction(project_id: int, payload: ConfirmInput, x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("manager", "hq_finance", "executive"))
    with connect() as db:
        project = db.execute(
            """SELECT cp.*,c.contract_amount,i.id AS introduction_id,i.partner_id,h.store_id
               FROM construction_projects cp JOIN contracts c ON c.id=cp.contract_id
               JOIN negotiations n ON n.id=c.negotiation_id
               JOIN introductions i ON i.id=n.introduction_id
               JOIN households h ON h.id=i.household_id WHERE cp.id=?""", (project_id,)
        ).fetchone()
        if not project:
            raise HTTPException(404, "着工プロジェクトが見つかりません")
        if x_demo_role == "manager":
            manager = db.execute("SELECT store_id FROM users WHERE role=?", (x_demo_role,)).fetchone()
            if project["store_id"] != manager["store_id"]:
                raise HTTPException(403, "自店舗以外の着工案件は処理できません")
        if not project["actual_start_date"]:
            raise HTTPException(409, "実際着工日が未登録です")
        if not payload.evidence.strip():
            raise HTTPException(422, "確認証跡を入力してください")
        rule = db.execute(
            """SELECT fr.* FROM partner_agreements pa JOIN fee_rules fr ON fr.id=pa.fee_rule_id
               WHERE pa.partner_id=? AND pa.status='active' AND pa.effective_from<=?
               AND (pa.effective_to IS NULL OR pa.effective_to>=?) ORDER BY pa.effective_from DESC LIMIT 1""",
            (project["partner_id"], date.today().isoformat(), date.today().isoformat()),
        ).fetchone()
        if not rule:
            raise HTTPException(409, "適用可能な報酬ルールがありません")
        params = json.loads(rule["params"])
        params = rule["params"]
        if isinstance(params, str):
            params = json.loads(params)
        if rule["type"] == "rate":
            amount = round(project["contract_amount"] * float(params["rate"]))
        elif rule["type"] == "fixed":
            amount = int(params["amount"])
        else:
            tiers = params["tiers"]
            amount = next((int(t["amount"]) for t in tiers if project["contract_amount"] <= t["up_to"]), int(tiers[-1]["amount"]))
        user_id = db.execute("SELECT id FROM users WHERE role=?", (x_demo_role,)).fetchone()["id"]
        db.execute("UPDATE construction_projects SET confirmed_start_date=?,confirmation_evidence=? WHERE id=?",
                   (payload.confirmed_start_date, payload.evidence.strip(), project_id))
        db.execute(
            """UPDATE tasks SET done=1,status='done' WHERE related_type='construction_project'
               AND related_id=? AND task_type='construction_queue'""", (project_id,)
        )
        existing = db.execute("SELECT id FROM fee_entitlements WHERE contract_id=?", (project["contract_id"],)).fetchone()
        if not existing:
            intro_status = db.execute("SELECT status FROM introductions WHERE id=?", (project["introduction_id"],)).fetchone()["status"]
            state = "Disputed" if intro_status == "帰属争议中" else "Confirmed"
            db.execute(
                """INSERT INTO fee_entitlements(contract_id,introduction_id,fee_rule_id,base_amount,
                   calculated_amount,state,dispute_reason,calculated_at,confirmed_by) VALUES(?,?,?,?,?,?,?,?,?)""",
                (project["contract_id"], project["introduction_id"], rule["id"], project["contract_amount"],
                 amount, state, "紹介帰属の確認中" if state == "Disputed" else None,
                 datetime.now().isoformat(timespec="seconds"), user_id),
            )
        audit(db, user_id, "construction.confirmed", "construction_project", project_id,
              f"evidence={payload.evidence.strip()}; fee={amount}")
        db.commit()
    return {"ok": True, "calculated_amount": amount, "rule_version": rule["version"]}


class EntitlementAction(BaseModel):
    action: str


@app.post("/api/entitlements/{entitlement_id}/action")
def entitlement_action(entitlement_id: int, payload: EntitlementAction,
                       x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("hq_finance",))
    transitions = {"approve": ("Pending", "Confirmed"), "invoice": ("Confirmed", "Invoiced"),
                   "paid": ("Invoiced", "Paid")}
    if payload.action not in transitions:
        raise HTTPException(422, "不明な状態変更です")
    with connect() as db:
        entitlement = db.execute("SELECT * FROM fee_entitlements WHERE id=?", (entitlement_id,)).fetchone()
        if not entitlement:
            raise HTTPException(404, "報酬権利が見つかりません")
        source, target = transitions[payload.action]
        if entitlement["state"] != source:
            raise HTTPException(409, f"{source} 状態の報酬のみ処理できます")
        user_id = db.execute("SELECT id FROM users WHERE role='hq_finance'").fetchone()["id"]
        db.execute(
            "UPDATE fee_entitlements SET state=?,invoice_data_generated=IF(?='Invoiced',1,invoice_data_generated) WHERE id=?",
            (target, target, entitlement_id),
        )
        task_type = {"approve": "fee_approval", "invoice": "invoice_generation", "paid": "invoice_unpaid"}[payload.action]
        db.execute(
            "UPDATE tasks SET done=1,status='done' WHERE related_type='fee_entitlement' AND related_id=? AND task_type=?",
            (entitlement_id, task_type),
        )
        audit(db, user_id, f"entitlement.{payload.action}", "fee_entitlement", entitlement_id, target)
        db.commit()
    return {"ok": True, "state": target}


class DisputeInput(BaseModel):
    reason: str
    evidence_level: str


@app.post("/api/introductions/{introduction_id}/dispute")
def raise_dispute(introduction_id: int, payload: DisputeInput,
                  x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=?", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        intro = db.execute("SELECT id,household_id FROM introductions WHERE id=?", (introduction_id,)).fetchone()
        if not intro:
            raise HTTPException(404, "紹介記録が見つかりません")
        require_household_access(db, x_demo_role, user, intro["household_id"])
        if not payload.reason.strip():
            raise HTTPException(422, "争議理由を入力してください")
        entitlement = db.execute("SELECT * FROM fee_entitlements WHERE introduction_id=?", (introduction_id,)).fetchone()
        if entitlement and entitlement["state"] in ("Invoiced", "Paid"):
            raise HTTPException(409, "請求後の金額は争議状態に変更できません。調整記録が必要です")
        if entitlement:
            db.execute("UPDATE fee_entitlements SET state='Disputed',dispute_reason=? WHERE id=?",
                       (payload.reason.strip(), entitlement["id"]))
            db.execute(
                """INSERT INTO referral_disputes(fee_entitlement_id,raised_by,reason,evidence_level,status)
                   VALUES(?,?,?,?,'Open')""",
                (entitlement["id"], user["id"], payload.reason.strip(), payload.evidence_level),
            )
        db.execute("UPDATE introductions SET status='帰属争议中',existing_customer_flag=1,evidence_note=? WHERE id=?",
                   (payload.reason.strip(), introduction_id))
        audit(db, user["id"], "referral_dispute.raised", "introduction", introduction_id, payload.evidence_level)
        db.commit()
    return {"ok": True}


class DisputeDecisionInput(BaseModel):
    decision: str
    decision_note: str


@app.post("/api/referral-disputes/{dispute_id}/decision")
def decide_referral_dispute(dispute_id: int, payload: DisputeDecisionInput,
                            x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("hq_finance",))
    if payload.decision not in ("confirm", "write_off", "reassessment"):
        raise HTTPException(422, "不明な裁定です")
    note = payload.decision_note.strip()
    if len(note) < 5:
        raise HTTPException(422, "裁定理由を5文字以上で入力してください")
    with connect() as db:
        user = request_user(db, x_demo_role)
        dispute = db.execute(
            """SELECT d.*,fe.introduction_id FROM referral_disputes d
               JOIN fee_entitlements fe ON fe.id=d.fee_entitlement_id WHERE d.id=?""",
            (dispute_id,),
        ).fetchone()
        if not dispute:
            raise HTTPException(404, "争議記録が見つかりません")
        if dispute["status"] in ("Decided", "WrittenOff"):
            raise HTTPException(409, "裁定済みの争議です")
        target_status = "Reassessment" if payload.decision == "reassessment" else "Decided"
        db.execute(
            """UPDATE referral_disputes SET status=?,decided_by=?,decided_at=?,decision_note=?
               WHERE id=?""",
            (target_status, user["id"], datetime.now().isoformat(timespec="seconds"), note, dispute_id),
        )
        if payload.decision == "confirm":
            db.execute(
                "UPDATE fee_entitlements SET state='Confirmed',dispute_reason=NULL WHERE id=?",
                (dispute["fee_entitlement_id"],),
            )
            db.execute(
                "UPDATE introductions SET status='受付確認済' WHERE id=?", (dispute["introduction_id"],)
            )
        elif payload.decision == "write_off":
            db.execute(
                "UPDATE fee_entitlements SET state='WrittenOff' WHERE id=?", (dispute["fee_entitlement_id"],)
            )
            db.execute("UPDATE introductions SET status='見送り' WHERE id=?", (dispute["introduction_id"],))
        if payload.decision != "reassessment":
            db.execute(
                """UPDATE tasks SET done=1,status='done' WHERE related_type='introduction'
                   AND related_id=? AND task_type='dispute'""", (dispute["introduction_id"],)
            )
        audit(db, user["id"], "referral_dispute.decided", "referral_dispute", dispute_id,
              f"decision={payload.decision}; {note}")
        db.commit()
    return {"ok": True, "status": target_status}


class StageInput(BaseModel):
    to_stage: str


@app.post("/api/households/{household_id}/stage")
def change_stage(household_id: int, payload: StageInput, x_demo_role: str = Header(default="advisor")):
    if payload.to_stage not in STAGES:
        raise HTTPException(422, "不明なステージです")
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=?", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        require_household_access(db, x_demo_role, user, household_id)
        current = db.execute("SELECT to_stage FROM stage_events WHERE household_id=? ORDER BY changed_at DESC LIMIT 1",
                             (household_id,)).fetchone()
        if not current:
            raise HTTPException(404, "家庭が見つかりません")
        db.execute(
            """INSERT INTO stage_events(household_id,from_stage,to_stage,changed_by,changed_at)
               VALUES(?,?,?,?,?)""",
            (household_id, current["to_stage"], payload.to_stage, user["id"],
             datetime.now().isoformat(timespec="seconds")),
        )
        audit(db, user["id"], "stage.changed", "household", household_id, payload.to_stage)
        db.commit()
    return {"ok": True}


class ReportInput(BaseModel):
    manual_note: str = ""


class SystemConfigInput(BaseModel):
    value: object
    reason: str


@app.get("/api/system-config")
def get_system_config(x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("hq_finance",))
    with connect() as db:
        rows = db.execute(
            """SELECT c.config_key,c.value_json,c.updated_at,u.name AS updated_by_name
               FROM system_configs c LEFT JOIN users u ON u.id=c.updated_by ORDER BY c.config_key"""
        )
        return {"items": [
            {
                "key": row["config_key"],
                "value": json.loads(row["value_json"]) if isinstance(row["value_json"], str) else row["value_json"],
                "updated_at": row["updated_at"],
                "updated_by": row["updated_by_name"],
            }
            for row in rows
        ]}


@app.put("/api/system-config/{config_key}")
def update_system_config(config_key: str, payload: SystemConfigInput,
                         x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("hq_finance",))
    if config_key not in SYSTEM_CONFIG_DEFAULTS:
        raise HTTPException(404, "不明な設定項目です")
    if not valid_config_value(config_key, payload.value):
        raise HTTPException(422, "設定値の形式または範囲が正しくありません")
    reason = payload.reason.strip()
    if not 10 <= len(reason) <= 500:
        raise HTTPException(422, "変更理由は10〜500文字で入力してください")
    with connect() as db:
        user = db.execute("SELECT id FROM users WHERE role=?", (x_demo_role,)).fetchone()
        current = db.execute(
            "SELECT value_json FROM system_configs WHERE config_key=? FOR UPDATE", (config_key,)
        ).fetchone()
        if not current:
            raise HTTPException(404, "設定項目が見つかりません")
        previous_value = current["value_json"]
        if isinstance(previous_value, str):
            previous_value = json.loads(previous_value)
        db.execute(
            "UPDATE system_configs SET value_json=?,updated_at=?,updated_by=? WHERE config_key=?",
            (json.dumps(payload.value, ensure_ascii=False, sort_keys=True),
             datetime.now().isoformat(timespec="seconds"), user["id"], config_key),
        )
        if any(config_key == item[1] for item in SLA_CONFIG):
            sync_sla_settings(db)
        audit(db, user["id"], "system_config.updated", "system_config", None,
              f"key={config_key}; before={json.dumps(previous_value, ensure_ascii=False, sort_keys=True)}; "
              f"after={json.dumps(payload.value, ensure_ascii=False, sort_keys=True)}; reason={reason}")
    return {"ok": True}


@app.put("/api/report")
def save_report(payload: ReportInput, x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = db.execute("SELECT id FROM users WHERE role=?", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        today = date.today().isoformat()
        count = db.execute("SELECT COUNT(*) FROM activities WHERE user_id=? AND DATE(acted_at)=CURRENT_DATE",
                           (user["id"],)).fetchone()[0]
        summary = f"本日の活動 {count} 件。面談・紹介状況を確認してください。"
        existing = db.execute("SELECT id FROM daily_report_drafts WHERE user_id=? AND report_date=?",
                              (user["id"], today)).fetchone()
        if existing:
            db.execute("UPDATE daily_report_drafts SET auto_summary=?,manual_note=? WHERE id=?",
                       (summary, payload.manual_note, existing["id"]))
        else:
            db.execute("INSERT INTO daily_report_drafts(user_id,report_date,auto_summary,manual_note) VALUES(?,?,?,?)",
                       (user["id"], today, summary, payload.manual_note))
        db.commit()
    return {"ok": True}


@app.post("/api/reset")
def reset_demo(x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("hq_finance",))
    with connect() as db:
        for table in TABLES:
            db.execute(f"DROP TABLE IF EXISTS `{table}`")
        seed(db)
        ensure_system_config(db)
    return {"ok": True}


@app.get("/api/health")
def health():
    with connect() as db:
        db.execute("SELECT 1")
    return {"status": "ok"}


DIST = ROOT / "frontend" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    def frontend(path: str):
        candidate = DIST / path
        return FileResponse(candidate if candidate.is_file() else DIST / "index.html")
