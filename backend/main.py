import json
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
  id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120) NOT NULL, area VARCHAR(120) NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120) NOT NULL, role VARCHAR(40) NOT NULL,
  store_id INT NULL, FOREIGN KEY (store_id) REFERENCES stores(id)
);
CREATE TABLE IF NOT EXISTS households (
  id INT AUTO_INCREMENT PRIMARY KEY, representative_name VARCHAR(120) NOT NULL, store_id INT,
  advisor_id INT, budget_band VARCHAR(120), area_pref VARCHAR(255), land_status VARCHAR(40),
  status VARCHAR(40) NOT NULL DEFAULT 'active', lost_reason TEXT, created_at DATETIME NOT NULL,
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
  FOREIGN KEY (partner_id) REFERENCES partners(id)
);
CREATE TABLE IF NOT EXISTS fee_rules (
  id INT AUTO_INCREMENT PRIMARY KEY, version VARCHAR(80) NOT NULL, type VARCHAR(40) NOT NULL, params JSON NOT NULL,
  base VARCHAR(120) NOT NULL, effective_from DATE NOT NULL, approved_by INT,
  FOREIGN KEY (approved_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS partner_agreements (
  id INT AUTO_INCREMENT PRIMARY KEY, partner_id INT NOT NULL, effective_from DATE NOT NULL,
  effective_to DATE, fee_rule_id INT NOT NULL, status VARCHAR(40) NOT NULL,
  FOREIGN KEY (partner_id) REFERENCES partners(id), FOREIGN KEY (fee_rule_id) REFERENCES fee_rules(id)
);
CREATE TABLE IF NOT EXISTS introductions (
  id INT AUTO_INCREMENT PRIMARY KEY, household_id INT NOT NULL, partner_id INT NOT NULL,
  partner_staff_id INT, introduced_at DATETIME NOT NULL, reception_confirmed_at DATETIME,
  status VARCHAR(80) NOT NULL, existing_customer_flag TINYINT NOT NULL DEFAULT 0, evidence_note TEXT,
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
  FOREIGN KEY (contract_id) REFERENCES contracts(id)
);
CREATE TABLE IF NOT EXISTS fee_entitlements (
  id INT AUTO_INCREMENT PRIMARY KEY, contract_id INT NOT NULL, introduction_id INT NOT NULL,
  fee_rule_id INT NOT NULL, base_amount BIGINT NOT NULL, calculated_amount BIGINT NOT NULL,
  state VARCHAR(40) NOT NULL, dispute_reason TEXT, calculated_at DATETIME NOT NULL, confirmed_by INT,
  FOREIGN KEY (contract_id) REFERENCES contracts(id), FOREIGN KEY (introduction_id) REFERENCES introductions(id),
  FOREIGN KEY (fee_rule_id) REFERENCES fee_rules(id), FOREIGN KEY (confirmed_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS referral_disputes (
  id INT AUTO_INCREMENT PRIMARY KEY, fee_entitlement_id INT NOT NULL, raised_by INT NOT NULL,
  reason TEXT NOT NULL, evidence_level VARCHAR(8) NOT NULL, status VARCHAR(40) NOT NULL, decided_by INT,
  decided_at DATETIME, decision_note TEXT, FOREIGN KEY (fee_entitlement_id) REFERENCES fee_entitlements(id),
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
"""

TABLES = [
    "audit_logs", "daily_report_drafts", "tasks", "data_disclosures", "consents", "referral_disputes",
    "fee_entitlements", "construction_projects", "contracts", "negotiations", "introductions",
    "partner_agreements", "fee_rules", "partner_staff", "partners", "stage_events", "activities",
    "touches", "persons", "households", "users", "stores",
]

STORES = [
    ("新宿店", "東京"), ("池袋店", "東京"), ("立川店", "東京"), ("横浜店", "神奈川"),
    ("川崎店", "神奈川"), ("大宮店", "埼玉"), ("船橋店", "千葉"), ("千葉店", "千葉"),
    ("名古屋店", "愛知"), ("梅田店", "大阪"), ("神戸店", "兵庫"), ("福岡店", "福岡"),
]
STAGES = ["新規予約", "初回相談済", "FP診断済", "紹介済", "訪問・商談中", "契約", "着工", "完了・見送り"]


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
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) FROM stores").fetchone()[0]:
        return
    db.executemany("INSERT INTO stores(name,area) VALUES(?,?)", STORES)
    db.executemany(
        "INSERT INTO users(name,role,store_id) VALUES(?,?,?)",
        [("佐藤 美咲", "advisor", 1), ("田中 健", "manager", 1), ("山本 経理", "hq_finance", None)],
    )
    now = datetime.now().replace(microsecond=0)
    today = date.today()
    households = [
        ("佐々木 遥", "5,000〜6,000万円", "東京都杉並区", "検討中", "active"),
        ("高橋 陽子", "4,000〜5,000万円", "東京都世田谷区", "有", "active"),
        ("鈴木 健太", "6,000〜7,000万円", "東京都練馬区", "無", "active"),
    ]
    for i, household in enumerate(households, 1):
        db.execute(
            """INSERT INTO households(representative_name,store_id,advisor_id,budget_band,area_pref,
               land_status,status,created_at) VALUES(?,1,1,?,?,?, ?,?)""",
            (*household, (today - timedelta(days=14 - i * 4)).isoformat()),
        )
        db.execute("INSERT INTO persons(household_id,name,relation,phone,email) VALUES(?,?,?,?,?)",
                   (i, household[0], "本人", f"090-0000-00{i:02}", f"demo{i}@example.test"))
        for days_ago, channel, campaign, method in [
            (30 - i * 2, "Web広告", "春の家づくり相談", "UTM"),
            (14 - i * 2, "直接来店", "", "手入力"),
        ]:
            db.execute(
                """INSERT INTO touches(household_id,touch_at,channel,campaign_id,creative_id,
                   tracking_code,landing_referrer,store_id,capture_method) VALUES(?,?,?,?,?,?,?,?,?)""",
                (i, (today - timedelta(days=days_ago)).isoformat(), channel, campaign or None,
                 "creative-a" if campaign else None, f"DEMO-{i}-{days_ago}", "demo.example.test", 1, method),
            )
        db.execute(
            "INSERT INTO stage_events(household_id,from_stage,to_stage,changed_by,changed_at) VALUES(?,NULL,'新規予約',1,?)",
            (i, (today - timedelta(days=14 - i * 4)).isoformat()),
        )
        db.execute(
            """INSERT INTO activities(household_id,user_id,type,body,acted_at,next_action,next_action_due)
               VALUES(?,1,'面談','ご希望条件と住まいづくりの進め方を相談しました',?,?,?)""",
            (i, (now - timedelta(days=i)).isoformat(), "候補会社のご紹介", (today + timedelta(days=1 - i)).isoformat()),
        )
    db.executemany(
        "INSERT INTO partners(name,area,tags,active) VALUES(?,?,?,1)",
        [
            ("青葉ホーム", "東京", '["価格","土地探し"]'),
            ("みらい住建", "東京", '["性能","耐震"]'),
            ("木の香デザイン", "東京", '["デザイン","自然素材"]'),
            ("ひだまり工務店", "神奈川", '["価格","地域密着"]'),
            ("空と家住宅", "埼玉", '["性能","省エネ"]'),
        ],
    )
    db.executemany("INSERT INTO partner_staff(partner_id,name) VALUES(?,?)",
                   [(1, "小林"), (2, "伊藤"), (3, "森"), (4, "吉田"), (5, "斎藤")])
    db.execute(
        """INSERT INTO fee_rules(version,type,params,base,effective_from,approved_by)
           VALUES('2026.1','rate','{"rate":0.02}','請負金額',?,3)""", (today.replace(month=1, day=1).isoformat(),)
    )
    db.execute("INSERT INTO partner_agreements(partner_id,effective_from,fee_rule_id,status) VALUES(1,?,1,'active')",
               (today.replace(month=1, day=1).isoformat(),))
    for partner_id, negotiation_status in [(1, "契約"), (2, "商談中"), (3, "訪問予定")]:
        intro_id = db.execute(
            """INSERT INTO introductions(household_id,partner_id,partner_staff_id,introduced_at,
               reception_confirmed_at,status) VALUES(1,?,?,?,?,'受付確認済')""",
            (partner_id, partner_id, (today - timedelta(days=10)).isoformat(), (today - timedelta(days=9)).isoformat()),
        ).lastrowid
        nego_id = db.execute("INSERT INTO negotiations(introduction_id,status,last_activity_at) VALUES(?,?,?)",
                             (intro_id, negotiation_status, (today - timedelta(days=2)).isoformat())).lastrowid
        if partner_id == 1:
            contract_id = db.execute(
                """INSERT INTO contracts(negotiation_id,contract_date,contract_amount,builder_contact)
                   VALUES(?,?,32000000,'小林')""", (nego_id, (today - timedelta(days=4)).isoformat())
            ).lastrowid
            db.execute(
                """INSERT INTO construction_projects(contract_id,planned_start_date,actual_start_date)
                   VALUES(?,?,?)""", (contract_id, (today + timedelta(days=7)).isoformat(), (today - timedelta(days=1)).isoformat())
            )
    for i in range(1, 4):
        db.execute("INSERT INTO consents(household_id,purpose,scope,granted_at) VALUES(?,?,?,?)",
                   (i, "住宅会社への希望条件共有", "L3", (today - timedelta(days=8)).isoformat()))
    db.execute(
        "INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id) VALUES(1,'佐々木様へ候補会社をフォロー',?,'sla_auto',1)",
        ((today - timedelta(days=1)).isoformat(),),
    )
    db.execute(
        "INSERT INTO tasks(assignee_id,title,due_at,source,related_household_id) VALUES(1,'高橋様へ次回相談の日程確認',?,'manual',2)",
        (today.isoformat(),),
    )
    summary = db.execute("SELECT COUNT(*) FROM activities WHERE user_id=1 AND DATE(acted_at)=CURRENT_DATE").fetchone()[0]
    db.execute("INSERT INTO daily_report_drafts(user_id,report_date,auto_summary,manual_note) VALUES(1,?,?, '')",
               (today.isoformat(), f"本日の活動 {summary} 件。面談・紹介状況を確認してください。"))
    db.commit()


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
    if x_demo_role not in ("advisor", "manager", "hq_finance"):
        raise HTTPException(400, "不明なデモロールです")
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE role=?", (x_demo_role,)).fetchone()
        households = [dict(row) for row in db.execute(
            """SELECT h.*,s.name AS store_name,u.name AS advisor_name FROM households h
               LEFT JOIN stores s ON s.id=h.store_id LEFT JOIN users u ON u.id=h.advisor_id ORDER BY h.id"""
        )]
        for household in households:
            household["persons"] = [dict(r) for r in db.execute("SELECT * FROM persons WHERE household_id=?", (household["id"],))]
            touches = [dict(r) for r in db.execute("SELECT * FROM touches WHERE household_id=? ORDER BY touch_at", (household["id"],))]
            household["touches"] = touches
            household["first_touch"] = touches[0] if touches else None
            household["latest_touch"] = touches[-1] if touches else None
            household["stage_events"] = [dict(r) for r in db.execute(
                "SELECT e.*,u.name AS changed_by_name FROM stage_events e LEFT JOIN users u ON u.id=e.changed_by WHERE household_id=? ORDER BY changed_at",
                (household["id"],))]
            household["activities"] = [dict(r) for r in db.execute(
                "SELECT a.*,u.name AS user_name FROM activities a LEFT JOIN users u ON u.id=a.user_id WHERE household_id=? ORDER BY acted_at DESC",
                (household["id"],))]
            household["introductions"] = [dict(r) for r in db.execute(
                """SELECT i.*,p.name AS partner_name,ps.name AS staff_name,n.id AS negotiation_id,
                   n.status AS negotiation_status,n.last_activity_at,c.id AS contract_id,c.contract_date,
                   c.contract_amount,cp.id AS project_id,cp.planned_start_date,cp.actual_start_date,
                   cp.confirmed_start_date,cp.confirmation_evidence,fe.id AS entitlement_id,
                   fe.calculated_amount,fe.state AS entitlement_state,fe.dispute_reason
                   FROM introductions i JOIN partners p ON p.id=i.partner_id
                   LEFT JOIN partner_staff ps ON ps.id=i.partner_staff_id
                   LEFT JOIN negotiations n ON n.introduction_id=i.id
                   LEFT JOIN contracts c ON c.negotiation_id=n.id
                   LEFT JOIN construction_projects cp ON cp.contract_id=c.id
                   LEFT JOIN fee_entitlements fe ON fe.introduction_id=i.id
                   WHERE i.household_id=? ORDER BY i.id""", (household["id"],))]
            household["consents"] = [dict(r) for r in db.execute(
                "SELECT * FROM consents WHERE household_id=? ORDER BY granted_at DESC", (household["id"],))]
            household["disclosures"] = [dict(r) for r in db.execute(
                "SELECT * FROM data_disclosures WHERE household_id=? ORDER BY disclosed_at DESC", (household["id"],))]
        store_filter = "WHERE h.store_id=?" if x_demo_role in ("advisor", "manager") else ""
        store_args = (user["store_id"],) if store_filter else ()
        activities_today = db.execute(
            f"SELECT COUNT(*) FROM activities a JOIN households h ON h.id=a.household_id {store_filter} AND DATE(a.acted_at)=CURRENT_DATE"
            if store_filter else "SELECT COUNT(*) FROM activities WHERE DATE(acted_at)=CURRENT_DATE",
            (*store_args,) if store_filter else (),
        ).fetchone()[0]
        overdue = [dict(r) for r in db.execute(
            f"SELECT t.*,h.representative_name FROM tasks t LEFT JOIN households h ON h.id=t.related_household_id "
            f"WHERE t.done=0 AND DATE(t.due_at)<CURRENT_DATE"
            + (" AND (t.assignee_id=? OR h.store_id=?)" if x_demo_role != "hq_finance" else ""),
            (user["id"], user["store_id"]) if x_demo_role != "hq_finance" else (),
        )]
        entitlements = [dict(r) for r in db.execute(
            """SELECT fe.*,fr.version AS rule_version,fr.type AS rule_type,fr.params,fr.base,
               h.representative_name,p.name AS partner_name,c.contract_amount
               FROM fee_entitlements fe JOIN contracts c ON c.id=fe.contract_id
               JOIN negotiations n ON n.id=(SELECT negotiation_id FROM contracts WHERE id=fe.contract_id)
               JOIN introductions i ON i.id=fe.introduction_id JOIN households h ON h.id=i.household_id
               JOIN partners p ON p.id=i.partner_id JOIN fee_rules fr ON fr.id=fe.fee_rule_id ORDER BY fe.id"""
        )]
        return {
            "user": dict(user), "roles": [{"id": "advisor", "name": "顧問"}, {"id": "manager", "name": "店長"}, {"id": "hq_finance", "name": "本社・経理"}],
            "stores": [dict(r) for r in db.execute("SELECT * FROM stores ORDER BY id")],
            "partners": [dict(r) for r in db.execute("SELECT * FROM partners WHERE active=1 ORDER BY name")],
            "partner_staff": [dict(r) for r in db.execute("SELECT * FROM partner_staff ORDER BY partner_id")],
            "households": households, "entitlements": entitlements, "overdue_tasks": overdue,
            "activity_count_today": activities_today,
            "disputed_count": db.execute("SELECT COUNT(*) FROM fee_entitlements WHERE state='Disputed'").fetchone()[0],
            "pending_confirmation_count": db.execute(
                "SELECT COUNT(*) FROM fee_entitlements WHERE state IN ('PendingConfirmation','Confirmed')").fetchone()[0],
            "stage_names": STAGES,
            "audit_logs": [dict(r) for r in db.execute(
                """SELECT a.*,u.name AS user_name FROM audit_logs a LEFT JOIN users u ON u.id=a.user_id
                   ORDER BY a.`at` DESC LIMIT 25""")],
            "daily_report": dict(db.execute("SELECT * FROM daily_report_drafts WHERE user_id=? ORDER BY id DESC LIMIT 1", (user["id"],)).fetchone())
            if db.execute("SELECT 1 FROM daily_report_drafts WHERE user_id=? LIMIT 1", (user["id"],)).fetchone() else None,
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
        db.execute(
            """INSERT INTO activities(household_id,user_id,type,body,acted_at,next_action,next_action_due)
               VALUES(?,?,?,?,?,?,?)""",
            (payload.household_id, user["id"], payload.type, payload.body,
             datetime.now().isoformat(timespec="seconds"), payload.next_action, payload.next_action_due),
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
    role_guard(x_demo_role, ("manager", "hq_finance"))
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
    transitions = {"invoice": ("Confirmed", "Invoiced"), "paid": ("Invoiced", "Paid")}
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
                """INSERT INTO referral_disputes(fee_entitlement_id,raised_by,reason,evidence_level,status)
                   VALUES(?,?,?,?,'Open')""",
                (entitlement["id"], user_id["id"], payload.reason.strip(), payload.evidence_level),
            )
        db.execute("UPDATE introductions SET status='帰属争议中',existing_customer_flag=1,evidence_note=? WHERE id=?",
                   (payload.reason.strip(), introduction_id))
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
