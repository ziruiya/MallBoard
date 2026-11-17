import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity, ArrowDownRight, ArrowUpRight, BadgeJapaneseYen, Bell, Building2, CalendarDays,
  Check, ChevronDown, ChevronRight, CircleAlert, ClipboardList, Clock3, FileText, Filter,
  Home, Languages, LayoutDashboard, LogOut, Menu, Plus, Search, Settings, ShieldCheck,
  Users, WalletCards, X,
} from "lucide-react";
import "./style.css";

const COPY = {
  ja: {
    product: "MallBoard", subtitle: "住宅相談ビジネス・業務基盤", today: "今日の業務",
    households: "顧客・世帯", introductions: "紹介・商談", revenue: "着工・報酬",
    management: "経営・管理", settings: "設定", search: "顧客・会社を検索…",
    todayTitle: "おはようございます、", todaySub: "今日の業務状況を確認しましょう。",
    appointments: "今日の予約", followups: "今日のフォロー", overdue: "超過タスク",
    activities: "本日の活動", household: "世帯", open: "開く", quickActivity: "活動を記録",
    dailyReport: "日報ドラフト", autoSummary: "自動サマリー", note: "今日のメモ",
    save: "保存する", pipeline: "紹介パイプライン", recentHouseholds: "担当世帯",
    viewAll: "すべて見る", stage: "現在ステージ", nextAction: "次のアクション",
    due: "期限", partner: "住宅会社", status: "ステータス", elapsed: "経過",
    contract: "契約", actualStart: "実際着工", confirmStart: "着工確認",
    confirmationEvidence: "確認証跡・メモ", confirm: "着工を確認して報酬を確定",
    entitlement: "報酬権利", basis: "計算根拠", amount: "報酬額", rule: "適用ルール",
    invoice: "請求へ", paid: "入金済みにする", disputed: "争議中", frozen: "請求対象外・金額凍結",
    partnerCreate: "紹介を追加", partnerSelect: "住宅会社", staffSelect: "担当者",
    add: "追加する", introduced: "紹介済", received: "受付確認済", negotiating: "商談中",
    scheduled: "訪問予定", visited: "訪問済", quoted: "見積提示", declined: "見送り",
    stages: "ステージ", firstTouch: "初回流入", latestTouch: "最新流入",
    consent: "同意・情報共有", audit: "監査ログ", controls: "管理・統制",
    stores: "店舗", funnel: "店舗別ファネル", monthly: "月別着工数・報酬",
    roi: "集客チャネルROI", risk: "争議・既存顧客", ruleVersions: "報酬ルール履歴",
    demoWarning: "すべて架空のデモデータです。", prototype: "非公式プロトタイプ",
    roleAdvisor: "顧問", roleManager: "店長", roleFinance: "本社・経理",
    role: "デモロール", language: "言語", reset: "デモデータをリセット",
    resetConfirm: "デモデータを初期状態に戻します。よろしいですか？",
    resetDone: "デモデータを初期状態に戻しました。", noRows: "表示するデータがありません。",
    first: "初回", last: "最新", person: "ご家族", budget: "ご予算", area: "希望エリア",
    land: "土地", history: "ステージ履歴", activitiesHistory: "活動履歴",
    introduction: "紹介先", negotiations: "並行商談", people: "担当者", show: "詳細",
    close: "閉じる", addActivity: "活動を登録", activityType: "活動種別", body: "内容",
    nextDue: "次回期限", send: "登録", cancel: "キャンセル", meeting: "面談", phone: "電話",
    line: "LINE", visit: "訪問同行", memo: "メモ", success: "操作が完了しました。",
    error: "操作に失敗しました。", find: "検索", all: "すべて", choose: "選択してください",
    stageNow: "ステージを更新", selectStage: "ステージ", record: "更新する",
    startPlanned: "着工予定", confirmed: "着工確認済", evidence: "証跡",
    review: "詳細を確認", days: "日", noEntitlement: "着工確認後に報酬権利が生成されます。",
    amountRule: "請負金額 × 料率", currentRole: "表示ロール", loggingOut: "ログアウト",
  },
  zh: {
    product: "MallBoard", subtitle: "住宅咨询业务管理平台", today: "今日工作",
    households: "客户家庭", introductions: "介绍与洽谈", revenue: "开工与报酬",
    management: "经营管理", settings: "设置", search: "搜索客户或公司…",
    todayTitle: "早上好，", todaySub: "查看今天的业务进展。",
    appointments: "今日预约", followups: "今日跟进", overdue: "超期任务",
    activities: "今日活动", household: "家庭", open: "打开", quickActivity: "记录活动",
    dailyReport: "日报草稿", autoSummary: "自动汇总", note: "今日备注",
    save: "保存", pipeline: "介绍管道", recentHouseholds: "负责家庭",
    viewAll: "查看全部", stage: "当前阶段", nextAction: "下一步", due: "截止日期",
    partner: "住宅公司", status: "状态", elapsed: "停留", contract: "签约",
    actualStart: "实际开工", confirmStart: "开工确认", confirmationEvidence: "确认依据/备注",
    confirm: "确认开工并生成报酬", entitlement: "报酬权利", basis: "计算依据", amount: "报酬金额",
    rule: "适用规则", invoice: "转为请款", paid: "标记已付款", disputed: "争议中",
    frozen: "不可请款 · 金额已冻结", partnerCreate: "新增介绍", partnerSelect: "住宅公司",
    staffSelect: "负责人", add: "添加", introduced: "已介绍", received: "已确认受理",
    negotiating: "洽谈中", scheduled: "预约访问", visited: "已访问", quoted: "已报价",
    declined: "未继续", stages: "业务阶段", firstTouch: "首次来源", latestTouch: "最近来源",
    consent: "授权与信息共享", audit: "审计日志", controls: "经营与管控", stores: "门店",
    funnel: "门店漏斗", monthly: "月度开工与报酬", roi: "获客渠道 ROI",
    risk: "争议与既有客户", ruleVersions: "报酬规则版本", demoWarning: "所有数据均为虚构演示数据。",
    prototype: "非正式原型", roleAdvisor: "顾问", roleManager: "店长", roleFinance: "总部·财务",
    role: "演示角色", language: "语言", reset: "重置演示数据",
    resetConfirm: "将演示数据恢复到初始状态，确定吗？", resetDone: "演示数据已恢复初始状态。",
    noRows: "暂无数据。", first: "首次", last: "最近", person: "家庭成员", budget: "预算",
    area: "意向区域", land: "土地", history: "阶段记录", activitiesHistory: "活动记录",
    introduction: "介绍对象", negotiations: "并行洽谈", people: "负责人", show: "查看详情",
    close: "关闭", addActivity: "记录活动", activityType: "活动类型", body: "内容",
    nextDue: "下次跟进日期", send: "提交", cancel: "取消", meeting: "面谈", phone: "电话",
    line: "LINE", visit: "陪同访问", memo: "备注", success: "操作成功。",
    error: "操作失败。", find: "搜索", all: "全部", choose: "请选择",
    stageNow: "更新阶段", selectStage: "阶段", record: "更新",
    startPlanned: "计划开工", confirmed: "已确认开工", evidence: "凭据",
    review: "查看详情", days: "天", noEntitlement: "确认开工后将生成报酬权利。",
    amountRule: "合同金额 × 费率", currentRole: "当前角色", loggingOut: "退出登录",
  },
};

const ROLE_LABEL = { ja: { advisor: "顧問", manager: "店長", hq_finance: "本社・経理" },
  zh: { advisor: "顾问", manager: "店长", hq_finance: "总部·财务" } };
const NAV = [
  ["dashboard", LayoutDashboard, "today"], ["households", Users, "households"],
  ["introductions", ArrowDownRight, "introductions"], ["revenue", BadgeJapaneseYen, "revenue"],
  ["management", Building2, "management"], ["settings", Settings, "settings"],
];
const API_BASE = import.meta.env.VITE_API_BASE || "";

function App() {
  const [locale, setLocale] = useState(localStorage.getItem("mallboard-locale") || "ja");
  const [role, setRole] = useState(localStorage.getItem("mallboard-role") || "advisor");
  const [page, setPage] = useState("dashboard");
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [modal, setModal] = useState("");
  const [query, setQuery] = useState("");
  const [toast, setToast] = useState("");
  const [busy, setBusy] = useState(false);
  const t = (key) => COPY[locale][key] || key;

  async function load() {
    const response = await fetch(`${API_BASE}/api/bootstrap`, { headers: { "X-Demo-Role": role } });
    if (!response.ok) throw new Error("load failed");
    const result = await response.json();
    setData(result);
    if (selected) setSelected(result.households.find((h) => h.id === selected.id) || null);
  }
  useEffect(() => {
    localStorage.setItem("mallboard-locale", locale);
    document.documentElement.lang = locale;
  }, [locale]);
  useEffect(() => {
    localStorage.setItem("mallboard-role", role);
    load().catch(() => setToast("API connection failed"));
  }, [role]);
  useEffect(() => {
    if (!toast) return undefined;
    const id = setTimeout(() => setToast(""), 3000);
    return () => clearTimeout(id);
  }, [toast]);

  async function api(path, method = "POST", body) {
    setBusy(true);
    try {
      const response = await fetch(`${API_BASE}${path}`, {
        method, headers: { "Content-Type": "application/json", "X-Demo-Role": role },
        body: body ? JSON.stringify(body) : undefined,
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || t("error"));
      }
      await load();
      setToast(t("success"));
      return await response.json();
    } catch (error) {
      setToast(error.message || t("error"));
      throw error;
    } finally { setBusy(false); }
  }

  const filtered = useMemo(() => (data?.households || []).filter((h) =>
    `${h.representative_name} ${h.area_pref}`.toLowerCase().includes(query.toLowerCase())), [data, query]);
  const roleOptions = data?.roles || [{ id: "advisor" }, { id: "manager" }, { id: "hq_finance" }];
  const openHousehold = (household) => { setSelected(household); setModal("household"); };

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Home size={21}/></div><div><b>MallBoard</b><span>{t("subtitle")}</span></div></div>
      <div className="workspace-label">WORKSPACE</div>
      <nav>{NAV.map(([id, Icon, key]) => <button key={id} onClick={() => setPage(id)}
        className={`nav-item ${page === id ? "active" : ""}`}><Icon size={18}/><span>{t(key)}</span>
        {id === "revenue" && data?.pending_confirmation_count > 0 && <em>{data.pending_confirmation_count}</em>}
      </button>)}</nav>
      <div className="sidebar-spacer"/>
      <div className="role-card"><div className="avatar">{role === "hq_finance" ? "経" : role === "manager" ? "店" : "佐"}</div>
        <div className="role-meta"><b>{data?.user?.name || "Loading…"}</b><span>{ROLE_LABEL[locale][role]}</span></div>
        <ChevronDown size={16} className="muted"/></div>
      <div className="sidebar-foot">DEMO ENVIRONMENT <span>●</span></div>
    </aside>
    <main className="main">
      <header className="topbar">
        <div className="breadcrumb"><span>{t("product")}</span><ChevronRight size={14}/><b>{t(NAV.find(([id]) => id === page)?.[2] || page)}</b></div>
        <div className="top-actions">
          <label className="searchbox"><Search size={16}/><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("search")}/><kbd>⌘ K</kbd></label>
          <button className="icon-btn" title="Notifications"><Bell size={18}/><i/></button>
          <div className="select-wrap"><Users size={15}/><select aria-label={t("role")} value={role} onChange={(e) => setRole(e.target.value)}>
            {roleOptions.map((option) => <option value={option.id} key={option.id}>{ROLE_LABEL[locale][option.id]}</option>)}
          </select><ChevronDown size={13}/></div>
          <button className="language-btn" onClick={() => setLocale(locale === "ja" ? "zh" : "ja")} title={t("language")}><Languages size={16}/>{locale === "ja" ? "中文" : "日本語"}</button>
        </div>
      </header>
      <div className="page-content">
        {!data ? <div className="loading"><div className="spinner"/>Loading MallBoard…</div> : <>
          {page === "dashboard" && <Dashboard data={data} t={t} role={role} onHousehold={openHousehold}
            onActivity={() => setModal("activity")} onNavigate={setPage}
            onReport={(body) => api("/api/report", "PUT", { manual_note: body })}/>}
          {page === "households" && <Households items={filtered} t={t} onOpen={openHousehold}/>}
          {page === "introductions" && <Introductions items={filtered} t={t} onOpen={openHousehold}
            onAdd={(household) => { setSelected(household); setModal("introduction"); }}/>}
          {page === "revenue" && <Revenue data={data} t={t} role={role} api={api} onOpen={openHousehold}/>}
          {page === "management" && <Management data={data} t={t}/>}
          {page === "settings" && <SettingsPage data={data} t={t} role={role} locale={locale} onReset={async () => {
            if (window.confirm(t("resetConfirm"))) { await api("/api/reset"); setToast(t("resetDone")); }
          }}/>}
        </>}
      </div>
      <footer className="app-footer"><ShieldCheck size={14}/>{t("prototype")} · {t("demoWarning")}<span>© MallBoard Demo</span></footer>
    </main>
    {modal === "household" && selected && <HouseholdModal household={selected} t={t} role={role}
      onClose={() => setModal("")} onActivity={() => setModal("activity")} api={api}/>}
    {modal === "activity" && <ActivityModal households={data?.households || []} t={t} onClose={() => setModal("")}
      onSubmit={(body) => api("/api/activities", "POST", body)}/>}
    {modal === "introduction" && selected && <IntroductionModal household={selected} data={data} t={t}
      onClose={() => setModal("")} onSubmit={(body) => api("/api/introductions", "POST", body)}/>}
    {toast && <div className={`toast ${toast === t("error") ? "toast-error" : ""}`}><Check size={17}/>{toast}</div>}
    {busy && <div className="busy-indicator"><div className="spinner"/></div>}
  </div>;
}

function PageTitle({ eyebrow, title, sub, actions }) {
  return <div className="page-title"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h1>{title}</h1>{sub && <p>{sub}</p>}</div>{actions && <div className="title-actions">{actions}</div>}</div>;
}
function Metric({ label, value, delta, icon: Icon, tone = "blue", small }) {
  return <div className={`metric-card ${small ? "metric-small" : ""}`}><div className={`metric-icon ${tone}`}><Icon size={18}/></div>
    <div className="metric-info"><span>{label}</span><strong>{value}</strong>{delta && <small>{delta}</small>}</div>
    {delta && <div className="metric-spark"><ArrowUpRight size={16}/></div>}</div>;
}
function Dashboard({ data, t, role, onHousehold, onActivity, onNavigate, onReport }) {
  const [note, setNote] = useState(data.daily_report?.manual_note || "");
  const appointments = data.households.filter((h) => h.status === "active").length;
  const followups = data.households.reduce((n, h) => n + h.activities.filter((a) => a.next_action_due && a.next_action_due <= new Date().toISOString().slice(0, 10)).length, 0);
  const recent = data.households.slice(0, 4);
  const introCount = data.households.reduce((n, h) => n + h.introductions.length, 0);
  return <><PageTitle eyebrow={new Date().toLocaleDateString("ja-JP", { year: "numeric", month: "long", day: "numeric", weekday: "long" })}
    title={<>{t("todayTitle")}<span>{data.user.name}さん</span></>} sub={t("todaySub")}
    actions={<button className="primary-btn" onClick={onActivity}><Plus size={16}/>{t("quickActivity")}</button>}/>
    <div className="metrics-grid">
      <Metric label={t("appointments")} value={String(appointments).padStart(2, "0")} delta="+2.4%" icon={CalendarDays}/>
      <Metric label={t("followups")} value={String(followups).padStart(2, "0")} delta={t("today")} icon={Activity} tone="violet"/>
      <Metric label={t("overdue")} value={String(data.overdue_tasks.length).padStart(2, "0")} delta={role === "hq_finance" ? t("disputed") : "要対応"} icon={Clock3} tone="orange"/>
      <Metric label={t("activities")} value={String(data.activity_count_today).padStart(2, "0")} delta="活動ログ" icon={ClipboardList} tone="green"/>
    </div>
    <div className="dashboard-grid">
      <section className="panel pipeline-panel"><div className="panel-head"><div><div className="eyebrow">OVERVIEW</div><h2>{t("pipeline")}</h2></div>
        <button className="text-button" onClick={() => onNavigate("introductions")}>{t("viewAll")} <ChevronRight size={15}/></button>
      </div>
        <div className="pipeline-summary"><div><strong>{data.households.length}</strong><span>{t("households")}</span></div><div className="pipeline-divider"/>
          <div><strong>{introCount}</strong><span>{t("introductions")}</span></div><div className="pipeline-divider"/>
          <div><strong>{data.entitlements.length}</strong><span>{t("entitlement")}</span></div></div>
        <StageFunnel items={data.households} t={t}/>
      </section>
      <section className="panel tasks-panel"><div className="panel-head"><div><div className="eyebrow">ACTION REQUIRED</div><h2>{t("overdue")}</h2></div><span className="pill pill-red">{data.overdue_tasks.length} overdue</span></div>
        {data.overdue_tasks.length ? data.overdue_tasks.map((task) => <div className="task-row" key={task.id}>
          <div className="task-check"><CircleAlert size={16}/></div><div className="task-copy"><b>{task.title}</b><span>{task.representative_name} · {task.due_at}</span></div>
          <button className="icon-btn compact" onClick={() => onHousehold(data.households.find((h) => h.id === task.related_household_id))}><ChevronRight size={16}/></button>
        </div>) : <div className="empty-mini"><Check size={17}/>{t("noRows")}</div>}
        <div className="task-bottom"><span><Clock3 size={14}/>{t("today")} 09:00 — 18:00</span><button className="text-button">{t("review")} <ChevronRight size={14}/></button></div>
      </section>
    </div>
    <div className="lower-grid">
      <section className="panel household-panel"><div className="panel-head"><div><div className="eyebrow">CUSTOMER SUCCESS</div><h2>{t("recentHouseholds")}</h2></div>
        <button className="text-button" onClick={() => onNavigate("households")}>{t("viewAll")} <ChevronRight size={15}/></button></div>
        <HouseholdTable items={recent} t={t} onOpen={onHousehold}/></section>
      <section className="panel report-panel"><div className="panel-head"><div><div className="eyebrow">DAILY SUMMARY</div><h2>{t("dailyReport")}</h2></div><FileText size={17} className="muted"/></div>
        <div className="auto-summary"><div className="summary-icon"><Activity size={16}/></div><div><span>{t("autoSummary")}</span><p>{data.daily_report?.auto_summary || `本日の活動 ${data.activity_count_today} 件。`}</p></div></div>
        <label className="field-label">{t("note")}<textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="..." rows="3"/></label>
        <button className="secondary-btn full-width" onClick={() => onReport(note)}><Check size={15}/>{t("save")}</button>
      </section>
    </div>
  </>;
}
function StageFunnel({ items, t }) {
  const order = ["新規予約", "初回相談済", "FP診断済", "紹介済", "訪問・商談中", "契約", "着工", "完了・見送り"];
  return <div className="funnel-list">{order.slice(0, 6).map((stage, i) => {
    const count = items.filter((h) => h.stage_events.at(-1)?.to_stage === stage).length;
    return <div className="funnel-row" key={stage}><span className="funnel-index">{String(i + 1).padStart(2, "0")}</span><span className="funnel-name">{stage}</span>
      <div className="funnel-track"><i style={{ width: `${items.length ? Math.max(4, count / items.length * 100) : 0}%` }}/></div><b>{count}</b><small>{items.length ? `${Math.round(count / items.length * 100)}%` : "0%"}</small></div>;
  })}</div>;
}
function HouseholdTable({ items, t, onOpen }) {
  return <div className="table-scroll"><table><thead><tr><th>{t("household")}</th><th>{t("stage")}</th><th>{t("nextAction")}</th><th>{t("due")}</th><th/></tr></thead>
    <tbody>{items.map((h) => { const task = h.activities.find((a) => a.next_action); return <tr key={h.id} onClick={() => onOpen(h)} className="click-row">
      <td><div className="customer-cell"><div className="customer-avatar">{h.representative_name.slice(0, 1)}</div><div><b>{h.representative_name}</b><span>{h.area_pref}</span></div></div></td>
      <td><span className="stage-tag">{h.stage_events.at(-1)?.to_stage}</span></td><td>{task?.next_action || "—"}</td><td className={task?.next_action_due < new Date().toISOString().slice(0, 10) ? "text-danger" : ""}>{task?.next_action_due || "—"}</td>
      <td><ChevronRight size={15} className="muted"/></td></tr>;})}</tbody></table>
    {!items.length && <div className="empty-state">{t("noRows")}</div>}</div>;
}
function Households({ items, t, onOpen }) {
  return <><PageTitle eyebrow="CUSTOMER RELATIONSHIP" title={t("households")} sub="顧客情報・接点・商談状況を一元管理"/>
    <section className="panel table-panel"><div className="panel-head"><div><h2>{t("households")} <span className="count-badge">{items.length}</span></h2></div>
      <div className="table-tools"><button className="filter-btn"><Filter size={15}/>{t("all")}<ChevronDown size={13}/></button></div></div>
      <HouseholdTable items={items} t={t} onOpen={onOpen}/></section></>;
}
function Introductions({ items, t, onOpen, onAdd }) {
  const [activeHousehold, setActiveHousehold] = useState(items[0]?.id || null);
  useEffect(() => { if (!items.some((h) => h.id === activeHousehold)) setActiveHousehold(items[0]?.id || null); }, [items, activeHousehold]);
  const household = items.find((h) => h.id === activeHousehold);
  return <><PageTitle eyebrow="PARTNER JOURNEY" title={t("introductions")} sub="一つの家庭に対する複数住宅会社との並行商談を追跡"/>
    <div className="intro-layout"><section className="panel intro-list"><div className="panel-head"><h2>{t("households")}</h2><span className="count-badge">{items.length}</span></div>
      {items.map((h) => <button className={`intro-household ${activeHousehold === h.id ? "selected" : ""}`} key={h.id} onClick={() => setActiveHousehold(h.id)}>
        <div className="customer-avatar">{h.representative_name.slice(0, 1)}</div><div><b>{h.representative_name}</b><span>{h.area_pref}</span></div><span className="intro-count">{h.introductions.length}</span>
      </button>)}</section>
      {household ? <section className="intro-detail"><div className="panel intro-context"><div><div className="eyebrow">{household.store_name} · {household.advisor_name}</div><h2>{household.representative_name}</h2><span>{household.budget_band} · {household.area_pref}</span></div>
        <button className="secondary-btn" onClick={() => onAdd(household)}><Plus size={15}/>{t("partnerCreate")}</button></div>
        <div className="partner-grid">{household.introductions.map((intro) => <PartnerCard key={intro.id} intro={intro} t={t} onOpen={() => onOpen(household)}/>)}
          {!household.introductions.length && <button className="add-partner-card" onClick={() => onAdd(household)}><Plus size={20}/>{t("partnerCreate")}</button>}</div>
      </section> : <section className="panel empty-state">{t("noRows")}</section>}
    </div></>;
}
function PartnerCard({ intro, t, onOpen }) {
  const elapsed = Math.max(0, Math.floor((Date.now() - new Date(intro.introduced_at).getTime()) / 86400000));
  const state = intro.entitlement_state;
  return <article className={`partner-card ${state === "Disputed" ? "disputed-card" : ""}`}>
    <div className="partner-card-head"><div className="partner-icon"><Building2 size={18}/></div><div><b>{intro.partner_name}</b><span>{intro.staff_name || "—"} · {intro.introduced_at}</span></div>
      {intro.existing_customer_flag ? <span className="pill pill-red">{t("disputed")}</span> : <span className="pill pill-blue">{t(intro.status === "受付確認済" ? "received" : "introduced")}</span>}</div>
    <div className="negotiation-status"><div><small>{t("status")}</small><b>{intro.negotiation_status || "紹介済"}</b></div><div><small>{t("elapsed")}</small><b>{elapsed} {t("days")}</b></div><div><small>{t("last")}</small><b>{intro.last_activity_at || "—"}</b></div></div>
    {intro.contract_id && <div className="contract-highlight"><div className="contract-icon"><Check size={15}/></div><div><b>{t("contract")} · ¥{Number(intro.contract_amount).toLocaleString()}</b><span>{intro.contract_date}</span></div></div>}
    {state === "Disputed" && <div className="frozen-banner"><CircleAlert size={15}/>{t("frozen")}</div>}
    <button className="card-link" onClick={onOpen}>{t("review")} <ChevronRight size={14}/></button>
  </article>;
}
function Revenue({ data, t, role, api, onOpen }) {
  const household = data.households.find((h) => h.introductions.some((i) => i.project_id || i.contract_id));
  const project = household?.introductions.find((i) => i.project_id);
  const feeRuleParams = (value) => typeof value === "string" ? JSON.parse(value) : value;
  return <><PageTitle eyebrow="CONSTRUCTION & REVENUE" title={t("revenue")} sub="予定・実際・確認を分けて記録し、報酬の根拠と状態を追跡"/>
    <div className="revenue-metrics"><Metric small label={t("entitlement")} value={String(data.entitlements.length).padStart(2, "0")} icon={WalletCards}/>
      <Metric small label={t("pending_confirmation_count") in data ? "確認待ち・処理待ち" : t("confirmStart")} value={String(data.pending_confirmation_count).padStart(2, "0")} icon={Clock3} tone="orange"/>
      <Metric small label={t("disputed")} value={String(data.disputed_count).padStart(2, "0")} icon={CircleAlert} tone="red"/>
      <Metric small label={t("amount")} value={`¥${data.entitlements.reduce((n, e) => n + e.calculated_amount, 0).toLocaleString()}`} icon={BadgeJapaneseYen} tone="green"/></div>
    {project ? <ConstructionCard household={household} project={project} data={data} t={t} role={role} api={api}/> :
      <div className="panel empty-state">{t("noEntitlement")}</div>}
    <section className="panel entitlement-panel"><div className="panel-head"><div><div className="eyebrow">REVENUE LEDGER</div><h2>{t("entitlement")}</h2></div>
      <span className="pill pill-green">APPEND-ONLY AUDIT</span></div>
      <div className="table-scroll"><table><thead><tr><th>{t("household")}</th><th>{t("partner")}</th><th>{t("basis")}</th><th>{t("rule")}</th><th>{t("amount")}</th><th>{t("status")}</th><th/></tr></thead><tbody>
      {data.entitlements.map((e) => <tr key={e.id}><td><b>{e.representative_name}</b></td><td>{e.partner_name}</td>
        <td>¥{Number(e.base_amount).toLocaleString()} × {feeRuleParams(e.params).rate ? `${feeRuleParams(e.params).rate * 100}%` : "—"}</td>
        <td><span className="rule-chip">v{e.rule_version}</span> {e.base}</td><td className="amount-cell">¥{Number(e.calculated_amount).toLocaleString()}</td>
        <td><StateBadge state={e.state}/></td><td><EntitlementActions entitlement={e} t={t} role={role} api={api}/></td></tr>)}</tbody></table>
        {!data.entitlements.length && <div className="empty-state">{t("noEntitlement")}</div>}</div></section>
    {data.disputed_count > 0 && <div className="dispute-note"><CircleAlert size={18}/><div><b>{t("frozen")}</b><span>異議申立てがある報酬は解決まで請求対象から除外されます。</span></div></div>}
    {household && <button className="text-button revenue-detail" onClick={() => onOpen(household)}>{t("show")} · {household.representative_name}<ChevronRight size={14}/></button>}
  </>;
}
function ConstructionCard({ household, project, data, t, role, api }) {
  const [evidence, setEvidence] = useState(project.confirmation_evidence || "");
  const canConfirm = role === "manager" || role === "hq_finance";
  return <section className="panel construction-panel"><div className="panel-head"><div><div className="eyebrow">PROJECT MILESTONE</div><h2>{household.representative_name} · {project.partner_name}</h2></div><StateBadge state={project.confirmed_start_date ? "Confirmed" : "PendingConfirmation"}/></div>
    <div className="milestone-line"><div className="milestone done"><div><Check size={15}/></div><span>{t("contract")}</span><b>{project.contract_date}</b></div><div className="milestone done"><div><Check size={15}/></div><span>{t("startPlanned")}</span><b>{project.planned_start_date}</b></div>
      <div className="milestone done"><div><Check size={15}/></div><span>{t("actualStart")}</span><b>{project.actual_start_date || "—"}</b></div><div className={`milestone ${project.confirmed_start_date ? "done" : "pending"}`}><div>{project.confirmed_start_date ? <Check size={15}/> : "4"}</div><span>{t("confirmStart")}</span><b>{project.confirmed_start_date || "未確認"}</b></div></div>
    {!project.confirmed_start_date && canConfirm ? <div className="confirm-row"><label className="field-label">{t("confirmationEvidence")}<input value={evidence} onChange={(e) => setEvidence(e.target.value)} placeholder="現場写真・担当者確認など"/></label>
      <button className="primary-btn" disabled={!evidence.trim()} onClick={() => api(`/api/construction/${project.project_id}/confirm`, "POST", { confirmed_start_date: new Date().toISOString().slice(0, 10), evidence })}><Check size={15}/>{t("confirm")}</button></div>
      : !project.confirmed_start_date ? <div className="inline-notice"><ShieldCheck size={16}/>{t("roleFinance")} または {t("roleManager")} ロールで着工確認ができます。</div>
      : <div className="success-notice"><Check size={16}/>{t("confirmed")} · {project.confirmation_evidence}</div>}
    {project.entitlement_id && <div className="generated-fee"><div className="metric-icon green"><BadgeJapaneseYen size={18}/></div><div><span>{t("entitlement")} · {t("basis")}</span><b>¥{Number(project.contract_amount).toLocaleString()} × 2% = ¥{Number(project.calculated_amount).toLocaleString()}</b></div><span className="rule-chip">FeeRule v2026.1</span></div>}
  </section>;
}
function StateBadge({ state }) {
  const labels = { Confirmed: "確認済", Invoiced: "請求済", Paid: "入金済", Disputed: "争議中",
    PendingConfirmation: "確認待ち", Estimated: "見積", Potential: "見込", WrittenOff: "償却" };
  return <span className={`state-badge state-${state?.toLowerCase()}`}>{state === "Disputed" && <CircleAlert size={13}/>} {labels[state] || state}</span>;
}
function EntitlementActions({ entitlement, t, role, api }) {
  if (entitlement.state === "Disputed") return <span className="frozen-label"><CircleAlert size={13}/>{t("frozen")}</span>;
  if (role !== "hq_finance") return <span className="muted">—</span>;
  if (entitlement.state === "Confirmed") return <button className="mini-action" onClick={() => api(`/api/entitlements/${entitlement.id}/action`, "POST", { action: "invoice" })}>{t("invoice")} <ChevronRight size={13}/></button>;
  if (entitlement.state === "Invoiced") return <button className="mini-action" onClick={() => api(`/api/entitlements/${entitlement.id}/action`, "POST", { action: "paid" })}>{t("paid")} <ChevronRight size={13}/></button>;
  return <span className="muted">—</span>;
}
function Management({ data, t }) {
  const max = Math.max(...data.stores.slice(0, 7).map((s) => data.households.filter((h) => h.store_id === s.id).length), 1);
  return <><PageTitle eyebrow="BUSINESS INTELLIGENCE" title={t("management")} sub="店舗・流入・着工・報酬を同じ事実データから可視化"/>
    <div className="management-grid"><section className="panel analytics-panel"><div className="panel-head"><div><div className="eyebrow">STORE PERFORMANCE</div><h2>{t("funnel")}</h2></div><span className="filter-btn"><CalendarDays size={15}/>今月<ChevronDown size={13}/></span></div>
      <div className="store-bars">{data.stores.slice(0, 8).map((store) => { const count = data.households.filter((h) => h.store_id === store.id).length;
        return <div className="store-bar-row" key={store.id}><span>{store.name}</span><div className="bar-track"><i style={{ width: `${count / max * 100}%` }}/></div><b>{count}</b></div>;})}</div>
      <div className="chart-footnote">Source: append-only StageEvent · {t("demoWarning")}</div></section>
      <section className="panel analytics-panel"><div className="panel-head"><div><div className="eyebrow">ATTRIBUTION</div><h2>{t("roi")}</h2></div><ArrowUpRight size={17} className="green-text"/></div>
        <div className="channel-list">{["Web広告", "直接来店", "紹介", "自然検索", "TVCM"].map((channel, i) => <div className="channel-row" key={channel}><div className={`channel-dot dot-${i}`}/><span>{channel}</span><b>{data.households.reduce((n, h) => n + h.touches.filter((touch) => touch.channel === channel).length, 0)}</b><small>{i === 0 ? "First touch" : i === 1 ? "Latest touch" : "Touch"}</small></div>)}</div>
        <div className="chart-footnote">First / Latest Touch は Touch 履歴から算出</div></section></div>
    <section className="panel governance-panel"><div className="panel-head"><div><div className="eyebrow">GOVERNANCE</div><h2>{t("audit")}</h2></div><span className="pill pill-green"><ShieldCheck size={13}/>監査対応</span></div>
      <div className="table-scroll"><table><thead><tr><th>日時</th><th>ユーザー</th><th>操作</th><th>対象</th><th>詳細</th></tr></thead><tbody>
        {data.audit_logs.map((row) => <tr key={row.id}><td>{row.at}</td><td>{row.user_name || "—"}</td><td><span className="audit-action">{row.action}</span></td><td>{row.target_type} #{row.target_id}</td><td>{row.detail}</td></tr>)}
      </tbody></table>{!data.audit_logs.length && <div className="empty-state">{t("noRows")}</div>}</div></section>
  </>;
}
function SettingsPage({ data, t, role, locale, onReset }) {
  return <><PageTitle eyebrow="SYSTEM PREFERENCES" title={t("settings")} sub="デモ環境の表示とデータを管理"/>
    <div className="settings-grid"><section className="panel setting-card"><div className="setting-icon"><Users size={19}/></div><div><h2>{t("role")}</h2><p>{t("currentRole")}：{ROLE_LABEL[locale][role]}。{locale === "ja" ? "役割ごとに表示と操作権限が異なります。" : "不同角色拥有不同的数据视图和操作权限。"}</p>
      <div className="setting-roles">{data.roles.map((r) => <span className={`role-chip ${r.id === role ? "current" : ""}`} key={r.id}>{ROLE_LABEL[locale][r.id]} {r.id === role && <Check size={13}/>}</span>)}</div></div></section>
      <section className="panel setting-card"><div className="setting-icon"><Languages size={19}/></div><div><h2>{t("language")}</h2><p>日本語を標準表示とし、中文へ切り替えられます。</p><span className="locale-pill">日本語 · 中文</span></div></section>
      <section className="panel setting-card"><div className="setting-icon"><ShieldCheck size={19}/></div><div><h2>{t("consent")}</h2><p>L1 原始診断データは初期状態で非表示です。共有履歴は対象世帯の詳細画面で確認できます。</p><span className="pill pill-green">L1 PROTECTED</span></div></section>
      <section className="panel setting-card danger-setting"><div className="setting-icon danger"><Settings size={19}/></div><div><h2>{t("reset")}</h2><p>世帯・紹介・着工・報酬を含むデモデータを初期状態に戻します。</p><button className="danger-btn" disabled={role !== "hq_finance"} onClick={onReset}>{t("reset")}</button>{role !== "hq_finance" && <small>本社・経理ロールで実行できます。</small>}</div></section>
    </div></>;
}
function HouseholdModal({ household: h, t, role, onClose, onActivity, api }) {
  const [stage, setStage] = useState(h.stage_events.at(-1)?.to_stage || "新規予約");
  const [disputeIntro, setDisputeIntro] = useState(null);
  const locale = document.documentElement.lang;
  return <Modal onClose={onClose} wide><div className="modal-heading"><div><div className="eyebrow">HOUSEHOLD 360° · #{String(h.id).padStart(4, "0")}</div><h2>{h.representative_name}</h2><p>{h.store_name} · {h.advisor_name} · {h.area_pref}</p></div><button className="icon-btn" onClick={onClose}><X size={18}/></button></div>
    <div className="household-facts"><Fact label={t("budget")} value={h.budget_band}/><Fact label={t("area")} value={h.area_pref}/><Fact label={t("land")} value={h.land_status}/><Fact label={t("stage")} value={h.stage_events.at(-1)?.to_stage}/></div>
    <div className="household-modal-grid"><div className="modal-column"><section className="modal-section"><div className="section-title"><h3>{t("people")}</h3><span className="count-badge">{h.persons.length}</span></div>
      {h.persons.map((p) => <div className="person-row" key={p.id}><div className="customer-avatar">{p.name.slice(0, 1)}</div><div><b>{p.name}</b><span>{p.relation} · {p.phone}</span></div></div>)}</section>
      <section className="modal-section"><div className="section-title"><h3>{t("firstTouch")} / {t("latestTouch")}</h3></div><div className="touch-compare">{[["first", h.first_touch], ["last", h.latest_touch]].map(([key, touch]) => <div className="touch-card" key={key}><small>{t(key)}</small><b>{touch?.channel || "—"}</b><span>{touch?.touch_at || "—"}</span><em>{touch?.capture_method || "—"}</em></div>)}</div></section>
      <section className="modal-section"><div className="section-title"><h3>{t("stages")}</h3><div className="inline-stage"><select value={stage} onChange={(e) => setStage(e.target.value)}>{h.stage_events.length ? h.stage_events.map((e, i) => <option key={`${e.id}-${i}`} value={e.to_stage}>{e.to_stage}</option>) : ["新規予約", "初回相談済", "FP診断済", "紹介済", "訪問・商談中", "契約", "着工", "完了・見送り"].map((s) => <option key={s}>{s}</option>)}</select><button className="mini-action" onClick={() => api(`/api/households/${h.id}/stage`, "POST", { to_stage: stage })}>{t("record")}</button></div></div>
        <div className="timeline">{h.stage_events.map((e) => <div className="timeline-row" key={e.id}><i/><div><b>{e.to_stage}</b><span>{e.changed_at} · {e.changed_by_name || ""}</span></div></div>)}</div></section>
      <section className="modal-section"><div className="section-title"><h3>{t("consent")}</h3></div>{h.consents.map((c) => <div className="consent-row" key={c.id}><ShieldCheck size={15}/><div><b>{c.scope} · {c.purpose}</b><span>同意: {c.granted_at} {c.revoked_at && ` · 取消: ${c.revoked_at}`}</span></div></div>)}
        {h.disclosures.map((d) => <div className="consent-row" key={d.id}><FileText size={15}/><div><b>{d.scope} → {d.disclosed_to}</b><span>共有: {d.disclosed_at}</span></div></div>)}
        <div className="privacy-lock"><ShieldCheck size={15}/>L1 原始診断データは非表示 · 閲覧操作は監査ログに記録されます。</div></section>
    </div><div className="modal-column"><section className="modal-section"><div className="section-title"><h3>{t("negotiations")}</h3><button className="mini-action" onClick={onActivity}><Plus size={13}/>{t("quickActivity")}</button></div>
      {h.introductions.map((intro) => <div className="negotiation-mini" key={intro.id}><div className="partner-icon"><Building2 size={16}/></div><div className="nego-mini-main"><b>{intro.partner_name}</b><span>{intro.staff_name} · {intro.introduced_at}</span><div className="nego-progress">{intro.status} / {intro.negotiation_status || "—"}</div>
        {intro.contract_id && <small>契約 ¥{Number(intro.contract_amount).toLocaleString()} · 着工 {intro.actual_start_date || "未定"} · 確認 {intro.confirmed_start_date || "未確認"}</small>}</div>
        {intro.existing_customer_flag ? <StateBadge state="Disputed"/> : <button className="text-button compact-link" onClick={() => setDisputeIntro(intro.id)}>既存顧客・争議</button>}</div>)}
      {!h.introductions.length && <div className="empty-state">{t("noRows")}</div>}
      {disputeIntro && <DisputeForm introId={disputeIntro} t={t} api={api} onCancel={() => setDisputeIntro(null)}/>}
      </section>
      <section className="modal-section"><div className="section-title"><h3>{t("activitiesHistory")}</h3><button className="mini-action" onClick={onActivity}><Plus size={13}/>{t("addActivity")}</button></div>
        {h.activities.slice(0, 6).map((a) => <div className="activity-row" key={a.id}><div className="activity-dot"><Activity size={13}/></div><div><b>{a.type} · {a.user_name}</b><span>{a.acted_at}</span><p>{a.body}</p>{a.next_action && <small>{t("nextAction")}: {a.next_action} · {a.next_action_due}</small>}</div></div>)}</section>
      <section className="modal-section touch-list"><div className="section-title"><h3>Touch history</h3></div>{h.touches.map((touch) => <div key={touch.id}><span>{touch.touch_at}</span><b>{touch.channel}</b><small>{touch.campaign_id || "—"} · {touch.capture_method}</small></div>)}</section>
    </div></div>
  </Modal>;
}
function DisputeForm({ introId, t, api, onCancel }) {
  const [reason, setReason] = useState("");
  const [level, setLevel] = useState("B");
  return <div className="dispute-form"><label className="field-label">争議理由<input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="住宅会社から既存顧客の申立て"/></label>
    <label className="field-label">証拠レベル<select value={level} onChange={(e) => setLevel(e.target.value)}><option value="A">A 契約 + 原始紹介記録</option><option value="B">B 住宅会社 CRM</option><option value="C">C 予約・来電記録</option><option value="D">D 口頭</option></select></label>
    <div className="form-actions"><button className="secondary-btn" onClick={onCancel}>{t("cancel")}</button><button className="danger-btn" disabled={!reason.trim()} onClick={() => api(`/api/introductions/${introId}/dispute`, "POST", { reason, evidence_level: level })}>{t("disputed")}</button></div></div>;
}
function Fact({ label, value }) { return <div className="fact-card"><span>{label}</span><b>{value || "—"}</b></div>; }
function ActivityModal({ households, t, onClose, onSubmit }) {
  const [householdId, setHouseholdId] = useState(households[0]?.id || "");
  const [type, setType] = useState("面談");
  const [body, setBody] = useState("");
  const [nextAction, setNextAction] = useState("");
  const [due, setDue] = useState("");
  async function submit(e) { e.preventDefault(); await onSubmit({ household_id: Number(householdId), type, body, next_action: nextAction || null, next_action_due: due || null }); onClose(); }
  return <Modal onClose={onClose}><form onSubmit={submit}><div className="modal-heading"><div><div className="eyebrow">ACTIVITY LOG</div><h2>{t("addActivity")}</h2></div><button type="button" className="icon-btn" onClick={onClose}><X size={18}/></button></div>
    <label className="field-label">{t("household")}<select value={householdId} onChange={(e) => setHouseholdId(e.target.value)}>{households.map((h) => <option key={h.id} value={h.id}>{h.representative_name}</option>)}</select></label>
    <label className="field-label">{t("activityType")}<select value={type} onChange={(e) => setType(e.target.value)}>{[["面談","meeting"],["電話","phone"],["LINE","line"],["訪問同行","visit"],["メモ","memo"]].map(([value,key]) => <option key={value} value={value}>{t(key)}</option>)}</select></label>
    <label className="field-label">{t("body")}<textarea required value={body} onChange={(e) => setBody(e.target.value)} rows="3"/></label>
    <label className="field-label">{t("nextAction")}<input value={nextAction} onChange={(e) => setNextAction(e.target.value)}/></label>
    <label className="field-label">{t("nextDue")}<input type="date" value={due} onChange={(e) => setDue(e.target.value)}/></label>
    <div className="form-actions"><button type="button" className="secondary-btn" onClick={onClose}>{t("cancel")}</button><button className="primary-btn"><Check size={15}/>{t("send")}</button></div>
  </form></Modal>;
}
function IntroductionModal({ household, data, t, onClose, onSubmit }) {
  const [partnerId, setPartnerId] = useState(data.partners[0]?.id || "");
  const staff = data.partner_staff.filter((s) => s.partner_id === Number(partnerId));
  const [staffId, setStaffId] = useState("");
  useEffect(() => setStaffId(String(staff[0]?.id || "")), [partnerId]);
  async function submit(e) { e.preventDefault(); await onSubmit({ household_id: household.id, partner_id: Number(partnerId), partner_staff_id: Number(staffId) }); onClose(); }
  return <Modal onClose={onClose}><form onSubmit={submit}><div className="modal-heading"><div><div className="eyebrow">PARTNER INTRODUCTION</div><h2>{t("partnerCreate")}</h2><p>{household.representative_name}</p></div><button type="button" className="icon-btn" onClick={onClose}><X size={18}/></button></div>
    <label className="field-label">{t("partnerSelect")}<select value={partnerId} onChange={(e) => setPartnerId(e.target.value)}>{data.partners.map((p) => <option key={p.id} value={p.id}>{p.name} · {p.area}</option>)}</select></label>
    <label className="field-label">{t("staffSelect")}<select value={staffId} onChange={(e) => setStaffId(e.target.value)}>{staff.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
    <div className="privacy-lock"><ShieldCheck size={15}/>顧客への情報共有は同意された範囲に限定されます。</div>
    <div className="form-actions"><button type="button" className="secondary-btn" onClick={onClose}>{t("cancel")}</button><button className="primary-btn"><Plus size={15}/>{t("add")}</button></div>
  </form></Modal>;
}
function Modal({ children, onClose, wide }) {
  return <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}><div className={`modal ${wide ? "modal-wide" : ""}`}>{children}</div></div>;
}

createRoot(document.getElementById("root")).render(<App/>);
