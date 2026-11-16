import json
import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import pymysql
from pymysql.cursors import DictCursor
from fastapi import FastAPI, Header, HTTPException, Query
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
  id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120) NOT NULL, area VARCHAR(120) NOT NULL, opened_at DATE NULL
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
  id INT AUTO_INCREMENT PRIMARY KEY, partner_id INT NOT NULL, name VARCHAR(120) NOT NULL, branch_name VARCHAR(120),
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
  invoice_data_generated TINYINT NOT NULL DEFAULT 0,
  reference_amount BIGINT NOT NULL DEFAULT 0,
  FOREIGN KEY (contract_id) REFERENCES contracts(id), FOREIGN KEY (introduction_id) REFERENCES introductions(id),
  FOREIGN KEY (fee_rule_id) REFERENCES fee_rules(id), FOREIGN KEY (confirmed_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS referral_disputes (
  id INT AUTO_INCREMENT PRIMARY KEY, fee_entitlement_id INT NOT NULL, raised_by INT NOT NULL,
  reason TEXT NOT NULL, evidence_level VARCHAR(8) NOT NULL, status VARCHAR(40) NOT NULL, decided_by INT,
  decided_at DATETIME, decision_note TEXT, due_date DATE NULL, dispute_type VARCHAR(40) NOT NULL DEFAULT 'referral',
  reference_amount BIGINT NOT NULL DEFAULT 0, FOREIGN KEY (fee_entitlement_id) REFERENCES fee_entitlements(id),
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
CREATE TABLE IF NOT EXISTS seed_metadata (
  id TINYINT PRIMARY KEY, batch_key VARCHAR(80) NOT NULL, seeded_at DATETIME NOT NULL
);
CREATE TABLE IF NOT EXISTS sla_settings (
  reminder_type VARCHAR(40) PRIMARY KEY, days_before INT NOT NULL, label_ja VARCHAR(120) NOT NULL,
  label_zh VARCHAR(120) NOT NULL
);
"""

TABLES = [
    "audit_logs", "daily_report_drafts", "tasks", "data_disclosures", "consents", "referral_disputes",
    "fee_entitlements", "construction_projects", "contracts", "negotiations", "introductions",
    "partner_agreements", "fee_rules", "partner_staff", "partners", "stage_events", "activities",
    "touches", "persons", "households", "users", "stores",
    "seed_metadata", "sla_settings",
]

STORES = [
    ("店舗A", "東京"), ("店舗B", "東京"), ("店舗C", "東京"), ("店舗D", "神奈川"),
    ("店舗E", "神奈川"), ("店舗F", "埼玉"), ("店舗G", "千葉"), ("店舗H", "千葉"),
    ("店舗I", "愛知"), ("店舗J", "大阪"), ("店舗K", "兵庫"), ("店舗L", "福岡"),
]
STAGES = ["新規予約", "初回相談済", "FP診断済", "紹介済", "訪問・商談中", "契約", "着工", "完了・見送り"]
SEED_BATCH = "mallboard-demo-2026-11-p0-v1"
SAMPLE_SURNAMES = ["佐藤", "田中", "鈴木", "高橋", "伊藤", "渡辺", "山本", "中村", "小林", "加藤", "吉田", "山田"]


def connect():
    return Database(pymysql.connect(**DB_CONFIG))


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
    db.execute(
        "INSERT INTO audit_logs(user_id, action, target_type, target_id, `at`, detail) VALUES(?,?,?,?,?,?)",
        (user_id, action, target_type, target_id, datetime.now().isoformat(timespec="seconds"), detail),
    )


def seed(db):
    ensure_schema(db)
    if db.execute("SELECT COUNT(*) FROM seed_metadata WHERE id=1").fetchone()[0]:
        return
    if db.execute("SELECT COUNT(*) FROM stores").fetchone()[0]:
        return
    now = datetime.now().replace(microsecond=0)
    today = date.today()
    db.executemany("INSERT INTO stores(name,area,opened_at) VALUES(?,?,?)",
                   [(name, area, date(2020 + (index % 5), (index % 12) + 1, 1))
                    for index, (name, area) in enumerate(STORES)])
    user_ids = {}
    for name, role, store_id in [("佐藤 美咲", "advisor", 1), ("田中 健", "manager", 3),
                                 ("山本 経理", "hq_finance", None), ("山田 社長", "executive", None)]:
        user_ids[role] = db.execute("INSERT INTO users(name,role,store_id) VALUES(?,?,?)",
                                    (name, role, store_id)).lastrowid
    advisor_ids = [user_ids["advisor"]]
    for store_id in range(2, 13):
        advisor_ids.append(db.execute("INSERT INTO users(name,role,store_id) VALUES(?,?,?)",
                                      (f"デモ顧問 {store_id:02}", "advisor", store_id)).lastrowid)

    month_counts = [(6, 7), (7, 8), (8, 10), (9, 12), (10, 14), (11, 9)]
    intake_dates = []
    current_year = 2026
    for month, count in month_counts:
        start = date(current_year, month, 1)
        end = date(current_year + (month == 12), (month % 12) + 1, 1)
        days = (end - start).days
        intake_dates.extend(start + timedelta(days=(index * 3) % days) for index in range(count))
    intake_dates[-1] = date(2026, 11, 16)

    spread = [6, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4]
    store_ids = [store_id for store_id, count in enumerate(spread, 1) for _ in range(count)]
    household_names = {
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
    double_households = set(range(24, 36))
    triple_households = set(range(18, 24))
    introduced_households = set(range(1, 45)) | set(range(52, 56))
    fee_rule_ids = {}
    for partner_id in range(1, 13):
        name = f"住宅会社{chr(64 + partner_id)}"
        area = STORES[(partner_id - 1) % len(STORES)][1]
        db.execute("INSERT INTO partners(id,name,area,tags,active) VALUES(?,?,?,?,1)",
                   (partner_id, name, area, json.dumps(["価格", "性能"], ensure_ascii=False)))
        for branch_index in range(1, 3):
            db.execute("INSERT INTO partner_staff(partner_id,name,branch_name) VALUES(?,?,?)",
                       (partner_id, f"担当者{chr(64 + branch_index)}", f"支店{chr(64 + branch_index)}"))
        old_rule = db.execute(
            """INSERT INTO fee_rules(version,type,params,base,effective_from,approved_by)
               VALUES(?, 'rate', ?, '請負金額', '2025-01-01', ?)""",
            (f"2025.{partner_id}", '{"rate":0.018}', user_ids["hq_finance"]),
        ).lastrowid
        current_rule = db.execute(
            """INSERT INTO fee_rules(version,type,params,base,effective_from,effective_to,approved_by)
               VALUES(?, 'rate', ?, '請負金額', '2026-01-01', ?, ?)""",
            (f"2026.{partner_id}", '{"rate":0.02}',
             today + timedelta(days=20) if partner_id == 1 else None, user_ids["hq_finance"]),
        ).lastrowid
        fee_rule_ids[partner_id] = current_rule
        db.execute("INSERT INTO partner_agreements(partner_id,effective_from,effective_to,fee_rule_id,status) VALUES(?,?,?,?,?)",
                   (partner_id, "2025-01-01", "2025-12-31", old_rule, "expired"))
        db.execute(
            """INSERT INTO partner_agreements(partner_id,effective_from,effective_to,fee_rule_id,status)
               VALUES(?,?,?,?, 'active')""",
            (partner_id, "2026-01-01", today + timedelta(days=15) if partner_id == 1 else None, current_rule),
        )

    for i in range(1, 61):
        household_code = f"HH-D{i:03}"
        store_id = store_ids[i - 1]
        advisor_id = advisor_ids[store_id - 1]
        if i in (4, 17, 35, 44):
            advisor_id = None
        status_name = household_names[i]
        status = "lost" if status_name == "解約済" else "completed" if status_name in ("入金済", "解約済") else "active"
        intake_at = datetime.combine(intake_dates[i - 1], datetime.min.time())
        sample_name = f"{SAMPLE_SURNAMES[(i - 1) % len(SAMPLE_SURNAMES)]}{chr(65 + (i - 1) // len(SAMPLE_SURNAMES))}"
        household_id = db.execute(
            """INSERT INTO households(household_code,representative_name,store_id,advisor_id,budget_band,
               area_pref,land_status,status,created_at,lost_reason)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (household_code, sample_name, store_id, advisor_id,
             ("4,000〜5,000万円", "5,000〜6,000万円", "6,000〜7,000万円")[i % 3],
             f"{STORES[store_id - 1][1]}エリア", ("有", "無", "検討中")[i % 3], status, intake_at,
             "デモ見送り" if status == "lost" else None),
        ).lastrowid
        db.execute("INSERT INTO persons(household_id,name,relation,phone,email) VALUES(?,?,?,?,?)",
                   (household_id, f"{sample_name} 本人", "本人", f"090-0000-{i:04}", f"demo{i:03}@example.test"))
        for touch_index, channel in enumerate(("Web広告", "直接来店")):
            touch_at = intake_at + timedelta(days=touch_index * 3)
            db.execute(
                """INSERT INTO touches(household_id,touch_at,channel,campaign_id,creative_id,
                   tracking_code,landing_referrer,store_id,capture_method) VALUES(?,?,?,?,?,?,?,?,?)""",
                (household_id, touch_at, channel, "DEMO_2026", "DEMO_CREATIVE",
                 f"DEMO-{i:03}-{touch_index}", "demo.example.test", store_id, "UTM" if touch_index == 0 else "手入力"),
            )
        stage_name = "紹介済" if i in range(52, 56) else {
            "相談中": "初回相談済", "紹介中": "紹介済", "契約済": "契約",
            "着工確認待ち": "着工", "報酬承認待ち": "着工", "請求済": "着工",
            "入金済": "完了・見送り", "争議中": "紹介済", "解約済": "完了・見送り",
        }[status_name]
        db.execute(
            "INSERT INTO stage_events(household_id,from_stage,to_stage,changed_by,changed_at) VALUES(?,NULL,?,?,?)",
            (household_id, stage_name, advisor_ids[store_id - 1], intake_at),
        )
        db.execute("INSERT INTO consents(household_id,purpose,scope,granted_at) VALUES(?,?,?,?)",
                   (household_id, "住宅会社への希望条件共有", "L3", intake_at + timedelta(days=2)))

    household_rows = db.execute(
        "SELECT id,household_code,store_id,advisor_id FROM households ORDER BY id"
    ).fetchall()
    household_ids = {int(row["household_code"][-3:]): row for row in household_rows}
    intros_by_household = {}
    for number in sorted(introduced_households):
        intro_count = 3 if number in triple_households else 2 if number in double_households else 1
        home = household_ids[number]
        intro_ids = []
        for position in range(intro_count):
            partner_id = ((number + position * 4 - 1) % 12) + 1
            introduced_at = datetime.combine(intake_dates[number - 1] + timedelta(days=7 + position), datetime.min.time())
            intro_status = "受付確認済" if number % 4 else "紹介済"
            intro_id = db.execute(
                """INSERT INTO introductions(household_id,partner_id,partner_staff_id,advisor_id,
                   introduced_at,reception_confirmed_at,status,valid_until)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (home["id"], partner_id, (partner_id - 1) * 2 + 1,
                 home["advisor_id"] if number % 13 else None, introduced_at,
                 introduced_at + timedelta(days=1) if intro_status == "受付確認済" else None, intro_status,
                 today + timedelta(days=5) if number == 12 else introduced_at.date() + timedelta(days=30)),
            ).lastrowid
            negotiation_status = ("訪問予定", "商談中", "見積提示")[position % 3]
            negotiation_id = db.execute(
                "INSERT INTO negotiations(introduction_id,status,last_activity_at) VALUES(?,?,?)",
                (intro_id, negotiation_status, introduced_at + timedelta(days=position + 2)),
            ).lastrowid
            intro_ids.append((intro_id, negotiation_id, partner_id))
        intros_by_household[number] = intro_ids

    contracts_by_intro = {}

    def create_contract(number, position=0, amount=32_000_000, project=None, fee_state=None, dispute=None):
        intro_id, negotiation_id, partner_id = intros_by_household[number][position]
        contract_date = today - timedelta(days=3) if number == 25 else intake_dates[number - 1] + timedelta(days=45)
        builder_contact = "担当1"
        db.execute("UPDATE negotiations SET status='契約' WHERE id=?", (negotiation_id,))
        contract_id = db.execute(
            "INSERT INTO contracts(negotiation_id,contract_date,contract_amount,builder_contact) VALUES(?,?,?,?)",
            (negotiation_id, contract_date, amount, builder_contact),
        ).lastrowid
        contracts_by_intro[intro_id] = contract_id
        if project is not None:
            planned_date, actual_date, confirmed_date, evidence, confirm_due, confirm_state, delayed_note = project
            db.execute(
                """INSERT INTO construction_projects(contract_id,planned_start_date,actual_start_date,
                   confirmed_start_date,confirmation_evidence,confirmation_due_date,confirmation_status,delayed_note)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (contract_id, planned_date, actual_date, confirmed_date, evidence, confirm_due, confirm_state, delayed_note),
            )
        if fee_state:
            calculated = round(amount * 0.02)
            entitlement_id = db.execute(
                """INSERT INTO fee_entitlements(contract_id,introduction_id,fee_rule_id,base_amount,
                   calculated_amount,state,dispute_reason,calculated_at,confirmed_by,invoice_data_generated,reference_amount)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (contract_id, intro_id, fee_rule_ids[partner_id], amount, calculated, fee_state,
                 dispute["reason"] if dispute else None, datetime.now().isoformat(timespec="seconds"),
                 user_ids["hq_finance"], 1 if fee_state in ("Invoiced", "Paid") else 0,
                 dispute["amount"] if dispute else 0),
            ).lastrowid
            if dispute:
                db.execute(
                    """INSERT INTO referral_disputes(fee_entitlement_id,raised_by,reason,evidence_level,
                       status,dispute_type,reference_amount,due_date) VALUES(?,?,?,'B','Open',?,?,?)""",
                    (entitlement_id, user_ids["manager"], dispute["reason"], dispute["type"],
                     dispute["amount"], today + timedelta(days=7)),
                )
                db.execute(
                    "UPDATE introductions SET status='帰属争议中',existing_customer_flag=1,evidence_note=? WHERE id=?",
                    (dispute["reason"], intro_id),
                )
        return contract_id, intro_id, partner_id

    for number in range(1, 6):
        amount = 16_500_000 if number == 1 else 32_000_000 + number * 100_000
        create_contract(number, amount=amount,
                        project=(intake_dates[number - 1] + timedelta(days=60),
                                 intake_dates[number - 1] + timedelta(days=75),
                                 intake_dates[number - 1] + timedelta(days=77), "着工写真を確認済み",
                                 intake_dates[number - 1] + timedelta(days=76), "confirmed", None),
                        fee_state="Paid")
    dispute_cases = [
        {"number": 6, "amount": 16_500_000, "fee": 330_000, "type": "referral", "reason": "紹介前接点の帰属確認"},
        {"number": 7, "amount": 11_000_000, "fee": 220_000, "type": "amount", "reason": "請負金額と料率適用の確認"},
        {"number": 8, "amount": 13_750_000, "fee": 275_000, "type": "construction", "reason": "着工証拠の真正性確認"},
    ]
    confirmation_projects = []
    for case in dispute_cases:
        project = (intake_dates[case["number"] - 1] + timedelta(days=60),
                   intake_dates[case["number"] - 1] + timedelta(days=75), None, None,
                   today - timedelta(days=2), "evidence_missing", None) if case["type"] == "construction" else None
        contract_id, intro_id, partner_id = create_contract(case["number"], amount=case["amount"], project=project,
                        fee_state="Disputed",
                        dispute={"reason": case["reason"], "type": case["type"], "amount": case["fee"]})
        if case["type"] == "construction":
            project_id = db.execute("SELECT id FROM construction_projects WHERE contract_id=?", (contract_id,)).fetchone()["id"]
            confirmation_projects.append((project_id, case["number"], "evidence_missing", today - timedelta(days=2), intro_id))
    for number in range(9, 14):
        create_contract(number, amount=32_000_000,
                        project=(intake_dates[number - 1] + timedelta(days=60),
                                 intake_dates[number - 1] + timedelta(days=75),
                                 intake_dates[number - 1] + timedelta(days=77), "着工確認済み",
                                 intake_dates[number - 1] + timedelta(days=76), "confirmed", None),
                        fee_state="Invoiced")
    for number in range(14, 18):
        create_contract(number, amount=30_000_000,
                        project=(intake_dates[number - 1] + timedelta(days=60),
                                 intake_dates[number - 1] + timedelta(days=75),
                                 intake_dates[number - 1] + timedelta(days=77), "証跡確認済み",
                                 intake_dates[number - 1] + timedelta(days=76), "confirmed", None),
                        fee_state="Pending")

    project_specs = [
        (18, 0, "planned_due", -2),
        (18, 1, "pending_review", 9),
        (19, 0, "planned_due", -1),
        (19, 1, "evidence_missing", -5),
        (20, 1, "planned_due_today", 0),
        (21, 0, "pending_review", -2),
        (22, 0, "delayed", 10),
    ]
    for number, position, state, days_late in project_specs:
        due_date = today + timedelta(days=days_late)
        planned_date = today - timedelta(days=2) if state == "planned_due" else today if state == "planned_due_today" else today + timedelta(days=10) if state == "delayed" else today - timedelta(days=8)
        actual_date = today - timedelta(days=5) if state in ("evidence_missing", "pending_review") else None
        evidence = "現場写真提出済・審査待ち" if state == "pending_review" else None
        contract_id, intro_id, partner_id = create_contract(
            number, position, 27_500_000,
            project=(planned_date, actual_date, None, evidence, due_date, state,
                     "工程調整後に確認予定" if state == "delayed" else None),
        )
        project_id = db.execute("SELECT id FROM construction_projects WHERE contract_id=?", (contract_id,)).fetchone()["id"]
        confirmation_projects.append((project_id, number, state, due_date, intro_id))

    for number in range(23, 29):
        project = None
        fee_state = None
        if number in (23, 24):
            project = (today - timedelta(days=10), today - timedelta(days=4),
                       today - timedelta(days=2), "確認証跡を審査済み", today - timedelta(days=3),
                       "confirmed", None)
            fee_state = "Confirmed"
        create_contract(number, amount=28_000_000, project=project, fee_state=fee_state)

    followup_offsets = [1, 2, 3, 5, 6, 9]
    for index, overdue_days in enumerate(followup_offsets):
        number = (index * 4) + 1
        home = household_ids[number]
        assignee = advisor_ids[home["store_id"] - 1]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               priority,related_type,related_id) VALUES(?,?,?,'sla_auto',?,'followup',?,'household',?)""",
            (assignee, f"DEMO follow-up HH-D{number:03}", today - timedelta(days=overdue_days), home["id"],
             "high" if index == 0 else "normal", home["id"]),
        )
    feedback_offsets = [2, 3, 5, 9]
    feedback_homes = [29, 30, 31, 32]
    for index, number in enumerate(feedback_homes):
        home = household_ids[number]
        intro_id = intros_by_household[number][0][0]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               priority,related_type,related_id) VALUES(?,?,?,'sla_auto',?,'partner_feedback','normal','introduction',?)""",
            (user_ids["manager"], f"DEMO partner feedback HH-D{number:03}",
             today - timedelta(days=feedback_offsets[index]), home["id"], intro_id),
        )
    for index, (project_id, number, state, due_date, intro_id) in enumerate(confirmation_projects):
        home = household_ids[number]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               priority,related_type,related_id) VALUES(?,?,?,'sla_auto',?,'construction_queue',?,
               'construction_project',?)""",
            (user_ids["manager"], f"DEMO construction queue {project_id}", due_date, home["id"],
             "normal", project_id),
        )

    for index, number in enumerate((1, 14, 45, 46, 47)):
        home = household_ids[number]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               related_type,related_id) VALUES(?,?,?,'sla_auto',?,'appointment','household',?)""",
            (home["advisor_id"] or user_ids["manager"], f"DEMO appointment HH-D{number:03}",
             today, home["id"], home["id"]),
        )

    for home in household_rows:
        if not home["advisor_id"]:
            number = int(home["household_code"][-3:])
            db.execute(
                """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
                   related_type,related_id) VALUES(?,?,?,'sla_auto',?,'unassigned','household',?)""",
                (user_ids["manager"], f"DEMO unassigned HH-D{number:03}", today, home["id"], home["id"]),
            )
    for number in range(1, 49):
        if number in (15, 25, 40):
            intro_id = intros_by_household[number][0][0]
            home = household_ids[number]
            db.execute(
                """UPDATE introductions SET advisor_id=NULL WHERE id=?""", (intro_id,)
            )
            db.execute(
                """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
                   related_type,related_id) VALUES(?,?,?,'sla_auto',?,'unassigned','introduction',?)""",
                (user_ids["manager"], f"DEMO unassigned introduction {intro_id}", today, home["id"], intro_id),
            )

    for number, task_type, state in [
        *((i, "fee_approval", "Pending") for i in range(14, 18)),
        *((i, "invoice_generation", "Confirmed") for i in (23, 24)),
        *((i, "invoice_unpaid", "Invoiced") for i in range(9, 14)),
        *((i, "dispute", "Disputed") for i in range(6, 9)),
    ]:
        intro_id = intros_by_household[number][0][0]
        home = household_ids[number]
        entitlement = db.execute("SELECT id FROM fee_entitlements WHERE introduction_id=?", (intro_id,)).fetchone()
        if entitlement:
            db.execute(
                """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
                   related_type,related_id) VALUES(?,?,?,'sla_auto',?,?,?,?)""",
                (user_ids["hq_finance"], f"DEMO {task_type} HH-D{number:03}", today, home["id"],
                 task_type, "fee_entitlement" if task_type != "dispute" else "introduction",
                 entitlement["id"] if task_type != "dispute" else intro_id),
            )

    for role, user_id in user_ids.items():
        count = db.execute("SELECT COUNT(*) FROM activities WHERE user_id=? AND DATE(acted_at)=CURRENT_DATE",
                           (user_id,)).fetchone()[0]
        db.execute(
            "INSERT INTO daily_report_drafts(user_id,report_date,auto_summary,manual_note) VALUES(?,?,?,?)",
            (user_id, today, f"本日の活動 {count} 件。デモデータを確認してください。", ""),
        )
    db.execute("INSERT INTO seed_metadata(id,batch_key,seeded_at) VALUES(1,?,?)",
               (SEED_BATCH, now))
    db.commit()


def ensure_schema(db):
    db.executescript(SCHEMA)
    migrations = {
        "households": {"household_code": "VARCHAR(24) NULL"},
        "stores": {"opened_at": "DATE NULL"},
        "partner_staff": {"branch_name": "VARCHAR(120) NULL"},
        "introductions": {"advisor_id": "INT NULL"},
        "introductions": {"advisor_id": "INT NULL", "valid_until": "DATE NULL"},
        "fee_rules": {"effective_to": "DATE NULL"},
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
    task_status_exists = db.execute(
        """SELECT COUNT(*) FROM information_schema.columns
           WHERE table_schema=DATABASE() AND table_name='tasks' AND column_name='status'"""
    ).fetchone()[0]
    if task_status_exists:
        db.execute("UPDATE tasks SET status=IF(done=1,'done','open') WHERE status IS NULL OR status='open'")
    index_exists = db.execute(
        """SELECT COUNT(*) FROM information_schema.statistics
           WHERE table_schema=DATABASE() AND table_name='households' AND index_name='uq_household_code'"""
    ).fetchone()[0]
    if not index_exists:
        db.execute("ALTER TABLE households ADD UNIQUE KEY uq_household_code (household_code)")
    for row in [
        ("introduction_validity", 30, "紹介有効期間", "介绍有效期"),
        ("construction_evidence", 7, "着工証拠提出期限", "开工证据提交期限"),
        ("dispute_resolution", 14, "争議処理期限", "争议处理期限"),
        ("agreement_renewal", 30, "提携契約更新期限", "合作协议续约期限"),
        ("fee_rule_validity", 30, "FeeRule適用期限", "FeeRule 适用期限"),
    ]:
        db.execute(
            """INSERT INTO sla_settings(reminder_type,days_before,label_ja,label_zh)
               VALUES(?,?,?,?) ON DUPLICATE KEY UPDATE reminder_type=VALUES(reminder_type)""",
            row,
        )


for attempt in range(60):
    try:
        with connect() as db:
            seed(db)
        break
    except pymysql.MySQLError:
        if attempt == 59:
            raise
        time.sleep(2)


def role_guard(role, allowed):
    if role not in allowed:
        raise HTTPException(403, "この操作を行う権限がありません")


@app.get("/api/bootstrap")
def bootstrap(x_demo_role: str = Header(default="advisor")):
    if x_demo_role not in ("advisor", "manager", "hq_finance", "executive"):
        raise HTTPException(400, "不明なデモロールです")
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        return {
            "user": {"id": user["id"], "name": user["name"], "role": user["role"], "store_id": user["store_id"]},
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
            "enums": {"stages": STAGES, "roles": ["advisor", "manager", "hq_finance", "executive"]},
            "environment": {"demo": True, "seed_batch": SEED_BATCH},
        }


def role_scope(role, user, household_alias="h"):
    if role == "advisor":
        return f"{household_alias}.advisor_id=?", (user["id"],)
    if role == "manager":
        return f"{household_alias}.store_id=?", (user["store_id"],)
    return "1=1", ()


def get_households(db, role, user):
    scope, scope_args = role_scope(role, user)
    households = [dict(row) for row in db.execute(
        f"""SELECT h.*,s.name AS store_name,u.name AS advisor_name FROM households h
            LEFT JOIN stores s ON s.id=h.store_id LEFT JOIN users u ON u.id=h.advisor_id
            WHERE {scope} ORDER BY h.id""", scope_args)]
    for household in households:
        household["persons"] = [dict(r) for r in db.execute("SELECT * FROM persons WHERE household_id=?", (household["id"],))]
        touches = [dict(r) for r in db.execute("SELECT * FROM touches WHERE household_id=? ORDER BY touch_at", (household["id"],))]
        household["touches"] = touches
        household["first_touch"] = touches[0] if touches else None
        household["latest_touch"] = touches[-1] if touches else None
        household["stage_events"] = [dict(r) for r in db.execute(
            """SELECT e.*,u.name AS changed_by_name FROM stage_events e
               LEFT JOIN users u ON u.id=e.changed_by WHERE household_id=? ORDER BY changed_at""",
            (household["id"],))]
        household["activities"] = [dict(r) for r in db.execute(
            """SELECT a.*,u.name AS user_name FROM activities a LEFT JOIN users u ON u.id=a.user_id
               WHERE household_id=? ORDER BY acted_at DESC""", (household["id"],))]
        household["introductions"] = [dict(r) for r in db.execute(
            """SELECT i.*,p.name AS partner_name,ps.name AS staff_name,ps.branch_name,
               n.id AS negotiation_id,n.status AS negotiation_status,n.last_activity_at,
               c.id AS contract_id,c.contract_date,c.contract_amount,cp.id AS project_id,
               cp.planned_start_date,cp.actual_start_date,cp.confirmed_start_date,
               cp.confirmation_evidence,cp.confirmation_due_date,cp.confirmation_status,
               cp.delayed_note,fe.id AS entitlement_id,fe.calculated_amount,
               fe.state AS entitlement_state,fe.dispute_reason,fe.invoice_data_generated,
               fe.reference_amount,fr.version AS rule_version,fr.params AS rule_params,fr.base AS rule_base
               FROM introductions i JOIN partners p ON p.id=i.partner_id
               LEFT JOIN partner_staff ps ON ps.id=i.partner_staff_id
               LEFT JOIN negotiations n ON n.introduction_id=i.id
               LEFT JOIN contracts c ON c.negotiation_id=n.id
               LEFT JOIN construction_projects cp ON cp.contract_id=c.id
               LEFT JOIN fee_entitlements fe ON fe.introduction_id=i.id
               LEFT JOIN fee_rules fr ON fr.id=fe.fee_rule_id
               WHERE i.household_id=? ORDER BY i.id""", (household["id"],))]
        household["consents"] = [dict(r) for r in db.execute(
            "SELECT * FROM consents WHERE household_id=? ORDER BY granted_at DESC", (household["id"],))]
        household["disclosures"] = [dict(r) for r in db.execute(
            "SELECT * FROM data_disclosures WHERE household_id=? ORDER BY disclosed_at DESC", (household["id"],))]
    return households


@app.get("/api/households")
def household_index(x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        role = x_demo_role
        households = get_households(db, role, user)
        scope, args = role_scope(role, user)
        advisor_scope = "store_id=?" if role in ("advisor", "manager") else "1=1"
        advisor_args = (user["store_id"],) if role in ("advisor", "manager") else ()
        entitlements = [dict(row) for row in db.execute(
            f"""SELECT fe.*,fr.version AS rule_version,fr.type AS rule_type,fr.params,fr.base,
                h.representative_name,h.household_code,p.name AS partner_name,c.contract_amount
                FROM fee_entitlements fe JOIN contracts c ON c.id=fe.contract_id
                JOIN introductions i ON i.id=fe.introduction_id JOIN households h ON h.id=i.household_id
                JOIN partners p ON p.id=i.partner_id JOIN fee_rules fr ON fr.id=fe.fee_rule_id
                WHERE {scope} ORDER BY fe.id""", args)]
        return {
            "user": {"id": user["id"], "name": user["name"], "role": role, "store_id": user["store_id"]},
            "stores": [dict(r) for r in db.execute(
                f"SELECT * FROM stores WHERE id=? ORDER BY id" if role in ("advisor", "manager") else "SELECT * FROM stores ORDER BY id",
                (user["store_id"],) if role in ("advisor", "manager") else ())],
            "advisors": [dict(r) for r in db.execute(
                f"SELECT id,name,store_id FROM users WHERE role='advisor' AND {advisor_scope} ORDER BY id",
                advisor_args)],
            "partners": [dict(r) for r in db.execute("SELECT * FROM partners WHERE active=1 ORDER BY name")],
            "partner_staff": [dict(r) for r in db.execute("SELECT * FROM partner_staff ORDER BY partner_id")],
            "households": households,
            "entitlements": entitlements,
            "audit_logs": [dict(r) for r in db.execute(
                """SELECT a.*,u.name AS user_name FROM audit_logs a LEFT JOIN users u ON u.id=a.user_id
                   WHERE (? IN ('hq_finance','executive') OR a.user_id=?)
                   ORDER BY a.`at` DESC LIMIT 50""", (role, user["id"]))],
            "daily_report": dict(row) if (row := db.execute(
                "SELECT * FROM daily_report_drafts WHERE user_id=? ORDER BY id DESC LIMIT 1", (user["id"],)
            ).fetchone()) else None,
            "seed_batch": SEED_BATCH,
        }


class AssignmentInput(BaseModel):
    advisor_id: int


class SLASettingInput(BaseModel):
    days_before: int


@app.put("/api/settings/sla/{reminder_type}")
def update_sla_setting(reminder_type: str, payload: SLASettingInput,
                       x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("hq_finance", "executive"))
    if payload.days_before < 0 or payload.days_before > 365:
        raise HTTPException(422, "期限は 0〜365 日の範囲で設定してください")
    with connect() as db:
        user = db.execute("SELECT id FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        setting = db.execute("SELECT reminder_type FROM sla_settings WHERE reminder_type=?",
                             (reminder_type,)).fetchone()
        if not setting:
            raise HTTPException(404, "期限設定が見つかりません")
        db.execute("UPDATE sla_settings SET days_before=? WHERE reminder_type=?",
                   (payload.days_before, reminder_type))
        audit(db, user["id"], "sla.updated", "sla_setting", 0,
              f"{reminder_type}={payload.days_before}")
        db.commit()
    return {"ok": True, "reminder_type": reminder_type, "days_before": payload.days_before}


@app.post("/api/households/{household_id}/assign")
def assign_household(household_id: int, payload: AssignmentInput,
                     x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("manager", "executive"))
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        household = db.execute("SELECT * FROM households WHERE id=?", (household_id,)).fetchone()
        advisor = db.execute("SELECT * FROM users WHERE id=? AND role='advisor'", (payload.advisor_id,)).fetchone()
        if not household or not advisor:
            raise HTTPException(404, "家庭または担当顧問が見つかりません")
        if x_demo_role == "manager" and (household["store_id"] != user["store_id"] or advisor["store_id"] != user["store_id"]):
            raise HTTPException(403, "自店舗内の担当割り当てのみ実行できます")
        db.execute("UPDATE households SET advisor_id=? WHERE id=?", (advisor["id"], household_id))
        db.execute("UPDATE introductions SET advisor_id=? WHERE household_id=? AND advisor_id IS NULL",
                   (advisor["id"], household_id))
        db.execute(
            """UPDATE tasks SET done=1,status='done' WHERE related_household_id=?
               AND task_type='unassigned' AND done=0""", (household_id,))
        audit(db, user["id"], "household.assigned", "household", household_id, str(advisor["id"]))
        db.commit()
    return {"ok": True}


@app.post("/api/introductions/{introduction_id}/assign")
def assign_introduction(introduction_id: int, payload: AssignmentInput,
                        x_demo_role: str = Header(default="advisor")):
    role_guard(x_demo_role, ("manager", "executive"))
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        intro = db.execute(
            """SELECT i.id,i.household_id,h.store_id FROM introductions i
               JOIN households h ON h.id=i.household_id WHERE i.id=?""", (introduction_id,)
        ).fetchone()
        advisor = db.execute("SELECT * FROM users WHERE id=? AND role='advisor'", (payload.advisor_id,)).fetchone()
        if not intro or not advisor:
            raise HTTPException(404, "紹介または担当顧問が見つかりません")
        if x_demo_role == "manager" and (intro["store_id"] != user["store_id"] or advisor["store_id"] != user["store_id"]):
            raise HTTPException(403, "自店舗内の担当割り当てのみ実行できます")
        db.execute("UPDATE introductions SET advisor_id=? WHERE id=?", (advisor["id"], introduction_id))
        db.execute(
            """UPDATE tasks SET done=1,status='done' WHERE related_type='introduction'
               AND related_id=? AND task_type='unassigned' AND done=0""", (introduction_id,))
        audit(db, user["id"], "introduction.assigned", "introduction", introduction_id, str(advisor["id"]))
        db.commit()
    return {"ok": True}


TASK_FILTERS = {
    "today_followup": "t.task_type='followup' AND t.due_at=CURRENT_DATE",
    "overdue_followup": "t.task_type='followup' AND t.due_at<CURRENT_DATE",
    "appointments_today": "t.task_type='appointment' AND t.due_at=CURRENT_DATE AND t.cancelled=0",
    "store_overdue": "t.due_at<CURRENT_DATE",
    "unassigned": "t.task_type='unassigned'",
    "partner_feedback": "t.task_type='partner_feedback'",
    "fee_approval": "t.task_type='fee_approval'",
    "invoice_generation": "t.task_type='invoice_generation'",
    "invoice_unpaid": "t.task_type='invoice_unpaid'",
    "critical_overdue": "t.due_at<CURRENT_DATE AND t.priority='high'",
    "disputed_introductions": "t.task_type='dispute'",
    "construction_queue": "t.task_type='construction_queue'",
    "construction_overdue": "t.task_type='construction_queue' AND t.due_at<CURRENT_DATE",
}

TASK_LABELS = {
    "advisor": [
        ("today_followup", "今日フォロー", "task", "households"),
        ("overdue_followup", "期限超過", "task", "households"),
        ("appointments_today", "本日来店", "appointment", "households"),
    ],
    "manager": [
        ("store_overdue", "店内期限超過", "task", "households"),
        ("unassigned", "担当未割当", "household", "introductions"),
        ("appointments_today", "本日来店", "appointment", "households"),
    ],
    "hq_finance": [
        ("fee_approval", "報酬承認待ち", "fee_entitlement", "revenue"),
        ("invoice_generation", "請求データ生成待ち", "fee_entitlement", "revenue"),
        ("invoice_unpaid", "請求済・未入金", "fee_entitlement", "revenue"),
    ],
    "executive": [
        ("critical_overdue", "重大業務リスク", "task", "households"),
        ("disputed_introductions", "紹介帰属争議", "introduction", "introductions"),
        ("construction_queue", "着工確認滞留", "construction_project", "revenue"),
    ],
}

TASK_LABELS_ZH = {
    "today_followup": "今日待跟进", "overdue_followup": "已超期", "appointments_today": "今日来店",
    "store_overdue": "门店超期任务", "unassigned": "未分配负责人", "fee_approval": "待审批报酬",
    "invoice_generation": "待生成请款数据", "invoice_unpaid": "已请款未入金",
    "critical_overdue": "重大业务风险", "disputed_introductions": "介绍归属争议",
    "construction_queue": "待确认开工",
}


@app.get("/api/dashboard/summary")
def dashboard_summary(x_demo_role: str = Header(default="advisor"),
                      x_demo_locale: str = Header(default="ja")):
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        if not user or x_demo_role not in TASK_LABELS:
            raise HTTPException(400, "不明なデモロールです")
        scope, scope_args = role_scope(x_demo_role, user)
        counters = []
        for key, label_ja, unit_type, target in TASK_LABELS[x_demo_role]:
            count = db.execute(
                f"""SELECT COUNT(*) FROM tasks t
                    LEFT JOIN households h ON h.id=t.related_household_id
                    WHERE t.done=0 AND t.status='open' AND t.cancelled=0
                    AND ({TASK_FILTERS[key]}) AND ({scope})""",
                (*scope_args,),
            ).fetchone()[0]
            counters.append({
                "key": key,
                "label": TASK_LABELS_ZH.get(key, label_ja) if x_demo_locale == "zh" else label_ja,
                "unit_type": unit_type,
                "count": count,
                "target_page": target,
                "filter": key,
            })
        return {"role": x_demo_role, "generated_at": datetime.now().isoformat(timespec="seconds"),
                "counters": counters, "seed_batch": SEED_BATCH}


@app.get("/api/dashboard/my-tasks")
def my_tasks(filter_name: Optional[str] = Query(default=None, alias="filter"),
             x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        scope, args = role_scope(x_demo_role, user)
        if x_demo_role == "advisor":
            scope = "t.assignee_id=?"
            args = (user["id"],)
        elif x_demo_role == "manager":
            scope = "h.store_id=?"
            args = (user["store_id"],)
        elif x_demo_role == "hq_finance":
            scope = "t.task_type IN ('fee_approval','invoice_generation','invoice_unpaid','dispute')"
            args = ()
        selected_filter = filter_name
        if selected_filter:
            if selected_filter not in TASK_FILTERS:
                raise HTTPException(422, "不明なタスクフィルターです")
            filters = TASK_FILTERS[selected_filter]
        elif x_demo_role == "advisor":
            filters = "t.due_at<=CURRENT_DATE OR t.task_type='appointment'"
        elif x_demo_role == "manager":
            filters = "t.due_at<=CURRENT_DATE OR t.task_type IN ('unassigned','appointment','partner_feedback','construction_queue')"
        elif x_demo_role == "hq_finance":
            filters = "t.task_type IN ('fee_approval','invoice_generation','invoice_unpaid','dispute')"
        else:
            filters = "t.priority='high' AND t.due_at<CURRENT_DATE OR t.task_type IN ('dispute','construction_queue')"
        rows = [dict(r) for r in db.execute(
            f"""SELECT t.id AS task_id,t.title,t.related_type,t.related_id,t.due_at,
                GREATEST(DATEDIFF(CURRENT_DATE,t.due_at),0) AS days_overdue,t.priority,
                IF(t.done=1 OR t.status='done','done','open') AS status,t.task_type,
                h.id AS household_id,h.household_code,h.representative_name,
                cp.confirmation_status
                FROM tasks t LEFT JOIN households h ON h.id=t.related_household_id
                LEFT JOIN construction_projects cp ON t.related_type='construction_project' AND cp.id=t.related_id
                WHERE t.done=0 AND t.status='open' AND t.cancelled=0
                AND ({filters}) AND ({scope})
                ORDER BY t.due_at,t.priority DESC,t.id""", (*args,))]
        for row in rows:
            row["due_at"] = row["due_at"].isoformat() if hasattr(row["due_at"], "isoformat") else str(row["due_at"])
        return {"role": x_demo_role, "filter": selected_filter, "tasks": rows}


@app.get("/api/dashboard/trends")
def dashboard_trends(metric: str = "inquiries", period: str = "30d",
                     x_demo_role: str = Header(default="advisor")):
    metric_queries = {
        "inquiries": ("households h", "DATE(h.created_at)", "h.id=h.id"),
        "consultations": ("activities a JOIN households h ON h.id=a.household_id", "DATE(a.acted_at)", "a.type='面談'"),
        "introductions": ("introductions i JOIN households h ON h.id=i.household_id", "DATE(i.introduced_at)", "1=1"),
        "contracts": ("contracts c JOIN negotiations n ON n.id=c.negotiation_id JOIN introductions i ON i.id=n.introduction_id JOIN households h ON h.id=i.household_id", "DATE(c.contract_date)", "1=1"),
        "construction": ("construction_projects cp JOIN contracts c ON c.id=cp.contract_id JOIN negotiations n ON n.id=c.negotiation_id JOIN introductions i ON i.id=n.introduction_id JOIN households h ON h.id=i.household_id", "DATE(cp.actual_start_date)", "cp.actual_start_date IS NOT NULL"),
    }
    periods = {"7d": 7, "30d": 30, "90d": 90, "180d": 180, "365d": 365}
    if period not in periods:
        raise HTTPException(422, "期間は 7d / 30d / 90d / 180d / 365d から選択してください")
    if metric != "cohort" and metric not in metric_queries:
        raise HTTPException(422, "不明なトレンド指標です")
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        scope, scope_args = role_scope(x_demo_role, user)
        days = periods[period]
        today = date.today()
        if metric == "cohort":
            cohorts = [dict(row) for row in db.execute(
                f"""SELECT DATE_FORMAT(h.created_at,'%%Y-%%m') AS cohort,
                    COUNT(DISTINCT h.id) AS households,
                    COUNT(DISTINCT i.id) AS introductions,
                    COUNT(DISTINCT c.id) AS contracts,
                    COUNT(DISTINCT CASE WHEN i.id IS NOT NULL THEN h.id END) AS introduced_households,
                    COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN h.id END) AS contracted_households
                    FROM households h LEFT JOIN introductions i ON i.household_id=h.id
                    LEFT JOIN negotiations n ON n.introduction_id=i.id
                    LEFT JOIN contracts c ON c.negotiation_id=n.id
                    WHERE h.created_at>=DATE_SUB(CURRENT_DATE, INTERVAL ? DAY) AND ({scope})
                    GROUP BY DATE_FORMAT(h.created_at,'%%Y-%%m') ORDER BY cohort""",
                (days, *scope_args))]
            for row in cohorts:
                row["introduction_rate"] = round(row["introduced_households"] / row["households"] * 100, 1) if row["households"] else 0
                row["contract_rate"] = round(row["contracted_households"] / row["households"] * 100, 1) if row["households"] else 0
            return {"metric": metric, "period": period, "unit_type": "cohort",
                    "cohorts": cohorts, "seed_batch": SEED_BATCH}
        source, event_date, extra = metric_queries[metric]
        current_start = today - timedelta(days=days - 1)
        previous_start = current_start - timedelta(days=days)

        def count_between(start, end):
            return db.execute(
                f"""SELECT COUNT(*) FROM {source} WHERE {extra} AND {event_date}>=? AND {event_date}<?
                    AND ({scope})""",
                (start, end, *scope_args),
            ).fetchone()[0]

        current_total = count_between(current_start, today + timedelta(days=1))
        previous_total = count_between(previous_start, current_start)
        if days == 7:
            points = [{"label": "前7日", "count": previous_total, "series": "previous"},
                      {"label": "近7日", "count": current_total, "series": "current"}]
        else:
            bucket_size = 5 if days == 30 else 7
            bucket_count = (days + bucket_size - 1) // bucket_size
            points = []
            for series, series_start in (("previous", previous_start), ("current", current_start)):
                for index in range(bucket_count):
                    start = series_start + timedelta(days=index * bucket_size)
                    end = min(start + timedelta(days=bucket_size), series_start + timedelta(days=days))
                    points.append({"label": f"{start.month}/{start.day}", "count": count_between(start, end),
                                   "series": series})
        return {"metric": metric, "period": period, "unit_type": "count",
                "current_count": current_total, "previous_count": previous_total,
                "change": current_total - previous_total, "points": points, "seed_batch": SEED_BATCH}


@app.get("/api/revenue")
def revenue_workspace(x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        scope, args = role_scope(x_demo_role, user)
        entitlements = [dict(row) for row in db.execute(
            f"""SELECT fe.*,fr.version AS rule_version,fr.type AS rule_type,fr.params,fr.base,
                h.id AS household_id,h.household_code,h.representative_name,p.name AS partner_name,
                c.contract_amount FROM fee_entitlements fe JOIN contracts c ON c.id=fe.contract_id
                JOIN introductions i ON i.id=fe.introduction_id JOIN households h ON h.id=i.household_id
                JOIN partners p ON p.id=i.partner_id JOIN fee_rules fr ON fr.id=fe.fee_rule_id
                WHERE {scope} ORDER BY fe.id""", args)]
        projects = [dict(row) for row in db.execute(
            f"""SELECT cp.*,c.id AS contract_id,c.contract_amount,c.contract_date,
                i.id AS introduction_id,h.id AS household_id,h.household_code,
                h.representative_name,p.name AS partner_name,fe.id AS entitlement_id,
                fe.state AS entitlement_state,fe.calculated_amount,fe.reference_amount
                FROM construction_projects cp JOIN contracts c ON c.id=cp.contract_id
                JOIN negotiations n ON n.id=c.negotiation_id
                JOIN introductions i ON i.id=n.introduction_id
                JOIN households h ON h.id=i.household_id JOIN partners p ON p.id=i.partner_id
                LEFT JOIN fee_entitlements fe ON fe.contract_id=c.id
                WHERE {scope} ORDER BY cp.confirmation_due_date,cp.id""", args)]
        for project in projects:
            project["days_overdue"] = max((date.today() - project["confirmation_due_date"]).days, 0) if project["confirmation_due_date"] else 0
        disputes = [dict(row) for row in db.execute(
            f"""SELECT rd.*,fe.state AS entitlement_state,fe.calculated_amount,
                h.id AS household_id,h.household_code,h.representative_name,p.name AS partner_name
                FROM referral_disputes rd JOIN fee_entitlements fe ON fe.id=rd.fee_entitlement_id
                JOIN introductions i ON i.id=fe.introduction_id JOIN households h ON h.id=i.household_id
                JOIN partners p ON p.id=i.partner_id WHERE {scope} ORDER BY rd.id""", args)]
        fee_counts = {state: sum(row["state"] == state for row in entitlements)
                      for state in ("Pending", "Confirmed", "Invoiced", "Paid", "Disputed")}
        amounts = {state: sum(int(row["calculated_amount"]) for row in entitlements if row["state"] == state)
                   for state in fee_counts}
        planned_fee = 0
        for project in projects:
            if project["entitlement_state"] is None and project["actual_start_date"] is None:
                rule = db.execute(
                    """SELECT fr.params FROM partner_agreements pa JOIN fee_rules fr ON fr.id=pa.fee_rule_id
                       JOIN introductions i ON i.partner_id=pa.partner_id
                       WHERE i.id=? AND pa.status='active' ORDER BY pa.effective_from DESC LIMIT 1""",
                    (project["introduction_id"],),
                ).fetchone()
                if rule:
                    params = rule["params"] if isinstance(rule["params"], dict) else json.loads(rule["params"])
                    planned_fee += round(project["contract_amount"] * float(params.get("rate", 0)))
        queue_counts = {}
        for row in projects:
            state = row["confirmation_status"] or "pending_review"
            queue_counts[state] = queue_counts.get(state, 0) + 1
        return {
            "projects": projects,
            "entitlements": entitlements,
            "disputes": disputes,
            "queue_counts": {
                "planned_due_overdue": sum(r["confirmation_status"] == "planned_due" and r["days_overdue"] > 0 for r in projects),
                "planned_due_today": sum(r["confirmation_status"] == "planned_due_today" for r in projects),
                "evidence_missing": sum(r["confirmation_status"] == "evidence_missing" for r in projects),
                "pending_review": sum(r["confirmation_status"] == "pending_review" for r in projects),
                "delayed": sum(r["confirmation_status"] == "delayed" for r in projects),
                "overdue": sum(r["days_overdue"] > 0 and not r["confirmed_start_date"] for r in projects),
                "total": sum(not r["confirmed_start_date"] for r in projects),
            },
            "financial": {
                "planned_construction_fee": planned_fee,
                "pending_approval": amounts["Pending"],
                "approved": amounts["Confirmed"],
                "invoiced": amounts["Invoiced"],
                "paid": amounts["Paid"],
                "confirmed_sales": amounts["Paid"],
                "dispute_count": len(disputes),
                "dispute_reference_amount": sum(int(row["reference_amount"]) for row in disputes),
                "frozen_amount": sum(int(row["calculated_amount"]) for row in entitlements if row["state"] == "Disputed"),
            },
            "counts": fee_counts,
            "seed_batch": SEED_BATCH,
        }


def build_reminders(db, role, user):
    scope, args = role_scope(role, user)
    partner_scope, partner_args = role_scope(role, user, "rh")
    rules = {row["reminder_type"]: row["days_before"] for row in db.execute("SELECT * FROM sla_settings")}
    reminders = []
    sources = [
        ("introduction_validity", "introduction", "introductions", "i.valid_until", "i.id", "i.status NOT IN ('見送り','帰属争议中')"),
        ("construction_evidence", "construction_project", "construction_projects", "cp.confirmation_due_date", "cp.id", "cp.confirmed_start_date IS NULL"),
        ("dispute_resolution", "dispute", "referral_disputes", "rd.due_date", "rd.id", "rd.status IN ('Open','UnderReview')"),
    ]
    for kind, related_type, table, deadline, object_id, active_clause in sources:
        if table == "introductions":
            joins = "JOIN households h ON h.id=i.household_id"
            alias = "i"
        elif table == "construction_projects":
            joins = "JOIN contracts c ON c.id=cp.contract_id JOIN negotiations n ON n.id=c.negotiation_id JOIN introductions i ON i.id=n.introduction_id JOIN households h ON h.id=i.household_id"
            alias = "cp"
        else:
            joins = "JOIN fee_entitlements fe ON fe.id=rd.fee_entitlement_id JOIN introductions i ON i.id=fe.introduction_id JOIN households h ON h.id=i.household_id"
            alias = "rd"
        rows = db.execute(
            f"""SELECT {alias}.id AS id,{deadline} AS due_at,h.id AS household_id,
                h.household_code,h.representative_name FROM {table} {alias} {joins}
                WHERE {active_clause} AND {deadline} IS NOT NULL AND {deadline}<=DATE_ADD(CURRENT_DATE, INTERVAL ? DAY)
                AND ({scope}) ORDER BY {deadline} LIMIT 20""",
            (rules[kind], *args),
        )
        for row in rows:
            reminders.append({
                "key": kind, "related_type": related_type, "related_id": row["id"],
                "household_id": row["household_id"], "household_code": row["household_code"],
                "representative_name": row["representative_name"],
                "due_at": row["due_at"].isoformat() if row["due_at"] else None,
                "days_until_due": (row["due_at"] - date.today()).days if row["due_at"] else 0,
                "sla_days": rules[kind], "status": "overdue" if row["due_at"] < date.today() else "upcoming",
            })
    for kind, table, deadline, id_column, active_clause in [
        ("agreement_renewal", "partner_agreements", "pa.effective_to", "pa.id", "pa.status='active'"),
        ("fee_rule_validity", "fee_rules", "fr.effective_to", "fr.id", "1=1"),
    ]:
        alias = "pa" if table == "partner_agreements" else "fr"
        rows = db.execute(
            f"""SELECT {id_column} AS id,{deadline} AS due_at,p.name AS partner_name
                FROM {table} {alias} {"JOIN partners p ON p.id=pa.partner_id" if alias=="pa" else "JOIN partner_agreements pa ON pa.fee_rule_id=fr.id JOIN partners p ON p.id=pa.partner_id"}
                WHERE {active_clause} AND {deadline} IS NOT NULL
                AND EXISTS (SELECT 1 FROM introductions ri JOIN households rh ON rh.id=ri.household_id
                            WHERE ri.partner_id=p.id AND ({partner_scope}))
                AND {deadline}<=DATE_ADD(CURRENT_DATE, INTERVAL ? DAY)
                ORDER BY {deadline} LIMIT 20""",
            (*partner_args, rules[kind]),
        )
        for row in rows:
            reminders.append({
                "key": kind, "related_type": "partner_agreement" if alias == "pa" else "fee_rule",
                "related_id": row["id"], "partner_name": row["partner_name"],
                "due_at": row["due_at"].isoformat() if row["due_at"] else None,
                "days_until_due": (row["due_at"] - date.today()).days if row["due_at"] else 0,
                "sla_days": rules[kind], "status": "overdue" if row["due_at"] < date.today() else "upcoming",
            })
    return reminders, rules


@app.get("/api/management")
def management_workspace(x_demo_role: str = Header(default="advisor")):
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=? ORDER BY id LIMIT 1", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
        scope, args = role_scope(x_demo_role, user)
        reminders, sla_rules = build_reminders(db, x_demo_role, user)
        stores = [dict(row) for row in db.execute(
            "SELECT * FROM stores WHERE id=? ORDER BY id" if x_demo_role in ("advisor", "manager") else "SELECT * FROM stores ORDER BY id",
            (user["store_id"],) if x_demo_role in ("advisor", "manager") else ())]
        for store in stores:
            total = db.execute("SELECT COUNT(*) FROM households WHERE store_id=?", (store["id"],)).fetchone()[0]
            contracts = db.execute(
                """SELECT COUNT(*) FROM contracts c JOIN negotiations n ON n.id=c.negotiation_id
                   JOIN introductions i ON i.id=n.introduction_id JOIN households h ON h.id=i.household_id
                   WHERE h.store_id=?""", (store["id"],)).fetchone()[0]
            store["household_count"] = total
            store["contract_count"] = contracts
            store["contract_household_count"] = db.execute(
                """SELECT COUNT(DISTINCT h.id) FROM contracts c JOIN negotiations n ON n.id=c.negotiation_id
                   JOIN introductions i ON i.id=n.introduction_id JOIN households h ON h.id=i.household_id
                   WHERE h.store_id=?""", (store["id"],)).fetchone()[0]
            store["opened_months"] = max((date.today() - store["opened_at"]).days // 30, 0) if store["opened_at"] else 0
        households = get_households(db, x_demo_role, user)
        allowed_ids = [row["id"] for row in households]
        if allowed_ids:
            placeholders = ",".join("?" for _ in allowed_ids)
            touch_rows = db.execute(
                f"""SELECT t.household_id,t.channel,t.touch_at
                    FROM touches t WHERE t.household_id IN ({placeholders}) ORDER BY t.household_id,t.touch_at""",
                tuple(allowed_ids))
            touch_groups = {}
            for touch in touch_rows:
                touch_groups.setdefault(touch["household_id"], []).append(touch)
            channel_stats = {}
            for household_id, rows in touch_groups.items():
                for position, kind in ((0, "first"), (-1, "latest")):
                    channel = rows[position]["channel"]
                    channel_stats.setdefault(channel, {"channel": channel, "first_touch": 0, "latest_touch": 0,
                                                       "households": set(), "introduced": set()})
                    channel_stats[channel][f"{kind}_touch"] += 1
                    channel_stats[channel]["households"].add(household_id)
                    if any(h["id"] == household_id and h["introductions"] for h in households):
                        channel_stats[channel]["introduced"].add(household_id)
            marketing = [{
                **{k: v for k, v in stat.items() if k not in ("households", "introduced")},
                "households": len(stat["households"]), "introduced_households": len(stat["introduced"]),
            } for stat in channel_stats.values()]
        else:
            marketing = []
        operation = {}
        thirty_days_ago = date.today() - timedelta(days=30)
        due_count = db.execute(
            f"SELECT COUNT(*) FROM tasks t LEFT JOIN households h ON h.id=t.related_household_id WHERE t.due_at>=? AND t.done IN (0,1) AND ({scope})",
            (thirty_days_ago, *args)).fetchone()[0]
        done_count = db.execute(
            f"SELECT COUNT(*) FROM tasks t LEFT JOIN households h ON h.id=t.related_household_id WHERE t.due_at>=? AND t.done=1 AND ({scope})",
            (thirty_days_ago, *args)).fetchone()[0]
        operation["followup_execution"] = {"numerator": done_count, "denominator": due_count,
                                           "rate": round(done_count / due_count * 100, 1) if due_count else 0}
        operation["data_completeness"] = {
            "numerator": sum(bool(h["budget_band"] and h["area_pref"] and h["store_id"]) for h in households),
            "denominator": len(households),
        }
        operation["next_action_setting"] = {
            "numerator": sum(any(a["next_action"] for a in h["activities"]) for h in households),
            "denominator": len(households),
        }
        if x_demo_role == "advisor":
            report_scope, report_args = "u.id=?", (user["id"],)
        elif x_demo_role == "manager":
            report_scope, report_args = "u.store_id=?", (user["store_id"],)
        else:
            report_scope, report_args = "1=1", ()
        reports = db.execute(
            f"""SELECT COUNT(DISTINCT r.report_date) FROM daily_report_drafts r
                JOIN users u ON u.id=r.user_id WHERE r.report_date>=? AND ({report_scope})""",
            (thirty_days_ago, *report_args)).fetchone()[0]
        operation["daily_report_submission"] = {"numerator": reports, "denominator": 30}
        recently_contacted = sum(any((datetime.now() - a["acted_at"]).days <= 7 for a in h["activities"]) for h in households)
        operation["customer_response_sample"] = {"numerator": recently_contacted, "denominator": len(households)}
        partner_quality = [dict(row) for row in db.execute(
            f"""SELECT p.id,p.name,COUNT(DISTINCT i.id) AS introductions,
                COUNT(DISTINCT c.id) AS contracts,
                COUNT(DISTINCT CASE WHEN fe.state='Paid' THEN fe.id END) AS paid,
                COUNT(DISTINCT CASE WHEN fe.state='Disputed' THEN fe.id END) AS disputed,
                COALESCE(SUM(DISTINCT CASE WHEN fe.state='Disputed' THEN fe.reference_amount END),0) AS frozen_reference_amount
                FROM partners p LEFT JOIN introductions i ON i.partner_id=p.id
                LEFT JOIN households h ON h.id=i.household_id
                LEFT JOIN negotiations n ON n.introduction_id=i.id
                LEFT JOIN contracts c ON c.negotiation_id=n.id
                LEFT JOIN fee_entitlements fe ON fe.contract_id=c.id
                WHERE (h.id IS NULL OR {scope}) GROUP BY p.id,p.name ORDER BY p.name""", args)]
        cohort_rows = [dict(row) for row in db.execute(
            f"""SELECT DATE_FORMAT(h.created_at,'%%Y-%%m') AS cohort,COUNT(DISTINCT h.id) AS households,
                COUNT(DISTINCT i.id) AS introductions,COUNT(DISTINCT c.id) AS contracts,
                COUNT(DISTINCT CASE WHEN i.id IS NOT NULL THEN h.id END) AS introduced_households,
                COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN h.id END) AS contracted_households
                FROM households h LEFT JOIN introductions i ON i.household_id=h.id
                LEFT JOIN negotiations n ON n.introduction_id=i.id
                LEFT JOIN contracts c ON c.negotiation_id=n.id
                WHERE h.created_at>=DATE_SUB(CURRENT_DATE,INTERVAL 365 DAY) AND ({scope})
                GROUP BY DATE_FORMAT(h.created_at,'%%Y-%%m') ORDER BY cohort""", args)]
        for row in cohort_rows:
            row["introduction_rate"] = round(row["introduced_households"] / row["households"] * 100, 1) if row["households"] else 0
            row["contract_rate"] = round(row["contracted_households"] / row["households"] * 100, 1) if row["households"] else 0
        return {
            "stores": stores, "operations": operation, "reminders": reminders, "sla_rules": sla_rules,
            "marketing": marketing, "partner_quality": partner_quality, "cohorts": cohort_rows,
            "seed_batch": SEED_BATCH,
        }


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
        household = db.execute("SELECT * FROM households WHERE id=?", (payload.household_id,)).fetchone()
        if not household:
            raise HTTPException(404, "世帯が見つかりません")
        if x_demo_role == "advisor" and household["advisor_id"] != user["id"]:
            raise HTTPException(403, "担当世帯以外は更新できません")
        if x_demo_role == "manager" and household["store_id"] != user["store_id"]:
            raise HTTPException(403, "自店舗以外は更新できません")
        db.execute(
            """INSERT INTO activities(household_id,user_id,type,body,acted_at,next_action,next_action_due)
               VALUES(?,?,?,?,?,?,?)""",
            (payload.household_id, user["id"], payload.type, payload.body,
             datetime.now().isoformat(timespec="seconds"), payload.next_action, payload.next_action_due),
        )
        overdue_task = db.execute(
            """SELECT id FROM tasks WHERE assignee_id=? AND related_household_id=?
               AND task_type='followup' AND done=0 AND status='open' AND due_at<CURRENT_DATE
               ORDER BY due_at,id LIMIT 1""", (user["id"], payload.household_id),
        ).fetchone()
        if overdue_task:
            db.execute("UPDATE tasks SET done=1,status='done' WHERE id=?", (overdue_task["id"],))
        if payload.next_action and payload.next_action_due:
            db.execute(
                """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
                   priority,related_type,related_id,status)
                   VALUES(?,?,?,'manual',?,'followup','normal','household',?,'open')""",
                (user["id"], payload.next_action, payload.next_action_due, payload.household_id, payload.household_id),
            )
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
        household = db.execute("SELECT id FROM households WHERE id=?", (payload.household_id,)).fetchone()
        staff = db.execute("SELECT id FROM partner_staff WHERE id=? AND partner_id=?",
                           (payload.partner_staff_id, payload.partner_id)).fetchone()
        if not household or not staff:
            raise HTTPException(404, "家庭または住宅会社担当者が見つかりません")
        now = datetime.now().isoformat(timespec="seconds")
        intro_id = db.execute(
            """INSERT INTO introductions(household_id,partner_id,partner_staff_id,advisor_id,introduced_at,
               status,valid_until) VALUES(?,?,?,?,?,'紹介済',?)""",
            (payload.household_id, payload.partner_id, payload.partner_staff_id,
             db.execute("SELECT advisor_id FROM households WHERE id=?", (payload.household_id,)).fetchone()["advisor_id"],
             now, date.today() + timedelta(days=30)),
        ).lastrowid
        db.execute("INSERT INTO negotiations(introduction_id,status,last_activity_at) VALUES(?,'訪問予定',?)", (intro_id, now))
        latest = db.execute("SELECT to_stage FROM stage_events WHERE household_id=? ORDER BY changed_at DESC LIMIT 1",
                            (payload.household_id,)).fetchone()
        if not latest or latest["to_stage"] != "紹介済":
            db.execute(
                "INSERT INTO stage_events(household_id,from_stage,to_stage,changed_by,changed_at) VALUES(?,?,?, ?,?)",
                (payload.household_id, latest["to_stage"] if latest else None, "紹介済",
                 db.execute("SELECT id FROM users WHERE role=?", (x_demo_role,)).fetchone()["id"], now),
            )
        user_id = db.execute("SELECT id FROM users WHERE role=?", (x_demo_role,)).fetchone()["id"]
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
            """SELECT cp.*,c.contract_amount,i.id AS introduction_id,i.partner_id
               FROM construction_projects cp JOIN contracts c ON c.id=cp.contract_id
               JOIN negotiations n ON n.id=c.negotiation_id
               JOIN introductions i ON i.id=n.introduction_id WHERE cp.id=?""", (project_id,)
        ).fetchone()
        if not project:
            raise HTTPException(404, "着工プロジェクトが見つかりません")
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
        db.execute(
            """UPDATE construction_projects SET confirmed_start_date=?,confirmation_evidence=?,
               confirmation_status='confirmed' WHERE id=?""",
            (payload.confirmed_start_date, payload.evidence.strip(), project_id))
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
    transitions = {
        "approve": ("Pending", "Confirmed"),
        "invoice": ("Confirmed", "Invoiced"),
        "paid": ("Invoiced", "Paid"),
    }
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
        db.execute("UPDATE fee_entitlements SET state=? WHERE id=?", (target, entitlement_id))
        db.execute(
            """UPDATE fee_entitlements SET invoice_data_generated=1 WHERE id=? AND ?='Invoiced'""",
            (entitlement_id, target),
        )
        db.execute(
            """UPDATE tasks SET done=1,status='done'
               WHERE related_type='fee_entitlement' AND related_id=? AND task_type=?""",
            (entitlement_id, {"Confirmed": "fee_approval", "Invoiced": "invoice_generation",
                              "Paid": "invoice_unpaid"}[target]),
        )
        if target == "Confirmed":
            db.execute(
                """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
                   related_type,related_id,status)
                   SELECT ?,CONCAT('請求データ生成待ち #',id),CURRENT_DATE,'sla_auto',
                   (SELECT household_id FROM introductions WHERE id=fee_entitlements.introduction_id),
                   'invoice_generation','fee_entitlement',id,'open'
                   FROM fee_entitlements WHERE id=?""",
                (user_id, entitlement_id),
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
        intro = db.execute("SELECT id FROM introductions WHERE id=?", (introduction_id,)).fetchone()
        if not intro:
            raise HTTPException(404, "紹介記録が見つかりません")
        user_id = db.execute("SELECT id FROM users WHERE role=?", (x_demo_role,)).fetchone()
        if not user_id or not payload.reason.strip():
            raise HTTPException(422, "争議理由を入力してください")
        entitlement = db.execute("SELECT * FROM fee_entitlements WHERE introduction_id=?", (introduction_id,)).fetchone()
        if entitlement and entitlement["state"] in ("Invoiced", "Paid"):
            raise HTTPException(409, "請求後の金額は争議状態に変更できません。調整記録が必要です")
        if entitlement:
            db.execute("UPDATE fee_entitlements SET state='Disputed',dispute_reason=? WHERE id=?",
                       (payload.reason.strip(), entitlement["id"]))
            db.execute(
                """INSERT INTO referral_disputes(fee_entitlement_id,raised_by,reason,evidence_level,status,
                   due_date,dispute_type,reference_amount) VALUES(?,?,?,?,'Open',?,'referral',?)""",
                (entitlement["id"], user_id["id"], payload.reason.strip(), payload.evidence_level,
                 date.today() + timedelta(days=14), entitlement["calculated_amount"]),
            )
        db.execute("UPDATE introductions SET status='帰属争议中',existing_customer_flag=1,evidence_note=? WHERE id=?",
                   (payload.reason.strip(), introduction_id))
        home_id = db.execute("SELECT household_id FROM introductions WHERE id=?", (introduction_id,)).fetchone()["household_id"]
        db.execute(
            """INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id,task_type,
               related_type,related_id,status) VALUES(?,?,?,'manual',?,'dispute','introduction',?,'open')""",
            (user_id["id"], f"紹介帰属争議 #{introduction_id}", date.today() + timedelta(days=14),
             home_id, introduction_id),
        )
        audit(db, user_id["id"], "referral_dispute.raised", "introduction", introduction_id, payload.evidence_level)
        db.commit()
    return {"ok": True}


class StageInput(BaseModel):
    to_stage: str


@app.post("/api/households/{household_id}/stage")
def change_stage(household_id: int, payload: StageInput, x_demo_role: str = Header(default="advisor")):
    if payload.to_stage not in STAGES:
        raise HTTPException(422, "不明なステージです")
    with connect() as db:
        current = db.execute("SELECT to_stage FROM stage_events WHERE household_id=? ORDER BY changed_at DESC LIMIT 1",
                             (household_id,)).fetchone()
        if not current:
            raise HTTPException(404, "家庭が見つかりません")
        user = db.execute("SELECT id FROM users WHERE role=?", (x_demo_role,)).fetchone()
        if not user:
            raise HTTPException(400, "不明なデモロールです")
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
