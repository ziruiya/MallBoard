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
    demoWarning: "デモデータ（仮データ）は全て架空です。", prototype: "非公式プロトタイプ",
    roleAdvisor: "顧問", roleManager: "店長", roleFinance: "本社・経理",
    roleExecutive: "社長", taskQueues: "優先対応", overdueLabel: "期限超過",
    counter_today_followups: "今日フォロー", counter_overdue: "期限超過",
    counter_appointments: "本日来店", counter_unassigned: "担当未割当",
    counter_fee_approval: "報酬承認待ち", counter_invoice_generation: "請求データ生成待ち",
    counter_invoice_unpaid: "請求済・未入金", counter_critical_risk: "重大業務リスク",
    counter_disputes: "紹介帰属争議", counter_construction_queue: "着工確認滞留",
    priorityHigh: "高", daysOverdue: "日超過", noPendingTasks: "未処理の業務はありません。",
    unitItems: "件", reminder_introduction_validity: "紹介有効期間",
    reminder_construction_evidence: "着工証拠提出期限", reminder_dispute_resolution: "争議処理期限",
    reminder_agreement_renewal: "提携契約更新期限", reminder_fee_rule_validity: "FeeRule適用期限",
    trendEntry: "業務トレンドを見る", selectMetric: "指標", period: "期間",
    followupRate: "フォロー実行率", completeness: "データ完全性",
    nextActionRate: "次回アクション設定率", reportRate: "日報提出率",
    responseQuality: "顧客対応品質", sampleSize: "対象数", noScore: "総合点・ランキングは表示しません",
    reminders: "期限リマインダー", storeCompare: "同条件の店舗比較", cohort: "相談月別コホート",
    selectedDeadline: "選択した期限対象", deadlineRecord: "対象レコード",
    partnerQuality: "住宅会社別・報酬処理品質", attribution: "流入経路分析",
    dashboardPrefs: "ホーム画面の表示設定", notificationPrefs: "通知設定",
    inApp: "アプリ内通知", emailNotice: "メール通知", savePreferences: "設定を保存",
    accountingNote: "本番では会計システムから請求・入金状態を受信します。MallBoard は請求書発行・入金消込を行いません。",
    plannedFee: "着工予定報酬", feeReview: "報酬条件確認中", approvedFee: "報酬承認済額",
    invoiceAmount: "請求額", paidAmount: "入金額", confirmedRevenue: "確定売上",
    referenceAmount: "争議中参考金額", frozenAmount: "凍結金額", approve: "承認",
    construction_planned_due: "予定日到来・未確認", construction_planned_due_today: "本日予定・未確認",
    construction_evidence_missing: "証拠未提出", construction_pending_review: "着工済・未審査",
    construction_delayed: "延期", operationsStatus: "店舗運営状況",
    dateLabel: "日付", userLabel: "ユーザー", actionLabel: "操作", targetLabel: "対象", detailLabel: "詳細",
    disputeType_referral: "紹介帰属争議", disputeType_amount: "報酬金額争議",
    disputeType_construction: "着工証拠争議", decisionReason: "裁定理由",
    reassessment: "再調査", writeOff: "報酬を償却", resolveDispute: "争議を裁定",
    stateConfirmed: "確認済", stateInvoiced: "請求データ生成済", statePaid: "入金済",
    stateDisputed: "争議中", statePendingConfirmation: "確認待ち", stateEstimated: "見積",
    statePotential: "見込", stateWrittenOff: "償却", statePending: "承認待ち",
    filterStore: "店舗", filterStage: "ステージを絞り込む", allStores: "全店舗",
    statusActive: "相談中", statusCompleted: "完了", statusLost: "見送り",
    managementSub: "店舗・流入・着工・報酬を同じ事実データから可視化", months: "か月",
    caseVolume: "案件数帯",
    slaPending: "SLA日数はデモ用の暫定値です。正式値は会社確認後に設定してください。",
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
    systemConfig: "運用設定", changeReason: "変更理由（10〜500文字）", saveConfig: "設定を保存",
    configSaved: "設定を保存しました。", configLoadError: "設定を読み込めません。",
    configPermission: "運用設定の変更は本社・経理ロールに限定されています。",
    actionQueue: "対応待ち", actionRequired: "対応が必要", businessTrend: "業務トレンド",
    dailySummary: "日報サマリー", businessOverview: "業務概況", businessIntelligence: "経営分析",
    storeComparison: "店舗比較", storeOperations: "店舗運営", deadlineReminders: "期限リマインダー",
    marketingAttribution: "マーケティング流入分析", cohortConversion: "相談月別転換",
    partnerSettlementQuality: "住宅会社別報酬処理品質", governance: "ガバナンス",
    versionedOperations: "バージョン管理された運用設定", personalWorkspace: "個人ワークスペース",
    touch: "接点", customerRelationship: "顧客関係", partnerJourney: "住宅会社との紹介",
    constructionRevenue: "着工・報酬", constructionConfirmation: "着工確認", revenueLedger: "報酬台帳",
    projectMilestone: "工事マイルストーン", systemPreferences: "システム設定",
    household360: "世帯360°", activityLog: "活動記録", partnerIntroduction: "住宅会社紹介",
    appendOnlyAudit: "追記専用監査", l1Protected: "L1 保護",
    settingsSub: "デモ環境の表示とデータを管理",
    householdsSub: "顧客情報・接点・商談状況を一元管理",
    introductionsSub: "一つの家庭に対する複数住宅会社との並行商談を追跡",
    revenueSub: "予定・実際・確認を分けて記録し、報酬の根拠と状態を追跡",
    roleDescription: "役割ごとに表示と操作権限が異なります。",
    languageDescription: "日本語を標準表示とし、中文へ切り替えられます。",
    consentDescription: "L1 原始診断データは初期状態で非表示です。共有履歴は対象世帯の詳細画面で確認できます。",
    resetDescription: "世帯・紹介・着工・報酬を含むデモデータを初期状態に戻します。",
    financeRoleOnly: "本社・経理ロールで実行できます。",
    workspace: "ワークスペース", demoEnvironment: "デモ環境",
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
    risk: "争议与既有客户", ruleVersions: "报酬规则版本", demoWarning: "演示数据（假数据）全部为虚构。",
    prototype: "非正式原型", roleAdvisor: "顾问", roleManager: "店长", roleFinance: "总部·财务",
    roleExecutive: "社长", taskQueues: "优先处理", overdueLabel: "超期",
    counter_today_followups: "今日跟进", counter_overdue: "超期",
    counter_appointments: "今日到店", counter_unassigned: "未分配负责人",
    counter_fee_approval: "待审批报酬", counter_invoice_generation: "待生成请款数据",
    counter_invoice_unpaid: "已请款·未入金", counter_critical_risk: "重大业务风险",
    counter_disputes: "介绍归属争议", counter_construction_queue: "开工确认滞留",
    priorityHigh: "高", daysOverdue: "天超期", noPendingTasks: "没有待处理事项。",
    unitItems: "项", reminder_introduction_validity: "介绍有效期",
    reminder_construction_evidence: "开工证据提交期限", reminder_dispute_resolution: "争议处理期限",
    reminder_agreement_renewal: "合作协议续约期限", reminder_fee_rule_validity: "FeeRule 适用期限",
    trendEntry: "查看业务趋势", selectMetric: "指标", period: "期间",
    followupRate: "跟进执行率", completeness: "数据完整性",
    nextActionRate: "下次行动设置率", reportRate: "日报提交率",
    responseQuality: "客户响应质量", sampleSize: "样本数", noScore: "不显示总分或排名",
    reminders: "期限提醒", storeCompare: "同条件门店对比", cohort: "咨询月份群组",
    selectedDeadline: "已选提醒事项", deadlineRecord: "业务记录",
    partnerQuality: "按住宅公司查看报酬处理质量", attribution: "来源渠道分析",
    dashboardPrefs: "首页显示设置", notificationPrefs: "通知设置",
    inApp: "应用内通知", emailNotice: "邮件通知", savePreferences: "保存设置",
    accountingNote: "生产版由会计系统回传请款和入金状态。MallBoard 不开发票、不做入金核销。",
    plannedFee: "预计开工报酬", feeReview: "报酬条件确认中", approvedFee: "已审批报酬金额",
    invoiceAmount: "请款金额", paidAmount: "入金金额", confirmedRevenue: "已确认收入",
    referenceAmount: "争议参考金额", frozenAmount: "冻结金额", approve: "审批",
    construction_planned_due: "已到计划日·待确认", construction_planned_due_today: "计划今日·待确认",
    construction_evidence_missing: "未提交证据", construction_pending_review: "已开工·待审核",
    construction_delayed: "延期", operationsStatus: "门店运营情况",
    dateLabel: "日期", userLabel: "用户", actionLabel: "操作", targetLabel: "对象", detailLabel: "详情",
    disputeType_referral: "介绍归属争议", disputeType_amount: "报酬金额争议",
    disputeType_construction: "开工证据争议", decisionReason: "裁决理由",
    reassessment: "重新调查", writeOff: "核销报酬", resolveDispute: "处理争议",
    stateConfirmed: "已确认", stateInvoiced: "请款数据已生成", statePaid: "已入金",
    stateDisputed: "争议中", statePendingConfirmation: "待确认", stateEstimated: "预计",
    statePotential: "潜在", stateWrittenOff: "已核销", statePending: "待审批",
    filterStore: "门店", filterStage: "按阶段筛选", allStores: "全部门店",
    statusActive: "咨询中", statusCompleted: "已完成", statusLost: "已流失",
    managementSub: "基于同一事实数据查看门店、来源、开工与报酬", months: "个月",
    caseVolume: "案件量区间",
    slaPending: "SLA 天数为演示暂定值。正式数值待公司确认后配置。",
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
    systemConfig: "系统运行设置", changeReason: "修改原因（10–500字）", saveConfig: "保存设置",
    configSaved: "设置已保存。", configLoadError: "无法加载设置。",
    configPermission: "系统运行设置仅限总部·财务角色修改。",
    actionQueue: "待处理队列", actionRequired: "需要处理", businessTrend: "业务趋势",
    dailySummary: "日报汇总", businessOverview: "业务概况", businessIntelligence: "经营分析",
    storeComparison: "门店对比", storeOperations: "门店运营", deadlineReminders: "期限提醒",
    marketingAttribution: "营销来源分析", cohortConversion: "咨询月份转化",
    partnerSettlementQuality: "住宅公司报酬处理质量", governance: "治理审计",
    versionedOperations: "版本化运营设置", personalWorkspace: "个人工作区",
    touch: "触点", customerRelationship: "客户关系", partnerJourney: "住宅公司介绍流程",
    constructionRevenue: "开工与报酬", constructionConfirmation: "开工确认", revenueLedger: "报酬台账",
    projectMilestone: "项目节点", systemPreferences: "系统设置",
    household360: "家庭360°", activityLog: "活动记录", partnerIntroduction: "住宅公司介绍",
    appendOnlyAudit: "仅追加审计记录", l1Protected: "L1 已保护",
    settingsSub: "管理演示环境的显示与数据",
    householdsSub: "统一管理客户信息、接点和洽谈状态",
    introductionsSub: "追踪同一家庭与多家住宅公司的并行洽谈",
    revenueSub: "分别记录计划、实际与确认日期，并追踪报酬依据和状态",
    roleDescription: "不同角色拥有不同的数据视图和操作权限。",
    languageDescription: "默认显示日语，并可切换为中文。",
    consentDescription: "L1 原始诊断数据默认隐藏。共享记录可在家庭详情中查看。",
    resetDescription: "将家庭、介绍、开工和报酬等演示数据恢复到初始状态。",
    financeRoleOnly: "请切换到总部·财务角色执行。",
    workspace: "工作区", demoEnvironment: "演示环境",
  },
};

const CONFIG_LABELS = {
  ja: {
    "fee_rule.applicability_basis": "報酬ルール適用基準", "fee.bank_fee_tolerance_yen": "振込手数料許容額",
    "expense.approval_thresholds_yen": "経費承認しきい値", "expense.allowed_categories": "経費カテゴリ",
    "retention.interview_online_years": "面談データのオンライン保存年数",
    "retention.interview_archive_years": "面談データのアーカイブ年数",
    "retention.daily_report_years": "日報保存年数", "retention.monthly_report_years": "月報保存年数",
    "retention.month_close_snapshot_years": "月次締めスナップショット保存年数",
    "retention.audit_years": "監査記録保存年数", "attachment.allowed_extensions": "添付可能な拡張子",
    "attachment.max_file_mb": "添付ファイル上限（MB）", "import.max_csv_rows": "CSV取込上限行数",
    "construction.expected_start_months": "着工予定の標準月数",
    "search.alert_queries_per_minute": "検索アラートしきい値（回/分）",
    "notification.email_retry_minutes": "メール再試行間隔（分）",
    "notification.quiet_hours": "通知の静穏時間", "calendar.retry_minutes": "カレンダー同期再試行間隔（分）",
    "calendar.max_retries": "カレンダー同期の最大再試行数",
    "finance.sync_interval_minutes": "会計連携の同期間隔（分）",
    "finance.summary_stale_after_minutes": "会計サマリーの期限切れ判定（分）",
    "task.followup_sla_days": "フォロー期限（営業日）",
    "task.partner_feedback_sla_days": "住宅会社回答期限（日）",
    "task.construction_evidence_sla_days": "着工証拠提出期限（日）",
    "sla.introduction_validity_days": "紹介有効期間（仮設定・日）",
    "sla.construction_evidence_days": "着工証拠提出期間（仮設定・日）",
    "sla.dispute_resolution_days": "争議処理期間（仮設定・日）",
    "sla.agreement_renewal_days": "提携契約更新期間（仮設定・日）",
    "sla.fee_rule_validity_days": "FeeRule適用期限（仮設定・日）",
    "month_close.lock_working_day": "月次締めロック営業日",
    "expense.max_receipt_mb": "領収書ファイル上限（MB）",
  },
  zh: {
    "fee_rule.applicability_basis": "报酬规则适用依据", "fee.bank_fee_tolerance_yen": "转账手续费容差",
    "expense.approval_thresholds_yen": "费用审批阈值", "expense.allowed_categories": "费用类别",
    "retention.interview_online_years": "面谈数据在线保存年限",
    "retention.interview_archive_years": "面谈数据归档年限",
    "retention.daily_report_years": "日报保存年限", "retention.monthly_report_years": "月报保存年限",
    "retention.month_close_snapshot_years": "月结快照保存年限", "retention.audit_years": "审计记录保存年限",
    "attachment.allowed_extensions": "允许的附件扩展名", "attachment.max_file_mb": "附件大小上限（MB）",
    "import.max_csv_rows": "CSV 导入最大行数", "construction.expected_start_months": "预计开工标准月数",
    "search.alert_queries_per_minute": "搜索告警阈值（次/分）", "notification.email_retry_minutes": "邮件重试间隔（分）",
    "notification.quiet_hours": "通知静默时段", "calendar.retry_minutes": "日历同步重试间隔（分）",
    "calendar.max_retries": "日历同步最大重试次数", "finance.sync_interval_minutes": "会计同步间隔（分）",
    "finance.summary_stale_after_minutes": "会计摘要过期判定（分）", "task.followup_sla_days": "跟进期限（天）",
    "task.partner_feedback_sla_days": "住宅公司反馈期限（天）",
    "task.construction_evidence_sla_days": "开工证据提交期限（天）",
    "sla.introduction_validity_days": "介绍有效期（暂定·天）",
    "sla.construction_evidence_days": "开工证据提交期限（暂定·天）",
    "sla.dispute_resolution_days": "争议处理期限（暂定·天）",
    "sla.agreement_renewal_days": "合作协议续约期限（暂定·天）",
    "sla.fee_rule_validity_days": "FeeRule 适用期限（暂定·天）",
    "month_close.lock_working_day": "月结锁定工作日", "expense.max_receipt_mb": "收据文件大小上限（MB）",
  },
};

const ROLE_LABEL = { ja: { advisor: "顧問", manager: "店長", hq_finance: "本社・経理", executive: "社長" },
  zh: { advisor: "顾问", manager: "店长", hq_finance: "总部·财务", executive: "社长" } };
const NAV = [
  ["dashboard", LayoutDashboard, "today"], ["households", Users, "households"],
  ["introductions", ArrowDownRight, "introductions"], ["revenue", BadgeJapaneseYen, "revenue"],
  ["management", Building2, "management"], ["settings", Settings, "settings"],
];
const STAGES = ["新規予約", "初回相談済", "FP診断済", "紹介済", "訪問・商談中", "契約", "着工", "完了・見送り"];
const API_BASE = import.meta.env.VITE_API_BASE || "";

function App() {
  const [locale, setLocale] = useState(localStorage.getItem("mallboard-locale") || "ja");
  const [role, setRole] = useState(localStorage.getItem("mallboard-role") || "advisor");
  const [page, setPage] = useState("dashboard");
  const [data, setData] = useState(null);
  const [summary, setSummary] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [trend, setTrend] = useState(null);
  const [management, setManagement] = useState(null);
  const [preferences, setPreferences] = useState({ dashboard_widgets: ["tasks", "overview"], notification_preferences: { in_app: true, email: false } });
  const [businessFilter, setBusinessFilter] = useState("");
  const [selected, setSelected] = useState(null);
  const [modal, setModal] = useState("");
  const [query, setQuery] = useState("");
  const [toast, setToast] = useState("");
  const [busy, setBusy] = useState(false);
  const t = (key) => COPY[locale][key] || key;

  async function load() {
    const headers = { "X-Demo-Role": role };
    const [identityResponse, domainResponse, summaryResponse, tasksResponse, preferencesResponse] = await Promise.all([
      fetch(`${API_BASE}/api/bootstrap`, { headers }),
      fetch(`${API_BASE}/api/households`, { headers }),
      fetch(`${API_BASE}/api/dashboard/summary`, { headers }),
      fetch(`${API_BASE}/api/dashboard/my-tasks`, { headers }),
      fetch(`${API_BASE}/api/preferences`, { headers }),
    ]);
    if ([identityResponse, domainResponse, summaryResponse, tasksResponse, preferencesResponse].some((response) => !response.ok)) {
      throw new Error("load failed");
    }
    const [identity, domain, nextSummary, nextTasks, nextPreferences] = await Promise.all([
      identityResponse.json(), domainResponse.json(), summaryResponse.json(), tasksResponse.json(), preferencesResponse.json(),
    ]);
    const result = { ...identity, ...domain };
    setData(result);
    setSummary(nextSummary);
    setTasks(nextTasks.items);
    setPreferences(nextPreferences);
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
    if (page !== "management" || !["manager", "hq_finance", "executive"].includes(role)) return;
    fetch(`${API_BASE}/api/management/overview`, { headers: { "X-Demo-Role": role } })
      .then(async (response) => {
        if (!response.ok) throw new Error("management load failed");
        setManagement(await response.json());
      }).catch(() => setToast("API connection failed"));
  }, [page, role]);
  useEffect(() => {
    if (page !== "dashboard") return;
    fetch(`${API_BASE}/api/dashboard/trends?metric=introductions&period=7d`, { headers: { "X-Demo-Role": role } })
      .then(async (response) => {
        if (response.ok) setTrend(await response.json());
      }).catch(() => {});
  }, [page, role]);
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

  const filtered = useMemo(() => {
    let rows = (data?.households || []).filter((h) =>
      `${h.household_code || ""} ${h.representative_name} ${h.area_pref}`.toLowerCase().includes(query.toLowerCase()));
    if (businessFilter === "unassigned") rows = rows.filter((h) => !h.advisor_id || h.introductions.some((item) => !item.advisor_id));
    if (businessFilter === "validity:due") {
      const limit = new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10);
      rows = rows.filter((h) => h.introductions.some((item) => item.valid_until
        && item.valid_until.toString().slice(0, 10) <= limit));
    }
    if (businessFilter === "disputed") rows = rows.filter((h) => h.introductions.some((item) => item.status === "帰属争議中" || item.entitlement_state === "Disputed"));
    if (businessFilter.startsWith("tasks:") || businessFilter.startsWith("appointments:")) {
      const taskFilter = businessFilter.split(":")[1];
      const relevantIds = new Set(tasks.filter((task) => {
        if (taskFilter === "overdue") return task.days_overdue > 0;
        if (taskFilter === "today_followups") return task.task_type === "followup"
          && task.due_at.toString().slice(0, 10) === new Date().toISOString().slice(0, 10);
        if (taskFilter === "critical") return task.priority === "high" && task.days_overdue > 0;
        return task.task_type === "appointment"
          && task.due_at.toString().slice(0, 10) === new Date().toISOString().slice(0, 10);
      }).filter((task) => task.related_type === "household").map((task) => task.related_id));
      rows = rows.filter((h) => relevantIds.has(h.id));
    }
    return rows;
  }, [data, query, businessFilter, tasks]);
  const openHousehold = (household) => { setSelected(household); setModal("household"); };

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Home size={21}/></div><div><b>MallBoard</b><span>{t("subtitle")}</span></div></div>
      <div className="workspace-label">{t("workspace")}</div>
      <nav>{NAV.map(([id, Icon, key]) => <button key={id} onClick={() => setPage(id)}
        className={`nav-item ${page === id ? "active" : ""}`}><Icon size={18}/><span>{t(key)}</span>
        {id === "households" && summary?.counters.find((item) => item.key === "overdue")?.count > 0 &&
          <em>{summary.counters.find((item) => item.key === "overdue").count}</em>}
      </button>)}</nav>
      <div className="sidebar-spacer"/>
      <div className="role-card"><div className="avatar">{role === "hq_finance" ? "経" : role === "manager" ? "店" : "佐"}</div>
        <div className="role-meta"><b>{data?.user?.name || "Loading…"}</b><span>{ROLE_LABEL[locale][role]}</span></div>
        <ChevronDown size={16} className="muted"/></div>
      <div className="sidebar-foot">{t("demoEnvironment")} <span>●</span></div>
    </aside>
    <main className="main">
      <header className="topbar">
        <div className="breadcrumb"><span>{t("product")}</span><ChevronRight size={14}/><b>{t(NAV.find(([id]) => id === page)?.[2] || page)}</b></div>
        <div className="top-actions">
          <label className="searchbox"><Search size={16}/><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("search")}/><kbd>⌘ K</kbd></label>
          <button className="icon-btn" title={t("notificationPrefs")}><Bell size={18}/></button>
          <div className="select-wrap"><Users size={15}/><select aria-label={t("role")} value={role} onChange={(e) => setRole(e.target.value)}>
            {data.roles.map((option) => <option value={option.id} key={option.id}>{ROLE_LABEL[locale][option.id]}</option>)}
          </select><ChevronDown size={13}/></div>
          <button className="language-btn" onClick={() => setLocale(locale === "ja" ? "zh" : "ja")} title={t("language")}><Languages size={16}/>{locale === "ja" ? "中文" : "日本語"}</button>
        </div>
      </header>
      <div className="page-content">
        {!data ? <div className="loading"><div className="spinner"/>Loading MallBoard…</div> : <>
          {page === "dashboard" && <Dashboard data={data} summary={summary} tasks={tasks} trend={trend} preferences={preferences} t={t} role={role} onHousehold={openHousehold}
            onActivity={() => setModal("activity")} onNavigate={setPage}
            onReport={(body) => api("/api/report", "PUT", { manual_note: body })}
            onCounter={(counter) => { setBusinessFilter(counter.filter); setPage(counter.target_page); }}
            onTask={(task) => {
              const h = data.households.find((item) => item.id === task.household_id);
              if (h) openHousehold(h);
              else { setBusinessFilter(task.task_type === "dispute" ? "disputed" : "construction:pending"); setPage(task.related_type === "introduction" ? "introductions" : "revenue"); }
            }}/>}
          {page === "households" && <Households items={filtered} stores={data.stores} t={t} onOpen={openHousehold}/>}
          {page === "introductions" && <Introductions items={filtered} t={t} onOpen={openHousehold}
            onAdd={(household) => { setSelected(household); setModal("introduction"); }}/>}
          {page === "revenue" && <Revenue data={data} t={t} role={role} api={api} onOpen={openHousehold} filter={businessFilter}/>}
          {page === "management" && <Management data={data} management={management} trend={trend} t={t} role={role}
            onReminder={(item) => { setBusinessFilter(item.filter); setPage(item.target_page); }}/>}
          {page === "settings" && <SettingsPage data={data} t={t} role={role} locale={locale} onReset={async () => {
            if (window.confirm(t("resetConfirm"))) { await api("/api/reset"); setToast(t("resetDone")); }
          }} onConfigSaved={() => { load().catch(() => setToast("API connection failed")); setToast(t("configSaved")); }}
            preferences={preferences} onSavePreferences={(next) => api("/api/preferences", "PUT", next)}/>}
        </>}
      </div>
      <footer className="app-footer"><ShieldCheck size={14}/>{t("prototype")} · {t("demoWarning")}<span>© MallBoard Demo</span></footer>
    </main>
    {modal === "household" && selected && <HouseholdModal household={selected} t={t} role={role}
      onClose={() => setModal("")} onActivity={() => setModal("activity")} api={api}/>}
    {modal === "activity" && <ActivityModal households={data?.households || []} initialHouseholdId={selected?.id} t={t} onClose={() => setModal("")}
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
function Dashboard({ data, summary, tasks, trend, preferences, t, role, onHousehold, onActivity, onNavigate, onReport, onCounter, onTask }) {
  const [note, setNote] = useState(data.daily_report?.manual_note || "");
  const [period, setPeriod] = useState("7d");
  const [metric, setMetric] = useState("introductions");
  const [trendData, setTrendData] = useState(trend);
  const showManagement = role !== "advisor";
  useEffect(() => { setTrendData(trend); }, [trend]);
  useEffect(() => {
    if (!showManagement) return;
    fetch(`${API_BASE}/api/dashboard/trends?metric=${metric}&period=${period}`, { headers: { "X-Demo-Role": role } })
      .then(async (response) => { if (response.ok) setTrendData(await response.json()); });
  }, [metric, period, role, showManagement]);
  const visibleTasks = tasks.slice(0, 5);
  return <><PageTitle eyebrow={new Date().toLocaleDateString("ja-JP", { year: "numeric", month: "long", day: "numeric", weekday: "long" })}
    title={<>{t("todayTitle")}<span>{data.user.name}さん</span></>} sub={t("todaySub")}
    actions={<button className="primary-btn" onClick={onActivity}><Plus size={16}/>{t("quickActivity")}</button>}/>
    <section className="panel queue-panel"><div className="panel-head"><div><div className="eyebrow">{t("actionQueue")}</div><h2>{t("taskQueues")}</h2></div>
      {summary && <span className="muted">{summary.generated_at}</span>}</div>
      <div className="queue-counters">{(summary?.counters || []).slice(0, 3).map((counter) =>
        <button className={`queue-counter ${counter.key === "overdue" || counter.key === "critical_risk" ? "queue-danger" : ""}`}
          key={counter.key} onClick={() => onCounter(counter)}>
          <span>{t(`counter_${counter.key}`) || counter.label}</span><strong>{counter.count}</strong>
          <small>{counter.unit_type === "items" ? t("unitItems") : counter.unit_type}</small><ChevronRight size={15}/>
        </button>)}</div>
    </section>
    <div className="dashboard-grid">
      {preferences.dashboard_widgets.includes("tasks") && <section className="panel tasks-panel"><div className="panel-head"><div><div className="eyebrow">{t("actionRequired")}</div><h2>{t("taskQueues")}</h2></div>
        <span className="pill pill-red">{tasks.length}</span></div>
        {visibleTasks.length ? visibleTasks.map((task) => <div className="task-row" key={task.task_id}>
          <div className={`task-check ${task.days_overdue > 0 ? "text-danger" : ""}`}>
            {task.priority === "high" ? <CircleAlert size={16}/> : <Clock3 size={16}/>}</div>
          <div className="task-copy"><b>{task.title}</b><span>{task.due_at} · {task.days_overdue > 0 ? `${task.days_overdue} ${t("daysOverdue")}` : t("today")}</span></div>
          <button className="icon-btn compact" aria-label={t("open")} onClick={() => onTask(task)}><ChevronRight size={16}/></button>
        </div>) : <div className="empty-mini"><Check size={17}/>{t("noPendingTasks")}</div>}
        <div className="task-bottom"><span><Clock3 size={14}/>{t("overdueLabel")}</span>
          <button className="text-button" onClick={() => onNavigate(role === "hq_finance" ? "revenue" : "households")}>{t("viewAll")} <ChevronRight size={14}/></button></div>
      </section>}
      {showManagement && preferences.dashboard_widgets.includes("trend") ? <section className="panel pipeline-panel"><div className="panel-head"><div><div className="eyebrow">{t("businessTrend")}</div><h2>{t("trendEntry")}</h2></div>
        <button className="text-button" onClick={() => onNavigate("management")}>{t("viewAll")} <ChevronRight size={15}/></button></div>
        <div className="trend-controls"><select value={metric} onChange={(event) => setMetric(event.target.value)}>
          <option value="inquiries">{localeLabel(document.documentElement.lang, "inquiries")}</option>
          <option value="visits">{localeLabel(document.documentElement.lang, "visits")}</option>
          <option value="introductions">{localeLabel(document.documentElement.lang, "introductions")}</option>
          <option value="contracts">{localeLabel(document.documentElement.lang, "contracts")}</option>
          <option value="construction">{localeLabel(document.documentElement.lang, "construction")}</option>
        </select><select value={period} onChange={(event) => setPeriod(event.target.value)}>
          <option value="7d">7d</option><option value="30d">30d</option><option value="90d">90d</option>
        </select></div>
        <div className="trend-summary"><strong>{trendData?.current_total ?? 0}</strong><span>{t("period")}: {period} · {t("introductions")}</span></div>
      </section> : preferences.dashboard_widgets.includes("report") && <section className="panel report-panel"><div className="panel-head"><div><div className="eyebrow">{t("dailySummary")}</div><h2>{t("dailyReport")}</h2></div><FileText size={17} className="muted"/></div>
        <div className="auto-summary"><div className="summary-icon"><Activity size={16}/></div><div><span>{t("autoSummary")}</span><p>{data.daily_report?.auto_summary || "—"}</p></div></div>
        <label className="field-label">{t("note")}<textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="..." rows="3"/></label>
        <button className="secondary-btn full-width" onClick={() => onReport(note)}><Check size={15}/>{t("save")}</button>
      </section>}
    </div>
    {showManagement && preferences.dashboard_widgets.includes("overview") && <section className="panel household-panel">
      <div className="panel-head"><div><div className="eyebrow">{t("businessOverview")}</div><h2>{t("pipeline")}</h2></div>
        <button className="text-button" onClick={() => onNavigate("management")}>{t("viewAll")} <ChevronRight size={15}/></button></div>
      <div className="pipeline-summary"><div><strong>{data.households.length}</strong><span>{t("households")}</span></div>
        <div className="pipeline-divider"/><div><strong>{data.households.reduce((count, item) => count + item.introductions.length, 0)}</strong><span>{t("introductions")}</span></div>
        <div className="pipeline-divider"/><div><strong>{data.entitlements.length}</strong><span>{t("entitlement")}</span></div></div>
      <StageFunnel items={data.households} t={t}/></section>}
  </>;
}
function localeLabel(locale, key) {
  const labels = {
    ja: { inquiries: "問い合わせ数", visits: "来店相談数", introductions: "紹介数", contracts: "契約数", construction: "着工数" },
    zh: { inquiries: "咨询数", visits: "到店咨询数", introductions: "介绍数", contracts: "签约数", construction: "开工数" },
  };
  return labels[locale]?.[key] || key;
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
function Households({ items, stores, t, onOpen }) {
  const [storeId, setStoreId] = useState("all");
  const [stage, setStage] = useState("all");
  const rows = items.filter((household) => (storeId === "all" || household.store_id === Number(storeId))
    && (stage === "all" || household.stage_events.at(-1)?.to_stage === stage));
  return <><PageTitle eyebrow={t("customerRelationship")} title={t("households")} sub={t("householdsSub")}/>
    <section className="panel table-panel"><div className="panel-head"><div><h2>{t("households")} <span className="count-badge">{rows.length}</span></h2></div>
      <div className="table-tools"><label className="filter-select">{t("filterStore")}<select value={storeId} onChange={(event) => setStoreId(event.target.value)}>
        <option value="all">{t("allStores")}</option>{stores.map((store) => <option value={store.id} key={store.id}>{store.name}</option>)}</select></label>
        <label className="filter-select">{t("filterStage")}<select value={stage} onChange={(event) => setStage(event.target.value)}>
          <option value="all">{t("all")}</option>{STAGES.map((value) => <option key={value}>{value}</option>)}</select></label></div></div>
      <HouseholdTable items={rows} t={t} onOpen={onOpen}/></section></>;
}
function Introductions({ items, t, onOpen, onAdd }) {
  const [activeHousehold, setActiveHousehold] = useState(items[0]?.id || null);
  useEffect(() => { if (!items.some((h) => h.id === activeHousehold)) setActiveHousehold(items[0]?.id || null); }, [items, activeHousehold]);
  const household = items.find((h) => h.id === activeHousehold);
  return <><PageTitle eyebrow={t("partnerJourney")} title={t("introductions")} sub={t("introductionsSub")}/>
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
function Revenue({ data, t, role, api, onOpen, filter }) {
  const projectItems = data.households.flatMap((household) => household.introductions
    .filter((intro) => intro.project_id && !intro.confirmed_start_date)
    .map((intro) => ({ household, project: intro })));
  const queue = filter.startsWith("construction:") && filter !== "construction:pending"
    ? projectItems.filter(({ project }) => project.confirmation_status === filter.slice("construction:".length))
    : projectItems;
  const disputes = data.entitlements.filter((item) => item.state === "Disputed");
  const sumState = (states) => data.entitlements.filter((item) => states.includes(item.state))
    .reduce((sum, item) => sum + Number(item.calculated_amount || 0), 0);
  const plannedAmount = projectItems.reduce((sum, item) => sum + Math.round(Number(item.contract_amount || 0) * 0.02), 0);
  const overdueProjects = projectItems.filter(({ project }) => project.confirmation_due_date
    && project.confirmation_due_date.toString().slice(0, 10) < new Date().toISOString().slice(0, 10)).length;
  const freezeAmount = disputes.reduce((sum, item) => sum + Number(item.calculated_amount || 0), 0);
  const referenceAmount = disputes.reduce((sum, item) => sum + Number(item.reference_amount || 0), 0);
  const feeRuleParams = (value) => typeof value === "string" ? JSON.parse(value) : value;
  return <><PageTitle eyebrow={t("constructionRevenue")} title={t("revenue")} sub={t("revenueSub")}/>
    <div className="revenue-metrics"><Metric small label={t("plannedFee")} value={`¥${plannedAmount.toLocaleString()}`} icon={CalendarDays}/>
      <Metric small label={t("feeReview")} value={`¥${sumState(["Pending"]).toLocaleString()}`} icon={Clock3} tone="orange"/>
      <Metric small label={t("approvedFee")} value={`¥${sumState(["Confirmed"]).toLocaleString()}`} icon={BadgeJapaneseYen} tone="green"/>
      <Metric small label={t("invoiceAmount")} value={`¥${sumState(["Invoiced"]).toLocaleString()}`} icon={FileText}/>
      <Metric small label={t("paidAmount")} value={`¥${sumState(["Paid"]).toLocaleString()}`} icon={WalletCards} tone="green"/>
      <Metric small label={t("confirmedRevenue")} value={`¥${sumState(["Confirmed", "Invoiced", "Paid"]).toLocaleString()}`} icon={BadgeJapaneseYen} tone="blue"/></div>
    <section className="panel construction-queue-panel"><div className="panel-head"><div><div className="eyebrow">{t("constructionConfirmation")}</div><h2>{t("confirmStart")} · {queue.length}</h2></div>
      <span className="pill pill-orange">{t("overdueLabel")} {overdueProjects}</span></div>
      <div className="construction-queue">{queue.map(({ household, project }) => <ConstructionCard key={project.project_id}
        household={household} project={project} t={t} role={role} api={api}/>)}
      {!queue.length && <div className="empty-state">{t("noRows")}</div>}</div>
    </section>
    <section className="panel entitlement-panel"><div className="panel-head"><div><div className="eyebrow">{t("revenueLedger")}</div><h2>{t("entitlement")}</h2></div>
      <span className="pill pill-green">{t("appendOnlyAudit")}</span></div>
      <div className="table-scroll"><table><thead><tr><th>{t("household")}</th><th>{t("partner")}</th><th>{t("basis")}</th><th>{t("rule")}</th><th>{t("amount")}</th><th>{t("status")}</th><th/></tr></thead><tbody>
      {data.entitlements.filter((e) => filter !== "disputed" || e.state === "Disputed").filter((e) => !filter.startsWith("entitlements:") || (
        filter === "entitlements:Pending" ? e.state === "Pending" :
          filter === "entitlements:Invoiced" ? e.state === "Invoiced" :
            filter === "entitlements:invoice_data_pending" ? e.state === "Confirmed" && !e.invoice_data_generated : true
      )).map((e) => <tr key={e.id}><td><b>{e.representative_name}</b></td><td>{e.partner_name}</td>
        <td>¥{Number(e.base_amount).toLocaleString()} × {feeRuleParams(e.params).rate ? `${feeRuleParams(e.params).rate * 100}%` : "—"}</td>
        <td><span className="rule-chip">v{e.rule_version}</span> {e.base}</td><td className="amount-cell">¥{Number(e.calculated_amount).toLocaleString()}</td>
        <td><StateBadge state={e.state} t={t}/></td><td><EntitlementActions entitlement={e} t={t} role={role} api={api}/></td></tr>)}</tbody></table>
        {!data.entitlements.length && <div className="empty-state">{t("noEntitlement")}</div>}</div></section>
    <section className="panel dispute-note"><CircleAlert size={18}/><div><b>{t("disputed")} {disputes.length} · {t("frozen")}</b>
      <span>{t("referenceAmount")}: ¥{referenceAmount.toLocaleString()} · {t("frozenAmount")}: ¥{freezeAmount.toLocaleString()} · {t("accountingNote")}</span></div></section>
    {disputes.map((item) => <DisputeResolution key={item.id} item={item} t={t} role={role} api={api}/>)}
  </>;
}
function ConstructionCard({ household, project, data, t, role, api }) {
  const [evidence, setEvidence] = useState(project.confirmation_evidence || "");
  const canConfirm = role === "manager" || role === "hq_finance" || role === "executive";
  const stateLabel = t(`construction_${project.confirmation_status}`);
  return <section className="panel construction-panel"><div className="panel-head"><div><div className="eyebrow">{t("projectMilestone")}</div><h2>{household.representative_name} · {project.partner_name}</h2>
    <small>{stateLabel} · {t("due")}: {project.confirmation_due_date || "—"}</small></div><StateBadge state={project.confirmed_start_date ? "Confirmed" : "PendingConfirmation"} t={t}/></div>
    <div className="milestone-line"><div className="milestone done"><div><Check size={15}/></div><span>{t("contract")}</span><b>{project.contract_date}</b></div><div className="milestone done"><div><Check size={15}/></div><span>{t("startPlanned")}</span><b>{project.planned_start_date}</b></div>
      <div className="milestone done"><div><Check size={15}/></div><span>{t("actualStart")}</span><b>{project.actual_start_date || "—"}</b></div><div className={`milestone ${project.confirmed_start_date ? "done" : "pending"}`}><div>{project.confirmed_start_date ? <Check size={15}/> : "4"}</div><span>{t("confirmStart")}</span><b>{project.confirmed_start_date || "未確認"}</b></div></div>
    {!project.confirmed_start_date && canConfirm ? <div className="confirm-row"><label className="field-label">{t("confirmationEvidence")}<input value={evidence} onChange={(e) => setEvidence(e.target.value)} placeholder="現場写真・担当者確認など"/></label>
      <button className="primary-btn" disabled={!evidence.trim() || !project.actual_start_date} onClick={() => api(`/api/construction/${project.project_id}/confirm`, "POST", { confirmed_start_date: new Date().toISOString().slice(0, 10), evidence })}><Check size={15}/>{t("confirm")}</button></div>
      : !project.confirmed_start_date ? <div className="inline-notice"><ShieldCheck size={16}/>{t("roleFinance")} または {t("roleManager")} ロールで着工確認ができます。</div>
      : <div className="success-notice"><Check size={16}/>{t("confirmed")} · {project.confirmation_evidence}</div>}
    {project.entitlement_id && <div className="generated-fee"><div className="metric-icon green"><BadgeJapaneseYen size={18}/></div><div><span>{t("entitlement")} · {t("basis")}</span><b>¥{Number(project.contract_amount).toLocaleString()} × {feeRate(project.rule_params)} = ¥{Number(project.calculated_amount).toLocaleString()}</b></div><span className="rule-chip">FeeRule v{project.rule_version}</span></div>}
  </section>;
}
function feeRate(params) {
  const parsed = typeof params === "string" ? JSON.parse(params) : params;
  return parsed?.rate ? `${parsed.rate * 100}%` : "—";
}
function DisputeResolution({ item, t, role, api }) {
  const [note, setNote] = useState("");
  const [decision, setDecision] = useState("confirm");
  return <section className="panel dispute-resolution"><div><b>{t(`disputeType_${item.dispute_type}`)} · {item.representative_name}</b>
    <span>{t("evidence")}: {item.evidence_level} · {t("referenceAmount")}: ¥{Number(item.reference_amount).toLocaleString()} · {item.dispute_status}</span></div>
    {role === "hq_finance" ? <div className="dispute-actions"><select value={decision} onChange={(event) => setDecision(event.target.value)}>
      <option value="confirm">{t("approve")}</option><option value="reassessment">{t("reassessment")}</option>
      <option value="write_off">{t("writeOff")}</option></select>
      <input value={note} onChange={(event) => setNote(event.target.value)} placeholder={t("decisionReason")}/>
      <button className="mini-action" disabled={!item.dispute_id || note.trim().length < 5}
        onClick={() => api(`/api/referral-disputes/${item.dispute_id}/decision`, "POST", { decision, decision_note: note })}>{t("resolveDispute")}</button>
    </div> : <StateBadge state="Disputed" t={t}/>}
  </section>;
}
function StateBadge({ state, t }) {
  const keys = { Confirmed: "stateConfirmed", Invoiced: "stateInvoiced", Paid: "statePaid", Disputed: "stateDisputed",
    PendingConfirmation: "statePendingConfirmation", Estimated: "stateEstimated", Potential: "statePotential",
    WrittenOff: "stateWrittenOff", Pending: "statePending" };
  return <span className={`state-badge state-${state?.toLowerCase()}`}>{state === "Disputed" && <CircleAlert size={13}/>} {t ? t(keys[state] || state) : state}</span>;
}
function EntitlementActions({ entitlement, t, role, api }) {
  if (entitlement.state === "Disputed") return <span className="frozen-label"><CircleAlert size={13}/>{t("frozen")}</span>;
  if (role !== "hq_finance") return <span className="muted">—</span>;
  if (entitlement.state === "Pending") return <button className="mini-action" onClick={() => api(`/api/entitlements/${entitlement.id}/action`, "POST", { action: "approve" })}>{t("approve")} <ChevronRight size={13}/></button>;
  if (entitlement.state === "Confirmed") return <button className="mini-action" onClick={() => api(`/api/entitlements/${entitlement.id}/action`, "POST", { action: "invoice" })}>{t("invoice")} <ChevronRight size={13}/></button>;
  if (entitlement.state === "Invoiced") return <button className="mini-action" onClick={() => api(`/api/entitlements/${entitlement.id}/action`, "POST", { action: "paid" })}>{t("paid")} <ChevronRight size={13}/></button>;
  return <span className="muted">—</span>;
}
function Management({ data, management, t, role, onReminder }) {
  const [metric, setMetric] = useState("introductions");
  const [period, setPeriod] = useState("90d");
  const [trendData, setTrendData] = useState(null);
  const [focusedReminder, setFocusedReminder] = useState(null);
  useEffect(() => {
    fetch(`${API_BASE}/api/dashboard/trends?metric=${metric}&period=${period}`, { headers: { "X-Demo-Role": role } })
      .then(async (response) => { if (response.ok) setTrendData(await response.json()); });
  }, [metric, period, role]);
  const stores = management?.stores || [];
  const max = Math.max(...stores.map((item) => item.households || 0), 1);
  const dimensionLabels = [
    ["followup_rate", t("followupRate")], ["data_completeness", t("completeness")],
    ["next_action_rate", t("nextActionRate")], ["report_submission_rate", t("reportRate")],
    ["response_rate", t("responseQuality")],
  ];
  return <><PageTitle eyebrow={t("businessIntelligence")} title={t("management")} sub={t("managementSub")}/>
    <div className="management-grid"><section className="panel analytics-panel"><div className="panel-head"><div><div className="eyebrow">{t("storeComparison")}</div><h2>{t("storeCompare")}</h2></div></div>
      <div className="store-bars">{stores.map((store) => <div className="store-bar-row store-comparison-row" key={store.id}>
        <span>{store.name}</span><div className="bar-track"><i style={{ width: `${store.households / max * 100}%` }}/></div>
        <b>{store.households}</b><small>{store.tenure_months}{t("months")} · {store.case_volume_band} {t("caseVolume")}</small>
      </div>)}</div><div className="chart-footnote">{t("sampleSize")} · {t("households")} · {t("demoWarning")}</div></section>
      <section className="panel analytics-panel"><div className="panel-head"><div><div className="eyebrow">{t("businessTrend")}</div><h2>{t("trendEntry")}</h2></div></div>
        <div className="trend-controls"><select value={metric} onChange={(event) => setMetric(event.target.value)}>
          {["inquiries", "visits", "introductions", "contracts", "construction"].map((key) => <option value={key} key={key}>{localeLabel(document.documentElement.lang, key)}</option>)}
        </select><select value={period} onChange={(event) => setPeriod(event.target.value)}>
          {["7d", "30d", "90d", "180d", "365d"].map((value) => <option key={value}>{value}</option>)}
        </select></div>
        <div className="trend-bars">{(trendData?.current || []).map((point, index) => <div key={`${point.date || point.start}-${index}`}
          title={`${point.date || point.start}: ${point.value}`}><i style={{ height: `${Math.max(3, Math.min(100, point.value * 12))}%` }}/></div>)}</div>
        <div className="trend-summary"><strong>{trendData?.current_total ?? 0}</strong><span>{t("period")} {period} · 前期間 {trendData?.previous_total ?? 0}</span></div>
      </section></div>
    {management?.operations_dimensions?.length > 0 && <section className="panel operations-panel"><div className="panel-head"><div><div className="eyebrow">{t("storeOperations")}</div><h2>{t("operationsStatus")}</h2></div><span className="pill pill-blue">{t("noScore")}</span></div>
      <div className="table-scroll"><table><thead><tr><th>{t("stores")}</th>{dimensionLabels.map(([,label]) => <th key={label}>{label}</th>)}<th>{t("sampleSize")}</th></tr></thead>
        <tbody>{management.operations_dimensions.map((row) => <tr key={row.store_id}><td>{stores.find((store) => store.id === row.store_id)?.name}</td>
          {dimensionLabels.map(([key]) => <td key={key}>{Math.round((row[key] || 0) * 100)}%</td>)}<td>{row.sample_size}</td></tr>)}</tbody></table></div>
    </section>}
    {management && <><section className="panel reminders-panel"><div className="panel-head"><div><div className="eyebrow">{t("deadlineReminders")}</div><h2>{t("reminders")}</h2></div></div>
      <div className="reminder-grid">{management.reminders.map((reminder) => <article className="reminder-card" key={reminder.key}>
        <h3>{t(`reminder_${reminder.key}`)}<span>{reminder.items.length}</span></h3>
        {reminder.items.map((item) => <button key={`${reminder.key}-${item.id}`} onClick={() => {
          setFocusedReminder({ key: reminder.key, item });
          onReminder(reminder, item);
        }}>
          <span>{item.representative_name}</span><small>{item.due_at || "—"}</small><ChevronRight size={14}/></button>)}
        {!reminder.items.length && <p className="muted">{t("noRows")}</p>}
      </article>)}</div>
      {focusedReminder && <div className="inline-notice" aria-live="polite">
        <b>{t("selectedDeadline")} · {t(`reminder_${focusedReminder.key}`)}</b>
        <span>{t("deadlineRecord")}: {focusedReminder.item.representative_name} · {focusedReminder.item.due_at || "—"} · #{focusedReminder.item.id}</span>
      </div>}
    </section>
    <div className="management-grid"><section className="panel analytics-panel"><div className="panel-head"><div><div className="eyebrow">{t("marketingAttribution")}</div><h2>{t("attribution")}</h2></div></div>
      <div className="table-scroll"><table><thead><tr><th>{t("firstTouch")}</th><th>{t("touch")}</th><th>{t("households")}</th><th>{t("contract")}</th></tr></thead>
        <tbody>{management.attribution.map((row) => <tr key={row.channel}><td>{row.channel}</td><td>{row.touches}</td><td>{row.households}</td><td>{row.contracts}</td></tr>)}</tbody></table></div>
    </section><section className="panel analytics-panel"><div className="panel-head"><div><div className="eyebrow">{t("cohortConversion")}</div><h2>{t("cohort")}</h2></div></div>
      <div className="table-scroll"><table><thead><tr><th>{t("cohort")}</th><th>{t("appointments")}</th><th>{t("introductions")}</th><th>{t("contract")}</th></tr></thead>
        <tbody>{management.cohorts.map((row) => <tr key={row.cohort}><td>{row.cohort}</td><td>{row.inquiries}</td><td>{row.introductions} ({row.inquiries ? Math.round(row.introductions / row.inquiries * 100) : 0}%)</td>
          <td>{row.contracts} ({row.inquiries ? Math.round(row.contracts / row.inquiries * 100) : 0}%)</td></tr>)}</tbody></table></div>
    </section></div>
    <section className="panel analytics-panel"><div className="panel-head"><div><div className="eyebrow">{t("partnerSettlementQuality")}</div><h2>{t("partnerQuality")}</h2></div></div>
      <div className="table-scroll"><table><thead><tr><th>{t("partner")}</th><th>{t("introductions")}</th><th>{t("disputed")}</th><th>{t("paid")}</th><th>{t("amount")}</th></tr></thead>
        <tbody>{management.partner_quality.map((row) => <tr key={row.id}><td>{row.name}</td><td>{row.introductions}</td><td>{row.disputes}</td>
          <td>{row.paid}</td><td>¥{Number(row.paid_amount).toLocaleString()}</td></tr>)}</tbody></table></div>
    </section></>}
    <section className="panel governance-panel"><div className="panel-head"><div><div className="eyebrow">{t("governance")}</div><h2>{t("audit")}</h2></div><span className="pill pill-green"><ShieldCheck size={13}/>{t("audit")}</span></div>
      <div className="table-scroll"><table><thead><tr><th>{t("dateLabel")}</th><th>{t("userLabel")}</th><th>{t("actionLabel")}</th><th>{t("targetLabel")}</th><th>{t("detailLabel")}</th></tr></thead><tbody>
        {data.audit_logs.map((row) => <tr key={row.id}><td>{row.at}</td><td>{row.user_name || "—"}</td><td><span className="audit-action">{row.action}</span></td><td>{row.target_type} #{row.target_id}</td><td>{row.detail}</td></tr>)}
      </tbody></table>{!data.audit_logs.length && <div className="empty-state">{t("noRows")}</div>}</div></section>
  </>;
}
function SettingsPage({ data, t, role, locale, onReset, onConfigSaved, preferences, onSavePreferences }) {
  return <><PageTitle eyebrow={t("systemPreferences")} title={t("settings")} sub={t("settingsSub")}/>
    <div className="settings-grid"><section className="panel setting-card"><div className="setting-icon"><Users size={19}/></div><div><h2>{t("role")}</h2><p>{t("currentRole")}：{ROLE_LABEL[locale][role]}。{t("roleDescription")}</p>
      <div className="setting-roles">{data.roles.map((r) => <span className={`role-chip ${r.id === role ? "current" : ""}`} key={r.id}>{ROLE_LABEL[locale][r.id]} {r.id === role && <Check size={13}/>}</span>)}</div></div></section>
      <section className="panel setting-card"><div className="setting-icon"><Languages size={19}/></div><div><h2>{t("language")}</h2><p>{t("languageDescription")}</p><span className="locale-pill">日本語 · 中文</span></div></section>
      <section className="panel setting-card"><div className="setting-icon"><ShieldCheck size={19}/></div><div><h2>{t("consent")}</h2><p>{t("consentDescription")}</p><span className="pill pill-green">{t("l1Protected")}</span></div></section>
      <section className="panel setting-card danger-setting"><div className="setting-icon danger"><Settings size={19}/></div><div><h2>{t("reset")}</h2><p>{t("resetDescription")}</p><button className="danger-btn" disabled={role !== "hq_finance"} onClick={onReset}>{t("reset")}</button>{role !== "hq_finance" && <small>{t("financeRoleOnly")}</small>}</div></section>
    </div>
    <PreferencePanel preferences={preferences} t={t} onSave={onSavePreferences}/>
    <section className="panel config-panel"><div className="panel-head"><div><div className="eyebrow">{t("versionedOperations")}</div><h2>{t("systemConfig")}</h2></div><ShieldCheck size={17} className="green-text"/></div>
      {role === "hq_finance" ? <SystemConfigPanel role={role} locale={locale} t={t} onSaved={onConfigSaved}/> :
        <p className="config-permission">{t("configPermission")}</p>}
      <p className="config-note">{t("slaPending")} {t("accountingNote")}</p>
    </section>
  </>;
}

function PreferencePanel({ preferences, t, onSave }) {
  const [widgets, setWidgets] = useState(preferences.dashboard_widgets);
  const [notifications, setNotifications] = useState(preferences.notification_preferences);
  useEffect(() => { setWidgets(preferences.dashboard_widgets); setNotifications(preferences.notification_preferences); }, [preferences]);
  function toggleWidget(widget) {
    setWidgets((current) => current.includes(widget) ? current.filter((item) => item !== widget)
      : current.length < 4 ? [...current, widget] : current);
  }
  return <section className="panel preference-panel"><div className="panel-head"><div><div className="eyebrow">{t("personalWorkspace")}</div><h2>{t("dashboardPrefs")}</h2></div></div>
    <div className="preference-options">{[["tasks", t("taskQueues")], ["overview", t("pipeline")], ["trend", t("trendEntry")], ["report", t("dailyReport")]].map(([key, label]) =>
      <label key={key}><input type="checkbox" checked={widgets.includes(key)} onChange={() => toggleWidget(key)}/>{label}</label>)}</div>
    <h3>{t("notificationPrefs")}</h3><div className="preference-options">
      {["in_app", "email"].map((key) => <label key={key}><input type="checkbox" checked={Boolean(notifications[key])}
        onChange={(event) => setNotifications((current) => ({ ...current, [key]: event.target.checked }))}/>
        {t(key === "in_app" ? "inApp" : "emailNotice")}</label>)}</div>
    <button className="secondary-btn" onClick={() => onSave({ dashboard_widgets: widgets, notification_preferences: notifications })}>
      <Check size={15}/>{t("savePreferences")}</button>
  </section>;
}

function SystemConfigPanel({ role, locale, t, onSaved }) {
  const [items, setItems] = useState([]);
  const [drafts, setDrafts] = useState({});
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState("");
  useEffect(() => {
    fetch(`${API_BASE}/api/system-config`, { headers: { "X-Demo-Role": role } })
      .then(async (response) => {
        if (!response.ok) throw new Error(t("configLoadError"));
        return response.json();
      })
      .then((result) => {
        setItems(result.items);
        setDrafts(Object.fromEntries(result.items.map((item) => [item.key, JSON.stringify(item.value, null, 2)])));
      })
      .catch((loadError) => setError(loadError.message || t("configLoadError")));
  }, [role, locale]);
  async function save(item) {
    setError("");
    let value;
    try { value = JSON.parse(drafts[item.key]); }
    catch { setError(locale === "ja" ? "JSON形式を確認してください。" : "请检查 JSON 格式。"); return; }
    setSaving(item.key);
    try {
      const response = await fetch(`${API_BASE}/api/system-config/${encodeURIComponent(item.key)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", "X-Demo-Role": role },
        body: JSON.stringify({ value, reason }),
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || t("error"));
      }
      setItems((current) => current.map((entry) => entry.key === item.key
        ? { ...entry, value, updated_at: new Date().toISOString() } : entry));
      setReason("");
      onSaved();
    } catch (saveError) { setError(saveError.message || t("error")); }
    finally { setSaving(""); }
  }
  return <><label className="config-reason"><span>{t("changeReason")}</span>
      <input value={reason} onChange={(event) => setReason(event.target.value)} maxLength={500}/>
    </label>
    {error && <div className="config-error" role="alert">{error}</div>}
    <div className="config-list">{items.map((item) => <div className="config-row" key={item.key}>
      <label><span>{CONFIG_LABELS[locale][item.key]}</span><textarea rows={2} value={drafts[item.key] || ""}
        onChange={(event) => setDrafts((current) => ({ ...current, [item.key]: event.target.value }))}/></label>
      <button className="mini-action" disabled={reason.trim().length < 10 || saving !== ""}
        onClick={() => save(item)}>{saving === item.key ? "…" : t("saveConfig")}</button>
    </div>)}</div>
  </>;
}
function HouseholdModal({ household: h, t, role, onClose, onActivity, api }) {
  const [stage, setStage] = useState(h.stage_events.at(-1)?.to_stage || "新規予約");
  const [disputeIntro, setDisputeIntro] = useState(null);
  const locale = document.documentElement.lang;
  return <Modal onClose={onClose} wide><div className="modal-heading"><div><div className="eyebrow">{t("household360")} · #{String(h.id).padStart(4, "0")}</div><h2>{h.representative_name}</h2><p>{h.store_name} · {h.advisor_name} · {h.area_pref}</p></div><button className="icon-btn" onClick={onClose}><X size={18}/></button></div>
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
        {intro.existing_customer_flag ? <StateBadge state="Disputed" t={t}/> : <button className="text-button compact-link" onClick={() => setDisputeIntro(intro.id)}>既存顧客・争議</button>}</div>)}
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
function ActivityModal({ households, initialHouseholdId, t, onClose, onSubmit }) {
  const [householdId, setHouseholdId] = useState(initialHouseholdId || households[0]?.id || "");
  const [type, setType] = useState("面談");
  const [body, setBody] = useState("");
  const [nextAction, setNextAction] = useState("");
  const [due, setDue] = useState("");
  async function submit(e) { e.preventDefault(); await onSubmit({ household_id: Number(householdId), type, body, next_action: nextAction || null, next_action_due: due || null }); onClose(); }
  return <Modal onClose={onClose}><form onSubmit={submit}><div className="modal-heading"><div><div className="eyebrow">{t("activityLog")}</div><h2>{t("addActivity")}</h2></div><button type="button" className="icon-btn" onClick={onClose}><X size={18}/></button></div>
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
  return <Modal onClose={onClose}><form onSubmit={submit}><div className="modal-heading"><div><div className="eyebrow">{t("partnerIntroduction")}</div><h2>{t("partnerCreate")}</h2><p>{household.representative_name}</p></div><button type="button" className="icon-btn" onClick={onClose}><X size={18}/></button></div>
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
