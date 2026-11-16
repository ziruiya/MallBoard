import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity, ArrowDownRight, ArrowUpRight, BadgeJapaneseYen, Bell, Building2, CalendarDays,
  Check, ChevronDown, ChevronRight, CircleAlert, ClipboardList, Clock3, FileText, Filter,
  Home, Languages, LayoutDashboard, LogOut, Menu, Plus, Search, Settings, ShieldCheck,
  Users, WalletCards, X,
} from "lucide-react";
import "./style.css";
import "./workbench.css";

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
    executive: "社長", notificationPreferences: "通知設定", todoBar: "対応が必要な業務",
    focusTasks: "今日の重点タスク", businessOverview: "経営概況", viewTrend: "業務トレンドを見る",
    openTasks: "未処理", dueOver: "期限超過", noTasks: "対応待ちの業務はありません。",
    dueToday: "本日期限", overdueDays: "超過日数", filterApplied: "適用中フィルター",
    clearFilter: "解除", taskList: "対応が必要な業務", jumpTo: "処理する",
    taskFollowup: "顧客フォロー", taskPartnerFeedback: "住宅会社の回答確認",
    taskConstruction: "着工確認", taskAppointment: "来店予約", taskUnassigned: "担当者未割当",
    taskFeeApproval: "報酬承認", taskInvoiceGeneration: "請求データ生成待ち",
    taskInvoiceUnpaid: "入金確認", taskDispute: "紹介帰属争議",
    constructionQueue: "着工確認キュー", pendingTotal: "確認待ち", overdueOnly: "期限超過",
    plannedOverdue: "予定日到来・未確認", evidenceMissing: "証拠未提出",
    actualUnderReview: "実着工・確認待ち", delayed: "延期",
    plannedFee: "着工予定報酬", approvalPendingAmount: "報酬条件確認中",
    approvedAmount: "報酬承認済額", invoicedAmount: "請求額", paidAmount: "入金額",
    confirmedSales: "確定売上", disputeCases: "争議件数", disputeReference: "争議中参考金額",
    frozenAmount: "凍結金額", noInvoiceGeneration: "MallBoard は請求書を発行しません。請求データ準備の状態のみ管理します。",
    accountingSync: "本番の請求・入金状況は会計システムから連携します。",
    managementSub: "店舗運営、期限リスク、流入、業務トレンドを確認",
    operations: "店舗運営状況", noOverallScore: "指標は個別表示です。総合点・順位付けは行いません。",
    sampleSize: "サンプル数", numerator: "実績", denominator: "対象",
    followupExecution: "フォロー実行率", dataCompleteness: "データ完全性",
    nextActionRate: "次回アクション設定率", reportSubmission: "日報提出率",
    responseQuality: "顧客対応品質サンプル",
    deadlineReminders: "期限リマインダー", dueDate: "期限", expiresIn: "期限まで",
    reminder_introduction_validity: "紹介有効期間", reminder_construction_evidence: "着工証拠提出期限",
    reminder_dispute_resolution: "争議処理期限", reminder_agreement_renewal: "提携契約更新期限",
    reminder_fee_rule_validity: "FeeRule 適用期限",
    storeComparison: "同条件の店舗比較", openMonths: "開設月数", caseVolume: "案件数",
    marketingAttribution: "集客チャネル分析", firstTouchCount: "初回流入",
    latestTouchCount: "最新流入", introducedHomes: "紹介済世帯",
    partnerQuality: "住宅会社別・報酬処理品質", conversionCohort: "コホート転換",
    trend: "業務トレンド", period7: "7日", period30: "30日", period90: "90日",
    period180: "180日", period365: "365日", previousPeriod: "前期間", currentPeriod: "直近期間",
    inquiriesMetric: "問い合わせ数", consultationsMetric: "来店相談数",
    introductionsMetric: "紹介数", contractsMetric: "契約数", constructionMetric: "着工数",
    cohortMonth: "相談月", inquiryHomes: "相談世帯", introRate: "紹介率", contractRate: "契約率",
    partnerIntros: "紹介件数", partnerContracts: "契約件数", partnerPaid: "入金済",
    partnerDisputes: "争議中", preferences: "表示設定", homeWidgets: "ホーム表示項目",
    notificationSettings: "通知設定", demoDataMarker: "デモデータ（仮データ）",
    hideOverdue: "超過タスク", showOverview: "経営概況", showDailyReport: "日報ドラフト",
    showFocusTasks: "重点タスク",
    slaSettings: "期限日数の設定", saveSla: "日数を保存", slaPermission: "期限設定は本社・経理または社長ロールで変更できます。",
    customerList: "世帯一覧", introPipeline: "紹介パイプライン", selectedHousehold: "選択中の世帯",
    approve: "承認",
    unassignedLabel: "担当未割当", advisorSelect: "担当顧問", assign: "担当を割り当てる",
    constructionPermission: "着工確認は店長または本社・経理ロールで実行できます。",
    unconfirmed: "未確認", revenueSub: "着工予定・実際・確認を分け、報酬の根拠と処理状況を追跡します。",
    householdsSub: "顧客情報・接点・商談状況を一元管理します。",
    introductionsSub: "一つの家庭に対する複数住宅会社との並行商談を追跡します。",
    construction: "着工確認", fees: "報酬台帳", disputes: "争議処理",
    trendDelta: "前期間比", enableNotifications: "未処理業務の通知を表示",
    badgeRule: "既読では消えず、業務オブジェクトが処理された時のみ解消します。",
    productionNotes: "運用上の前提", productionRoleNotice: "本番ではデモロールを認証済みユーザーに置き換えます。",
    evidencePlaceholder: "現場写真・担当者確認など", feeGenerated: "計算根拠を台帳に記録",
    remindersNotice: "期限の日数は設定値です。具体的な SLA は会社確認後に確定します。",
    filter_today_followup: "今日のフォロー", filter_overdue_followup: "期限超過",
    filter_appointments_today: "本日来店", filter_store_overdue: "店内期限超過",
    filter_unassigned: "担当未割当", filter_partner_feedback: "住宅会社フィードバック待ち",
    filter_fee_approval: "報酬承認待ち", filter_invoice_generation: "請求データ生成待ち",
    filter_invoice_unpaid: "請求済・未入金", filter_critical_overdue: "重大業務リスク",
    filter_disputed_introductions: "紹介帰属争議", filter_construction_queue: "着工確認滞留",
    metric_units: "件", auditDescription: "監査記録",
    touchHistory: "接点履歴", existingCustomerDispute: "既存顧客・争議", disputeReason: "争議理由",
    disputePlaceholder: "住宅会社から既存顧客の申立て", evidenceLevel: "証拠レベル",
    evidenceA: "契約 + 原始紹介記録", evidenceB: "住宅会社 CRM",
    evidenceC: "予約・来電記録", evidenceD: "口頭",
    consented: "同意", revoked: "取消", shared: "共有",
    privacyNotice: "L1 原始診断データは非表示 · 閲覧操作は監査ログに記録されます。",
    activitySummaryTemplate: "本日の活動 {count} 件。面談・紹介状況を確認してください。",
    activitySummaryEmpty: "本日の活動状況を確認してください。",
    channel: "チャネル", attributionNote: "First / Latest Touch は Touch 履歴から算出",
    timestamp: "日時", userLabel: "ユーザー", actionLabel: "操作", targetLabel: "対象", detailLabel: "詳細",
    settingsSub: "デモ環境の表示とデータを管理",
    languageNotice: "日本語を標準表示とし、中文へ切り替えられます。",
    privacySettingsNotice: "L1 原始診断データは初期状態で非表示です。共有履歴は対象世帯の詳細画面で確認できます。",
    resetNotice: "世帯・紹介・着工・報酬を含むデモデータを初期状態に戻します。",
    resetPermission: "本社・経理ロールで実行できます。",
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
    executive: "社长", notificationPreferences: "通知设置", todoBar: "待处理业务",
    focusTasks: "今日重点任务", businessOverview: "经营概览", viewTrend: "查看业务趋势",
    openTasks: "待处理", dueOver: "已超期", noTasks: "当前没有待处理事项。",
    dueToday: "今日到期", overdueDays: "超期天数", filterApplied: "当前筛选",
    clearFilter: "清除", taskList: "待处理事项", jumpTo: "立即处理",
    taskFollowup: "客户跟进", taskPartnerFeedback: "住宅公司回复确认",
    taskConstruction: "开工确认", taskAppointment: "来店预约", taskUnassigned: "负责人未分配",
    taskFeeApproval: "报酬审批", taskInvoiceGeneration: "请款数据待生成",
    taskInvoiceUnpaid: "确认入金", taskDispute: "介绍归属争议",
    constructionQueue: "开工确认队列", pendingTotal: "待确认", overdueOnly: "已超期",
    plannedOverdue: "计划日到期·待确认", evidenceMissing: "未提交证据",
    actualUnderReview: "已实际开工·待审核", delayed: "延期",
    plannedFee: "计划开工报酬", approvalPendingAmount: "报酬条件确认中",
    approvedAmount: "已审批报酬", invoicedAmount: "已请款金额", paidAmount: "已入金金额",
    confirmedSales: "确定收入", disputeCases: "争议数量", disputeReference: "争议参考金额",
    frozenAmount: "冻结金额", noInvoiceGeneration: "MallBoard 不开发票；这里只跟踪请款数据准备状态。",
    accountingSync: "生产环境的请款与入金状态由会计系统回传。",
    managementSub: "查看门店运营、期限风险、来源与业务趋势",
    operations: "门店运营状况", noOverallScore: "指标分别展示，不计算总分或排名。",
    sampleSize: "样本量", numerator: "已完成", denominator: "目标",
    followupExecution: "跟进执行率", dataCompleteness: "数据完整度",
    nextActionRate: "下次行动设置率", reportSubmission: "日报提交率",
    responseQuality: "客户响应质量样本",
    deadlineReminders: "期限提醒", dueDate: "截止日期", expiresIn: "距截止",
    reminder_introduction_validity: "介绍有效期", reminder_construction_evidence: "开工证据提交期限",
    reminder_dispute_resolution: "争议处理期限", reminder_agreement_renewal: "合作协议续约期限",
    reminder_fee_rule_validity: "FeeRule 适用期限",
    storeComparison: "同条件门店对比", openMonths: "开店月数", caseVolume: "案件量",
    marketingAttribution: "获客渠道分析", firstTouchCount: "首次来源",
    latestTouchCount: "最近来源", introducedHomes: "已介绍家庭",
    partnerQuality: "住宅公司报酬处理质量", conversionCohort: "转化队列",
    trend: "业务趋势", period7: "7天", period30: "30天", period90: "90天",
    period180: "180天", period365: "365天", previousPeriod: "上一周期", currentPeriod: "最近周期",
    inquiriesMetric: "咨询数", consultationsMetric: "来店咨询数",
    introductionsMetric: "介绍数", contractsMetric: "签约数", constructionMetric: "开工数",
    cohortMonth: "咨询月份", inquiryHomes: "咨询家庭", introRate: "介绍率", contractRate: "签约率",
    partnerIntros: "介绍数", partnerContracts: "签约数", partnerPaid: "已入金",
    partnerDisputes: "争议中", preferences: "显示偏好", homeWidgets: "首页显示项",
    notificationSettings: "通知设置", demoDataMarker: "演示数据（虚构）",
    hideOverdue: "超期任务", showOverview: "经营概览", showDailyReport: "日报草稿",
    showFocusTasks: "重点任务",
    slaSettings: "期限天数设置", saveSla: "保存天数", slaPermission: "期限设置仅限总部财务或社长角色修改。",
    customerList: "家庭列表", introPipeline: "介绍管道", selectedHousehold: "当前家庭",
    approve: "审批",
    unassignedLabel: "负责人未分配", advisorSelect: "选择顾问", assign: "分配负责人",
    constructionPermission: "开工确认需由店长或总部财务角色执行。",
    unconfirmed: "未确认", revenueSub: "分别记录计划、实际与确认开工时间，并追踪报酬依据和状态。",
    householdsSub: "统一管理客户信息、接触记录与洽谈状态。",
    introductionsSub: "追踪同一家庭与多家住宅公司的并行洽谈。",
    construction: "开工确认", fees: "报酬台账", disputes: "争议处理",
    trendDelta: "较上一周期", enableNotifications: "显示未处理业务提醒",
    badgeRule: "打开页面不会消除提醒；只有业务对象处理完成后才会消除。",
    productionNotes: "生产环境说明", productionRoleNotice: "生产环境将以已认证用户身份替代演示角色切换。",
    evidencePlaceholder: "现场照片、负责人确认等", feeGenerated: "计算依据已记入台账",
    remindersNotice: "期限天数为配置值；具体 SLA 待公司确认后确定。",
    filter_today_followup: "今日待跟进", filter_overdue_followup: "已超期",
    filter_appointments_today: "今日来店", filter_store_overdue: "门店超期任务",
    filter_unassigned: "负责人未分配", filter_partner_feedback: "待住宅公司反馈",
    filter_fee_approval: "待审批报酬", filter_invoice_generation: "待生成请款数据",
    filter_invoice_unpaid: "已请款未入金", filter_critical_overdue: "重大业务风险",
    filter_disputed_introductions: "介绍归属争议", filter_construction_queue: "待确认开工",
    metric_units: "项", auditDescription: "审计记录",
    touchHistory: "接触记录", existingCustomerDispute: "既有客户／争议", disputeReason: "争议原因",
    disputePlaceholder: "住宅公司提出其为既有客户", evidenceLevel: "证据等级",
    evidenceA: "合同 + 原始介绍记录", evidenceB: "住宅公司 CRM",
    evidenceC: "预约／来电记录", evidenceD: "口头",
    consented: "授权", revoked: "撤销", shared: "共享",
    privacyNotice: "L1 原始诊断数据不可见 · 查看操作会记录在审计日志中。",
    activitySummaryTemplate: "今日活动 {count} 项。请查看面谈与介绍进展。",
    activitySummaryEmpty: "请查看今日活动情况。",
    channel: "渠道", attributionNote: "First / Latest Touch 根据接触记录计算",
    timestamp: "时间", userLabel: "用户", actionLabel: "操作", targetLabel: "对象", detailLabel: "详情",
    settingsSub: "管理演示环境的显示方式和数据",
    languageNotice: "默认显示日语，并可切换为中文。",
    privacySettingsNotice: "L1 原始诊断数据默认不可见。共享记录可在对应家庭的详情页查看。",
    resetNotice: "将家庭、介绍、开工与报酬等演示数据恢复到初始状态。",
    resetPermission: "仅限总部财务角色执行。",
  },
};

const ENUM_LABELS = {
  ja: {
    "新規予約": "新規予約", "初回相談済": "初回相談済", "FP診断済": "FP診断済", "紹介済": "紹介済",
    "訪問・商談中": "訪問・商談中", "契約": "契約", "着工": "着工", "完了・見送り": "完了・見送り",
    "訪問予定": "訪問予定", "訪問済": "訪問済", "見積提示": "見積提示", "商談中": "商談中",
    "受付確認済": "受付確認済", "商談へ移行": "商談へ移行", "見送り": "見送り", "帰属争議中": "帰属争議中",
    "有": "有", "無": "無", "検討中": "検討中", "本人": "本人", "配偶者": "配偶者",
    "Confirmed": "着工確認済", "Invoiced": "請求済", "Paid": "入金済", "Disputed": "争議中",
    "Pending": "承認待ち", "PendingConfirmation": "確認待ち", "Estimated": "見積", "Potential": "見込",
    "WrittenOff": "償却", "面談": "面談", "電話": "電話", "LINE": "LINE", "訪問同行": "訪問同行", "メモ": "メモ",
    "L1": "L1 原始診断", "L2": "L2 診断結果", "L3": "L3 共有用条件",
    "住宅会社への希望条件共有": "住宅会社への希望条件共有",
    "Web広告": "Web広告", "ポスティング": "ポスティング", "紹介": "紹介",
    "自然検索": "自然検索", "直接来店": "直接来店", "TVCM": "TVCM", "UTM": "UTM",
    "QR": "QR", "予約連携": "予約連携", "手入力": "手入力",
    "東京エリア": "東京エリア", "神奈川エリア": "神奈川エリア", "埼玉エリア": "埼玉エリア",
    "千葉エリア": "千葉エリア", "愛知エリア": "愛知エリア", "大阪エリア": "大阪エリア",
    "兵庫エリア": "兵庫エリア", "福岡エリア": "福岡エリア",
  },
  zh: {
    "新規予約": "新预约", "初回相談済": "已完成首次咨询", "FP診断済": "已完成财务诊断", "紹介済": "已介绍",
    "訪問・商談中": "访问／洽谈中", "契約": "已签约", "着工": "已开工", "完了・見送り": "已完成／未继续",
    "訪問予定": "计划访问", "訪問済": "已访问", "見積提示": "已报价", "商談中": "洽谈中",
    "受付確認済": "已确认受理", "商談へ移行": "已转为洽谈", "見送り": "未继续", "帰属争議中": "归属争议中",
    "有": "有", "無": "无", "検討中": "考虑中", "本人": "本人", "配偶者": "配偶",
    "Confirmed": "已确认开工", "Invoiced": "已请款", "Paid": "已入金", "Disputed": "争议中",
    "Pending": "待审批", "PendingConfirmation": "待确认", "Estimated": "预估", "Potential": "潜在",
    "WrittenOff": "已核销", "面談": "面谈", "電話": "电话", "LINE": "LINE", "訪問同行": "陪同访问", "メモ": "备注",
    "L1": "L1 原始诊断", "L2": "L2 诊断结果", "L3": "L3 共享条件",
    "住宅会社への希望条件共有": "向住宅公司共享意向条件",
    "Web広告": "网络广告", "ポスティング": "传单投递", "紹介": "转介绍",
    "自然検索": "自然搜索", "直接来店": "直接到店", "TVCM": "电视广告", "UTM": "UTM",
    "QR": "二维码", "予約連携": "预约联动", "手入力": "手动录入",
    "東京エリア": "东京地区", "神奈川エリア": "神奈川地区", "埼玉エリア": "埼玉地区",
    "千葉エリア": "千叶地区", "愛知エリア": "爱知地区", "大阪エリア": "大阪地区",
    "兵庫エリア": "兵库地区", "福岡エリア": "福冈地区",
  },
};
function displayEnum(value) {
  const locale = document.documentElement.lang === "zh" ? "zh" : "ja";
  return ENUM_LABELS[locale][value] || value || "—";
}

const ROLE_LABEL = { ja: { advisor: "顧問", manager: "店長", hq_finance: "本社・経理" },
  zh: { advisor: "顾问", manager: "店长", hq_finance: "总部·财务", executive: "社长" } };
ROLE_LABEL.ja.executive = "社長";
const NAV = [
  ["dashboard", LayoutDashboard, "today"], ["households", Users, "households"],
  ["introductions", ArrowDownRight, "introductions"], ["revenue", BadgeJapaneseYen, "revenue"],
  ["management", Building2, "management"], ["settings", Settings, "settings"],
];
const API_BASE = import.meta.env.VITE_API_BASE || "";
const DEFAULT_PREFERENCES = { focusTasks: true, overview: true, dailyReport: true, notifications: true };
function readPreferences() {
  try { return { ...DEFAULT_PREFERENCES, ...JSON.parse(localStorage.getItem("mallboard-preferences") || "{}") }; }
  catch { return DEFAULT_PREFERENCES; }
}
function savePreferences(value) { localStorage.setItem("mallboard-preferences", JSON.stringify(value)); }

function App() {
  const [locale, setLocale] = useState(localStorage.getItem("mallboard-locale") || "ja");
  const [role, setRole] = useState(localStorage.getItem("mallboard-role") || "advisor");
  const [page, setPage] = useState("dashboard");
  const [data, setData] = useState(null);
  const [bootstrap, setBootstrap] = useState(null);
  const [summary, setSummary] = useState(null);
  const [taskData, setTaskData] = useState({ tasks: [] });
  const [revenueData, setRevenueData] = useState(null);
  const [managementData, setManagementData] = useState(null);
  const [taskFilter, setTaskFilter] = useState("");
  const [preferences, setPreferences] = useState(readPreferences);
  const [selected, setSelected] = useState(null);
  const [modal, setModal] = useState("");
  const [activityHouseholdId, setActivityHouseholdId] = useState(null);
  const [query, setQuery] = useState("");
  const [toast, setToast] = useState("");
  const [busy, setBusy] = useState(false);
  const t = (key) => COPY[locale][key] || key;

  async function load(filter = taskFilter) {
    const headers = { "X-Demo-Role": role, "X-Demo-Locale": locale };
    const taskPath = `/api/dashboard/my-tasks${filter ? `?filter=${encodeURIComponent(filter)}` : ""}`;
    const paths = ["/api/bootstrap", "/api/households", "/api/dashboard/summary", taskPath, "/api/revenue", "/api/management"];
    const responses = await Promise.all(paths.map((path) => fetch(`${API_BASE}${path}`, { headers })));
    if (responses.some((response) => !response.ok)) throw new Error("API の読み込みに失敗しました。");
    const [identity, workspace, summaryResult, tasksResult, revenueResult, managementResult] =
      await Promise.all(responses.map((response) => response.json()));
    setBootstrap(identity);
    setData(workspace);
    setSummary(summaryResult);
    setTaskData(tasksResult);
    setRevenueData(revenueResult);
    setManagementData(managementResult);
    if (selected) setSelected(workspace.households.find((h) => h.id === selected.id) || null);
  }
  useEffect(() => {
    localStorage.setItem("mallboard-locale", locale);
    document.documentElement.lang = locale;
  }, [locale]);
  useEffect(() => {
    localStorage.setItem("mallboard-role", role);
    load().catch(() => setToast("API connection failed"));
  }, [role, locale, taskFilter]);
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
  const roleOptions = bootstrap?.roles || [{ id: "advisor" }, { id: "manager" }, { id: "hq_finance" }, { id: "executive" }];
  const openHousehold = (household) => { setSelected(household); setModal("household"); };
  const openCounter = (counter) => {
    setTaskFilter(counter.filter);
    setPage(counter.target_page);
  };
  const openTask = (task) => {
    if (!task) return;
    if (task.task_type === "construction_queue") {
      setTaskFilter("construction_queue"); setPage("revenue"); return;
    }
    if (["fee_approval", "invoice_generation", "invoice_unpaid"].includes(task.task_type)) {
      setTaskFilter(task.task_type); setPage("revenue"); return;
    }
    if (task.task_type === "dispute") {
      setTaskFilter("disputed_introductions"); setPage("introductions"); return;
    }
    if (task.task_type === "partner_feedback") {
      setTaskFilter("partner_feedback"); setPage("introductions");
      if (task.household_id) setSelected(data.households.find((h) => h.id === task.household_id) || null);
      return;
    }
    if (task.task_type === "unassigned") {
      setTaskFilter("unassigned"); setPage("introductions"); return;
    }
    if (!task.household_id) return;
    setSelected(data.households.find((h) => h.id === task.household_id) || null);
    setModal("household");
  };

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Home size={21}/></div><div><b>MallBoard</b><span>{t("subtitle")}</span></div></div>
      <div className="workspace-label">WORKSPACE</div>
      <nav>{NAV.map(([id, Icon, key]) => <button key={id} onClick={() => { setTaskFilter(""); setPage(id); }}
        className={`nav-item ${page === id ? "active" : ""}`}><Icon size={18}/><span>{t(key)}</span>
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
          <button className="icon-btn" title={t("notificationPreferences")} onClick={() => setPage("settings")}><Bell size={18}/></button>
          <div className="select-wrap"><Users size={15}/><select aria-label={t("role")} value={role} onChange={(e) => setRole(e.target.value)}>
            {roleOptions.map((option) => <option value={option.id} key={option.id}>{ROLE_LABEL[locale][option.id]}</option>)}
          </select><ChevronDown size={13}/></div>
          <button className="language-btn" onClick={() => setLocale(locale === "ja" ? "zh" : "ja")} title={t("language")}><Languages size={16}/>{locale === "ja" ? "中文" : "日本語"}</button>
        </div>
      </header>
      <div className="page-content">
        {!data ? <div className="loading"><div className="spinner"/>Loading MallBoard…</div> : <>
          {page === "dashboard" && <Dashboard data={data} summary={summary} tasks={taskData.tasks} t={t} locale={locale}
            role={role} preferences={preferences} onHousehold={openHousehold} onTask={openTask} onCounter={openCounter}
            onActivity={() => setModal("activity")} onNavigate={(target) => { setTaskFilter(""); setPage(target); }}
            onReport={(body) => api("/api/report", "PUT", { manual_note: body })}/>}
          {page === "households" && <Households items={filtered} tasks={taskData.tasks} taskFilter={taskFilter}
            t={t} onClearFilter={() => setTaskFilter("")} onOpen={openHousehold}/>}
          {page === "introductions" && <Introductions items={filtered} tasks={taskData.tasks} taskFilter={taskFilter}
            advisors={data.advisors} role={role} api={api} t={t} onClearFilter={() => setTaskFilter("")} onOpen={openHousehold}
            onAdd={(household) => { setSelected(household); setModal("introduction"); }}/>}
          {page === "revenue" && <Revenue data={data} revenue={revenueData} tasks={taskData.tasks}
            taskFilter={taskFilter} t={t} role={role} api={api} onClearFilter={() => setTaskFilter("")} onOpen={openHousehold}/>}
          {page === "management" && <Management data={data} reports={managementData} t={t} locale={locale} role={role}
            onNavigate={(target) => { setTaskFilter(""); setPage(target); }}/>}
          {page === "settings" && <SettingsPage data={data} roles={bootstrap?.roles || []} slaRules={managementData?.sla_rules || {}} t={t} role={role} locale={locale} api={api}
            preferences={preferences} onPreferences={(next) => { setPreferences(next); savePreferences(next); }} onReset={async () => {
            if (window.confirm(t("resetConfirm"))) { await api("/api/reset"); setToast(t("resetDone")); }
          }}/>}
        </>}
      </div>
      <footer className="app-footer"><ShieldCheck size={14}/>{t("prototype")} · {t("demoDataMarker")} · {t("demoWarning")}<span>© MallBoard Demo</span></footer>
    </main>
    {modal === "household" && selected && <HouseholdModal household={selected} t={t} role={role}
      onClose={() => setModal("")} onActivity={() => { setActivityHouseholdId(selected.id); setModal("activity"); }} api={api}/>}
    {modal === "activity" && <ActivityModal households={data?.households || []} initialHouseholdId={activityHouseholdId} t={t} onClose={() => setModal("")}
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
function Dashboard({ data, summary, tasks, t, locale, role, preferences, onHousehold, onTask, onCounter, onActivity, onNavigate, onReport }) {
  const [note, setNote] = useState(data.daily_report?.manual_note || "");
  const reportCount = data.daily_report?.auto_summary?.match(/本日の活動\s+(\d+)\s+件/)?.[1];
  const reportSummary = reportCount !== undefined
    ? t("activitySummaryTemplate").replace("{count}", reportCount)
    : data.daily_report?.auto_summary || t("activitySummaryEmpty");
  return <><PageTitle eyebrow={new Date().toLocaleDateString(locale === "ja" ? "ja-JP" : "zh-CN", { year: "numeric", month: "long", day: "numeric", weekday: "long" })}
    title={<>{t("todayTitle")}<span>{data.user.name}{locale === "ja" ? "さん" : "，您好"}</span></>} sub={t("todaySub")}
    actions={<button className="primary-btn" onClick={onActivity}><Plus size={16}/>{t("quickActivity")}</button>}/>
    <SectionTabs items={[["todoBar","dashboard-todo"],["focusTasks","dashboard-focus"],["businessOverview","dashboard-overview"],
      ...(preferences.dailyReport ? [["dailyReport","dashboard-report"]] : [])]} t={t}/>
    <section className="panel todo-bar" id="dashboard-todo"><div className="panel-head"><div><div className="eyebrow">ACTION QUEUE</div><h2>{t("todoBar")}</h2></div><span className="demo-batch">{t("demoDataMarker")}</span></div>
      <div className="counter-grid">{(summary?.counters || []).slice(0, 3).map((counter, index) =>
        <button key={counter.key} className={`counter-card counter-${index}`} onClick={() => onCounter(counter)}>
          <span>{counter.label}</span><b>{counter.count}<small>{t("metric_units")}</small></b>
          <span className="counter-link">{t("jumpTo")} <ChevronRight size={13}/></span>
        </button>)}</div>
    </section>
    <section className="panel focus-panel" id="dashboard-focus"><div className="panel-head"><div><div className="eyebrow">NEXT BEST ACTION</div><h2>{t("focusTasks")}</h2></div>
      </div>
      {preferences.focusTasks && <TaskList tasks={tasks.slice(0, 6)} t={t} onTask={onTask}/>}
    </section>
    {preferences.overview && <section className="panel overview-panel" id="dashboard-overview">
      <div className="panel-head"><div><div className="eyebrow">BUSINESS CONTEXT</div><h2>{t("businessOverview")}</h2></div>
        <button className="text-button" onClick={() => onNavigate("management")}>{t("viewTrend")} <ChevronRight size={15}/></button></div>
      <div className="overview-links"><button onClick={() => onNavigate("households")}><Users size={17}/><span>{t("recentHouseholds")}</span><ChevronRight size={15}/></button>
        <button onClick={() => onNavigate("introductions")}><Building2 size={17}/><span>{t("pipeline")}</span><ChevronRight size={15}/></button>
        <button onClick={() => onNavigate("revenue")}><BadgeJapaneseYen size={17}/><span>{t("revenue")}</span><ChevronRight size={15}/></button></div>
    </section>}
    {preferences.dailyReport && <section className="panel report-panel" id="dashboard-report"><div className="panel-head"><div><div className="eyebrow">DAILY SUMMARY</div><h2>{t("dailyReport")}</h2></div><FileText size={17} className="muted"/></div>
        <div className="auto-summary"><div className="summary-icon"><Activity size={16}/></div><div><span>{t("autoSummary")}</span><p>{reportSummary}</p></div></div>
        <label className="field-label">{t("note")}<textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="..." rows="3"/></label>
        <button className="secondary-btn full-width" onClick={() => onReport(note)}><Check size={15}/>{t("save")}</button>
      </section>}
  </>;
}
function SectionTabs({ items, t, active, onSelect }) {
  return <div className="section-tabs">{items.map(([key, target]) => <button key={target} onClick={() =>
    onSelect ? onSelect(key) : document.getElementById(target)?.scrollIntoView({ behavior: "smooth", block: "start" })}
    className={active === key ? "selected" : ""}>{t(key)}</button>)}</div>;
}
const TASK_TYPE_KEYS = {
  followup: "taskFollowup", partner_feedback: "taskPartnerFeedback", construction_queue: "taskConstruction",
  appointment: "taskAppointment", unassigned: "taskUnassigned", fee_approval: "taskFeeApproval",
  invoice_generation: "taskInvoiceGeneration", invoice_unpaid: "taskInvoiceUnpaid", dispute: "taskDispute",
};
function TaskList({ tasks, t, onTask }) {
  if (!tasks?.length) return <div className="empty-mini"><Check size={17}/>{t("noTasks")}</div>;
  return <div className="task-list">{tasks.map((task) => <button className="task-list-row" key={task.task_id} onClick={() => onTask(task)}>
    <span className={`task-type-icon ${task.days_overdue > 0 ? "late" : ""}`}>{task.days_overdue > 0 ? <CircleAlert size={16}/> : <ClipboardList size={16}/>}</span>
    <span className="task-list-main"><b>{task.title}</b><small>{task.representative_name || task.household_code || t(TASK_TYPE_KEYS[task.task_type] || "taskList")} · {task.due_at}</small></span>
    {task.days_overdue > 0 ? <span className="overdue-tag">{task.days_overdue}{t("days")}</span> : <span className="task-state">{t("dueToday")}</span>}
    <ChevronRight size={16} className="muted"/>
  </button>)}</div>;
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
      <td><div className="customer-cell"><div className="customer-avatar">{h.representative_name.slice(0, 1)}</div><div><b>{h.representative_name}</b><span>{displayEnum(h.area_pref)}</span></div></div></td>
      <td><span className="stage-tag">{displayEnum(h.stage_events.at(-1)?.to_stage)}</span></td><td>{task?.next_action || "—"}</td><td className={task?.next_action_due < new Date().toISOString().slice(0, 10) ? "text-danger" : ""}>{task?.next_action_due || "—"}</td>
      <td><ChevronRight size={15} className="muted"/></td></tr>;})}</tbody></table>
    {!items.length && <div className="empty-state">{t("noRows")}</div>}</div>;
}
function Households({ items, tasks, taskFilter, t, onClearFilter, onOpen }) {
  const taskHouseholdIds = new Set((tasks || []).map((task) => task.household_id).filter(Boolean));
  const shown = taskFilter ? items.filter((household) => taskHouseholdIds.has(household.id)) : items;
  return <><PageTitle eyebrow="CUSTOMER RELATIONSHIP" title={t("households")} sub={t("householdsSub")}/>
    {taskFilter && <div className="active-filter"><span>{t("filterApplied")}：{t(`filter_${taskFilter}`) || taskFilter}</span><button className="text-button" onClick={onClearFilter}>{t("clearFilter")}</button></div>}
    <SectionTabs items={[["customerList","household-list"],["taskList","household-tasks"]]} t={t}/>
    <section className="panel table-panel" id="household-list"><div className="panel-head"><div><h2>{t("households")} <span className="count-badge">{shown.length}</span></h2></div>
      <div className="table-tools"><button className="filter-btn"><Filter size={15}/>{t("all")}<ChevronDown size={13}/></button></div></div>
      <HouseholdTable items={shown} t={t} onOpen={onOpen}/></section>
    <section className="panel task-section" id="household-tasks"><div className="panel-head"><h2>{t("taskList")}</h2></div>
      <TaskList tasks={tasks} t={t} onTask={(task) => onOpen(items.find((household) => household.id === task.household_id))}/></section></>;
}
function Introductions({ items, tasks, taskFilter, advisors, role, api, t, onClearFilter, onOpen, onAdd }) {
  const taskHouseholdIds = new Set((tasks || []).map((task) => task.household_id).filter(Boolean));
  const shown = taskFilter ? items.filter((household) => taskHouseholdIds.has(household.id)) : items;
  const [activeHousehold, setActiveHousehold] = useState(items[0]?.id || null);
  useEffect(() => { if (!shown.some((h) => h.id === activeHousehold)) setActiveHousehold(shown[0]?.id || null); }, [shown, activeHousehold]);
  const household = shown.find((h) => h.id === activeHousehold);
  return <><PageTitle eyebrow="PARTNER JOURNEY" title={t("introductions")} sub={t("introductionsSub")}/>
    {taskFilter && <div className="active-filter"><span>{t("filterApplied")}：{t(`filter_${taskFilter}`) || taskFilter}</span><button className="text-button" onClick={onClearFilter}>{t("clearFilter")}</button></div>}
    <SectionTabs items={[["introPipeline","intro-pipeline"],["selectedHousehold","intro-selected"]]} t={t}/>
    <div className="intro-layout" id="intro-pipeline"><section className="panel intro-list"><div className="panel-head"><h2>{t("households")}</h2><span className="count-badge">{shown.length}</span></div>
      {shown.map((h) => <button className={`intro-household ${activeHousehold === h.id ? "selected" : ""}`} key={h.id} onClick={() => setActiveHousehold(h.id)}>
        <div className="customer-avatar">{h.representative_name.slice(0, 1)}</div><div><b>{h.representative_name}</b><span>{displayEnum(h.area_pref)}</span></div><span className="intro-count">{h.introductions.length}</span>
      </button>)}</section>
      {household ? <section className="intro-detail" id="intro-selected"><div className="panel intro-context"><div><div className="eyebrow">{household.store_name} · {household.advisor_name || t("unassignedLabel")}</div><h2>{household.representative_name}</h2><span>{household.budget_band} · {displayEnum(household.area_pref)}</span></div>
        {role === "manager" || role === "executive" ? <AssignAdvisorControl object={household} type="household" advisors={advisors} role={role} api={api} t={t}/> : null}
        <button className="secondary-btn" onClick={() => onAdd(household)}><Plus size={15}/>{t("partnerCreate")}</button></div>
        <div className="partner-grid">{household.introductions.map((intro) => <PartnerCard key={intro.id} intro={intro} storeId={household.store_id} t={t} role={role} advisors={advisors} api={api} onOpen={() => onOpen(household)}/>)}
          {!household.introductions.length && <button className="add-partner-card" onClick={() => onAdd(household)}><Plus size={20}/>{t("partnerCreate")}</button>}</div>
      </section> : <section className="panel empty-state">{t("noRows")}</section>}
    </div></>;
}
function AssignAdvisorControl({ object, storeId, type, advisors, role, api, t }) {
  const choices = (advisors || []).filter((advisor) => advisor.store_id === (object.store_id || storeId));
  const [advisorId, setAdvisorId] = useState(String(choices[0]?.id || ""));
  useEffect(() => { setAdvisorId(String(choices[0]?.id || "")); }, [object.id, advisors]);
  if (!choices.length) return null;
  return <div className="assign-control"><select aria-label={t("advisorSelect")} value={advisorId} onChange={(e) => setAdvisorId(e.target.value)}>
    {choices.map((advisor) => <option value={advisor.id} key={advisor.id}>{advisor.name}</option>)}</select>
    <button className="mini-action" disabled={!advisorId} onClick={() => api(`/api/${type === "household" ? "households" : "introductions"}/${object.id}/assign`, "POST", { advisor_id: Number(advisorId) })}>{t("assign")}</button>
  </div>;
}
function PartnerCard({ intro, storeId, t, role, advisors, api, onOpen }) {
  const elapsed = Math.max(0, Math.floor((Date.now() - new Date(intro.introduced_at).getTime()) / 86400000));
  const state = intro.entitlement_state;
  return <article className={`partner-card ${state === "Disputed" ? "disputed-card" : ""}`}>
    <div className="partner-card-head"><div className="partner-icon"><Building2 size={18}/></div><div><b>{intro.partner_name}</b><span>{intro.staff_name || "—"} · {intro.introduced_at}</span></div>
      {intro.existing_customer_flag ? <span className="pill pill-red">{t("disputed")}</span> : <span className="pill pill-blue">{t(intro.status === "受付確認済" ? "received" : "introduced")}</span>}</div>
    <div className="negotiation-status"><div><small>{t("status")}</small><b>{displayEnum(intro.negotiation_status || "紹介済")}</b></div><div><small>{t("elapsed")}</small><b>{elapsed} {t("days")}</b></div><div><small>{t("last")}</small><b>{intro.last_activity_at || "—"}</b></div></div>
    {!intro.advisor_id && (role === "manager" || role === "executive") && <AssignAdvisorControl object={intro} storeId={storeId} type="introduction" advisors={advisors} role={role} api={api} t={t}/>}
    {intro.contract_id && <div className="contract-highlight"><div className="contract-icon"><Check size={15}/></div><div><b>{t("contract")} · ¥{Number(intro.contract_amount).toLocaleString()}</b><span>{intro.contract_date}</span></div></div>}
    {state === "Disputed" && <div className="frozen-banner"><CircleAlert size={15}/>{t("frozen")}</div>}
    <button className="card-link" onClick={onOpen}>{t("review")} <ChevronRight size={14}/></button>
  </article>;
}
function Revenue({ data, revenue, tasks, taskFilter, t, role, api, onClearFilter, onOpen }) {
  const [activeSection, setActiveSection] = useState("construction");
  const projects = revenue?.projects || [];
  const queue = projects.filter((project) => !project.confirmed_start_date);
  const entitlements = revenue?.entitlements || [];
  const disputes = revenue?.disputes || [];
  const financial = revenue?.financial || {};
  const queueCounts = revenue?.queue_counts || {};
  const feeRuleParams = (value) => typeof value === "string" ? JSON.parse(value) : value;
  const sectionLabels = [["constructionQueue", "construction"], ["entitlement", "fees"], ["disputed", "disputes"]];
  const visibleEntitlements = taskFilter === "fee_approval" ? entitlements.filter((fee) => fee.state === "Pending")
    : taskFilter === "invoice_generation" ? entitlements.filter((fee) => fee.state === "Confirmed")
    : taskFilter === "invoice_unpaid" ? entitlements.filter((fee) => fee.state === "Invoiced") : entitlements;
  return <><PageTitle eyebrow="CONSTRUCTION & REVENUE" title={t("revenue")} sub={t("revenueSub")}/>
    {taskFilter && <div className="active-filter"><span>{t("filterApplied")}：{t(`filter_${taskFilter}`) || taskFilter}</span><button className="text-button" onClick={onClearFilter}>{t("clearFilter")}</button></div>}
    <div className="financial-state-grid">{[
      [t("plannedFee"), financial.planned_construction_fee, "planned"], [t("approvalPendingAmount"), financial.pending_approval, "pending"],
      [t("approvedAmount"), financial.approved, "approved"], [t("invoicedAmount"), financial.invoiced, "invoiced"],
      [t("paidAmount"), financial.paid, "paid"], [t("confirmedSales"), financial.confirmed_sales, "sales"],
      [t("disputeCases"), financial.dispute_count, "disputes"], [t("frozenAmount"), financial.frozen_amount, "frozen"],
    ].map(([label, amount, kind]) => <div className={`financial-state ${kind}`} key={kind}><span>{label}</span>
      <b>{kind === "disputes" ? amount || 0 : `¥${Number(amount || 0).toLocaleString()}`}</b></div>)}</div>
    <SectionTabs items={sectionLabels} t={t} active={activeSection} onSelect={setActiveSection}/>
    {activeSection === "construction" && <section className="panel queue-panel" id="construction">
      <div className="panel-head"><div><div className="eyebrow">CONSTRUCTION REVIEW</div><h2>{t("constructionQueue")} · {queue.length}</h2></div>
        <span className="pill pill-orange">{t("overdueOnly")} · {queueCounts.overdue || 0}</span></div>
      <div className="queue-state-grid">{[
        ["planned_due_overdue", t("plannedOverdue")], ["planned_due_today", t("dueToday")],
        ["evidence_missing", t("evidenceMissing")], ["pending_review", t("actualUnderReview")], ["delayed", t("delayed")],
      ].map(([key, label]) => <div className="queue-state" key={key}><span>{label}</span><b>{queueCounts[key] || 0}</b></div>)}</div>
      <div className="construction-list">{queue.map((project) => <ConstructionCard key={project.id} project={project} t={t} role={role} api={api}/>)}
        {!queue.length && <div className="empty-state">{t("noRows")}</div>}</div>
    </section>}
    {activeSection === "fees" && <section className="panel entitlement-panel" id="fees"><div className="panel-head"><div><div className="eyebrow">REVENUE LEDGER</div><h2>{t("entitlement")}</h2></div>
      <span className="pill pill-green">APPEND-ONLY AUDIT</span></div>
      <div className="table-scroll"><table><thead><tr><th>{t("household")}</th><th>{t("partner")}</th><th>{t("basis")}</th><th>{t("rule")}</th><th>{t("amount")}</th><th>{t("status")}</th><th/></tr></thead><tbody>
      {visibleEntitlements.map((e) => <tr key={e.id}><td><b>{e.representative_name}</b></td><td>{e.partner_name}</td>
        <td>¥{Number(e.base_amount).toLocaleString()} × {feeRuleParams(e.params).rate ? `${feeRuleParams(e.params).rate * 100}%` : "—"}</td>
        <td><span className="rule-chip">v{e.rule_version}</span> {e.base}</td><td className="amount-cell">¥{Number(e.calculated_amount).toLocaleString()}</td>
        <td><StateBadge state={e.state}/></td><td><EntitlementActions entitlement={e} t={t} role={role} api={api}/></td></tr>)}</tbody></table>
        {!visibleEntitlements.length && <div className="empty-state">{t("noEntitlement")}</div>}</div></section>}
    {activeSection === "disputes" && <section className="panel entitlement-panel" id="disputes"><div className="panel-head"><div><div className="eyebrow">FROZEN ENTITLEMENTS</div><h2>{t("disputed")} · {disputes.length}</h2></div>
      <span className="pill pill-red">¥{Number(financial.frozen_amount || 0).toLocaleString()} {t("frozenAmount")}</span></div>
      <div className="table-scroll"><table><thead><tr><th>{t("household")}</th><th>{t("partner")}</th><th>{t("status")}</th><th>{t("amount")}</th><th>{t("basis")}</th><th/></tr></thead>
      <tbody>{disputes.map((dispute) => <tr key={dispute.id}><td><b>{dispute.representative_name}</b></td><td>{dispute.partner_name}</td>
        <td>{dispute.reason}</td><td className="amount-cell">¥{Number(dispute.calculated_amount).toLocaleString()}</td><td>{dispute.evidence_level}</td>
        <td><button className="mini-action" onClick={() => onOpen(data.households.find((h) => h.id === dispute.household_id))}>{t("review")} <ChevronRight size={13}/></button></td></tr>)}</tbody></table>
      {!disputes.length && <div className="empty-state">{t("noRows")}</div>}</div>
      <div className="dispute-note"><CircleAlert size={18}/><div><b>{t("frozen")}</b><span>{t("noInvoiceGeneration")}</span></div></div>
    </section>}
    <div className="accounting-note"><ShieldCheck size={15}/><span>{t("noInvoiceGeneration")} {t("accountingSync")}</span></div>
  </>;
}
function ConstructionCard({ project, t, role, api }) {
  const [evidence, setEvidence] = useState(project.confirmation_evidence || "");
  const canConfirm = role === "manager" || role === "hq_finance";
  return <article className={`panel construction-panel ${project.days_overdue > 0 ? "construction-overdue" : ""}`}><div className="panel-head"><div><div className="eyebrow">PROJECT MILESTONE</div><h2>{project.representative_name} · {project.partner_name}</h2></div>
    <div className="construction-status"><StateBadge state={project.confirmed_start_date ? "Confirmed" : "PendingConfirmation"}/>{project.days_overdue > 0 && <span className="overdue-tag">{project.days_overdue}{t("days")}</span>}</div></div>
    <div className="milestone-line"><div className="milestone done"><div><Check size={15}/></div><span>{t("contract")}</span><b>{project.contract_date}</b></div><div className="milestone done"><div><Check size={15}/></div><span>{t("startPlanned")}</span><b>{project.planned_start_date}</b></div>
    <div className="milestone done"><div><Check size={15}/></div><span>{t("actualStart")}</span><b>{project.actual_start_date || "—"}</b></div><div className={`milestone ${project.confirmed_start_date ? "done" : "pending"}`}><div>{project.confirmed_start_date ? <Check size={15}/> : "4"}</div><span>{t("confirmStart")}</span><b>{project.confirmed_start_date || t("unconfirmed")}</b></div></div>
    {!project.confirmed_start_date && canConfirm ? <div className="confirm-row"><label className="field-label">{t("confirmationEvidence")}<input value={evidence} onChange={(e) => setEvidence(e.target.value)} placeholder={t("evidencePlaceholder")}/></label>
      <button className="primary-btn" disabled={!evidence.trim()} onClick={() => api(`/api/construction/${project.id}/confirm`, "POST", { confirmed_start_date: new Date().toISOString().slice(0, 10), evidence })}><Check size={15}/>{t("confirm")}</button></div>
      : !project.confirmed_start_date ? <div className="inline-notice"><ShieldCheck size={16}/>{t("constructionPermission")}</div>
      : <div className="success-notice"><Check size={16}/>{t("confirmed")} · {project.confirmation_evidence}</div>}
    {project.entitlement_id && <div className="generated-fee"><div className="metric-icon green"><BadgeJapaneseYen size={18}/></div><div><span>{t("entitlement")} · {t("basis")}</span><b>¥{Number(project.contract_amount).toLocaleString()} × {t("rule")} = ¥{Number(project.calculated_amount).toLocaleString()}</b></div><span className="rule-chip">{t("feeGenerated")}</span></div>}
  </article>;
}
function StateBadge({ state }) {
  return <span className={`state-badge state-${state?.toLowerCase()}`}>{state === "Disputed" && <CircleAlert size={13}/>} {displayEnum(state)}</span>;
}
function EntitlementActions({ entitlement, t, role, api }) {
  if (entitlement.state === "Disputed") return <span className="frozen-label"><CircleAlert size={13}/>{t("frozen")}</span>;
  if (role !== "hq_finance") return <span className="muted">—</span>;
  if (entitlement.state === "Pending") return <button className="mini-action" onClick={() => api(`/api/entitlements/${entitlement.id}/action`, "POST", { action: "approve" })}>{t("approve")} <ChevronRight size={13}/></button>;
  if (entitlement.state === "Confirmed") return <button className="mini-action" onClick={() => api(`/api/entitlements/${entitlement.id}/action`, "POST", { action: "invoice" })}>{t("invoice")} <ChevronRight size={13}/></button>;
  if (entitlement.state === "Invoiced") return <button className="mini-action" onClick={() => api(`/api/entitlements/${entitlement.id}/action`, "POST", { action: "paid" })}>{t("paid")} <ChevronRight size={13}/></button>;
  return <span className="muted">—</span>;
}
function Management({ data, reports, t, locale, role, onNavigate }) {
  const [metric, setMetric] = useState("inquiries");
  const [period, setPeriod] = useState("90d");
  const [trend, setTrend] = useState(null);
  const [cohort, setCohort] = useState(null);
  const metricLabels = { inquiries: t("inquiriesMetric"), consultations: t("consultationsMetric"),
    introductions: t("introductionsMetric"), contracts: t("contractsMetric"), construction: t("constructionMetric") };
  useEffect(() => {
    let active = true;
    const headers = { "X-Demo-Role": role };
    Promise.all([
      fetch(`${API_BASE}/api/dashboard/trends?metric=${metric}&period=${period}`, { headers }),
      fetch(`${API_BASE}/api/dashboard/trends?metric=cohort&period=365d`, { headers }),
    ]).then(async ([trendResponse, cohortResponse]) => {
      if (!trendResponse.ok || !cohortResponse.ok) throw new Error(t("error"));
      const [trendResult, cohortResult] = await Promise.all([trendResponse.json(), cohortResponse.json()]);
      if (active) { setTrend(trendResult); setCohort(cohortResult); }
    }).catch(() => { if (active) { setTrend(null); setCohort(null); } });
    return () => { active = false; };
  }, [metric, period, role]);
  const reminderTarget = (item) => onNavigate(
    item.related_type === "construction_project" ? "revenue" :
      item.related_type === "introduction" || item.related_type === "dispute" ? "introductions" : "settings",
  );
  const operationRows = [
    ["followupExecution", reports?.operations?.followup_execution],
    ["dataCompleteness", reports?.operations?.data_completeness],
    ["nextActionRate", reports?.operations?.next_action_setting],
    ["reportSubmission", reports?.operations?.daily_report_submission],
    ["responseQuality", reports?.operations?.customer_response_sample],
  ];
  return <><PageTitle eyebrow="BUSINESS INTELLIGENCE" title={t("management")} sub={t("managementSub")}/>
    <SectionTabs items={[["operations","management-operations"],["deadlineReminders","management-reminders"],["storeComparison","management-stores"],
      ["marketingAttribution","management-marketing"],["conversionCohort","management-cohort"],["partnerQuality","management-partners"],["trend","management-trend"]]} t={t}/>
    <section className="panel operations-panel" id="management-operations"><div className="panel-head"><div><div className="eyebrow">STORE OPERATIONS</div><h2>{t("operations")}</h2></div>
      <span className="panel-caption">{t("noOverallScore")}</span></div>
      <div className="operations-grid">{operationRows.map(([label, row]) => <div className="operation-card" key={label}>
        <span>{t(label)}</span><b>{row?.numerator || 0}<small> / {row?.denominator || 0} {t("sampleSize")}</small></b>
        <div className="operation-track"><i style={{ width: `${row?.denominator ? Math.min(100, row.numerator / row.denominator * 100) : 0}%` }}/></div>
      </div>)}</div></section>
    <section className="panel reminder-panel" id="management-reminders"><div className="panel-head"><div><div className="eyebrow">DEADLINE CONTROL</div><h2>{t("deadlineReminders")}</h2></div><span className="panel-caption">{t("remindersNotice")}</span></div>
      <div className="reminder-grid">{(reports?.reminders || []).map((item, index) => <button className={`reminder-card ${item.status === "overdue" ? "reminder-late" : ""}`} key={`${item.key}-${item.related_id}-${index}`} onClick={() => reminderTarget(item)}>
        <span className="reminder-kind">{t(`reminder_${item.key}`) || item.key}</span><b>{item.household_code || item.partner_name || `#${item.related_id}`}</b>
        <small>{t("dueDate")} · {item.due_at} · {item.status === "overdue" ? `${Math.abs(item.days_until_due)}${t("days")} ${t("dueOver")}` : `${item.days_until_due}${t("days")} ${t("expiresIn")}`}</small>
        <span className="reminder-action">{t("review")} <ChevronRight size={13}/></span>
      </button>)}</div>
    </section>
    <section className="panel store-comparison-panel" id="management-stores"><div className="panel-head"><div><div className="eyebrow">COMPARABLE STORE CONTEXT</div><h2>{t("storeComparison")}</h2></div>
      <span className="panel-caption">{locale === "ja" ? "開設月数と案件数を併記し、順位付けはしません。" : "同时显示开店时长和案件量，不进行排名。"}</span></div>
      <div className="table-scroll"><table><thead><tr><th>{t("stores")}</th><th>{t("openMonths")}</th><th>{t("caseVolume")}</th><th>{t("contractsMetric")}</th><th>{t("contractRate")}</th></tr></thead><tbody>
      {(reports?.stores || []).map((store) => <tr key={store.id}><td><b>{store.name}</b></td><td>{store.opened_months}</td><td>{store.household_count}</td><td>{store.contract_count}</td>
        <td>{store.household_count ? `${(store.contract_household_count / store.household_count * 100).toFixed(1)}%` : "—"}</td></tr>)}</tbody></table></div>
    </section>
    <div className="management-grid">
      <section className="panel analytics-panel" id="management-marketing"><div className="panel-head"><div><div className="eyebrow">ATTRIBUTION</div><h2>{t("marketingAttribution")}</h2></div><ArrowUpRight size={17} className="green-text"/></div>
        <div className="table-scroll"><table><thead><tr><th>{t("channel")}</th><th>{t("firstTouchCount")}</th><th>{t("latestTouchCount")}</th><th>{t("introducedHomes")}</th></tr></thead><tbody>
          {(reports?.marketing || []).map((row) => <tr key={row.channel}><td>{displayEnum(row.channel)}</td><td>{row.first_touch}</td><td>{row.latest_touch}</td><td>{row.introduced_households}</td></tr>)}</tbody></table></div>
        <div className="chart-footnote">{t("attributionNote")}</div></section>
      <section className="panel analytics-panel" id="management-partners"><div className="panel-head"><div><div className="eyebrow">PARTNER FEE OPERATIONS</div><h2>{t("partnerQuality")}</h2></div></div>
        <div className="table-scroll"><table><thead><tr><th>{t("partner")}</th><th>{t("partnerIntros")}</th><th>{t("partnerContracts")}</th><th>{t("partnerPaid")}</th><th>{t("partnerDisputes")}</th></tr></thead><tbody>
          {(reports?.partner_quality || []).map((row) => <tr key={row.id}><td>{row.name}</td><td>{row.introductions}</td><td>{row.contracts}</td><td>{row.paid}</td><td>{row.disputed}</td></tr>)}</tbody></table></div></section>
    </div>
    <section className="panel cohort-panel" id="management-cohort"><div className="panel-head"><div><div className="eyebrow">COHORT CONVERSION</div><h2>{t("conversionCohort")}</h2></div><span className="panel-caption">{t("period365")}</span></div>
      <div className="table-scroll"><table><thead><tr><th>{t("cohortMonth")}</th><th>{t("inquiryHomes")}</th><th>{t("introductionsMetric")}</th><th>{t("introRate")}</th><th>{t("contractsMetric")}</th><th>{t("contractRate")}</th></tr></thead><tbody>
        {(cohort?.cohorts || reports?.cohorts || []).map((row) => <tr key={row.cohort}><td>{row.cohort}</td><td>{row.households}</td><td>{row.introductions}</td><td>{row.introduction_rate}%</td><td>{row.contracts}</td><td>{row.contract_rate}%</td></tr>)}</tbody></table>
        {!(cohort?.cohorts || reports?.cohorts || []).length && <div className="empty-state">{t("noRows")}</div>}</div></section>
    <section className="panel trend-panel" id="management-trend"><div className="panel-head"><div><div className="eyebrow">BUSINESS TREND</div><h2>{t("trend")}</h2></div>
      <div className="trend-controls"><select aria-label={t("trend")} value={metric} onChange={(e) => setMetric(e.target.value)}>
        {Object.entries(metricLabels).map(([key, label]) => <option value={key} key={key}>{label}</option>)}</select>
        <select aria-label={t("period90")} value={period} onChange={(e) => setPeriod(e.target.value)}>
          {[["7d","period7"],["30d","period30"],["90d","period90"],["180d","period180"],["365d","period365"]].map(([value,label]) => <option value={value} key={value}>{t(label)}</option>)}</select></div></div>
      <div className="trend-summary"><span>{t("currentPeriod")} <b>{trend?.current_count ?? "—"}</b></span><span>{t("previousPeriod")} <b>{trend?.previous_count ?? "—"}</b></span>
        <span>{t("trendDelta")} <b>{trend?.change > 0 ? "+" : ""}{trend?.change ?? "—"}</b></span></div>
      <div className="trend-chart">{(trend?.points || []).map((point, index) => {
        const maximum = Math.max(1, ...(trend?.points || []).map((p) => p.count));
        return <div className={`trend-point ${point.series}`} key={`${point.series}-${point.label}-${index}`} title={`${point.label}: ${point.count}`}>
          <div className="trend-bar-wrap"><i style={{ height: `${Math.max(3, point.count / maximum * 100)}%` }}/></div><small>{point.label}</small></div>;
      })}</div>
    </section>
    <section className="panel governance-panel"><div className="panel-head"><div><div className="eyebrow">GOVERNANCE</div><h2>{t("audit")}</h2></div><span className="pill pill-green"><ShieldCheck size={13}/>{t("auditDescription")}</span></div>
      <div className="table-scroll"><table><thead><tr><th>{t("timestamp")}</th><th>{t("userLabel")}</th><th>{t("actionLabel")}</th><th>{t("targetLabel")}</th><th>{t("detailLabel")}</th></tr></thead><tbody>
        {data.audit_logs.map((row) => <tr key={row.id}><td>{row.at}</td><td>{row.user_name || "—"}</td><td><span className="audit-action">{row.action}</span></td><td>{row.target_type} #{row.target_id}</td><td>{row.detail}</td></tr>)}
      </tbody></table>{!data.audit_logs.length && <div className="empty-state">{t("noRows")}</div>}</div></section>
  </>;
}
function SettingsPage({ data, roles, slaRules, t, role, locale, preferences, onPreferences, api, onReset }) {
  const updatePreference = (key, value) => onPreferences({ ...preferences, [key]: value });
  return <><PageTitle eyebrow="SYSTEM PREFERENCES" title={t("settings")} sub={t("settingsSub")}/>
    <SectionTabs items={[["preferences","settings-preferences"],["notificationSettings","settings-notifications"],["slaSettings","settings-sla"],["reset","settings-reset"]]} t={t}/>
    <div className="settings-grid"><section className="panel setting-card"><div className="setting-icon"><Users size={19}/></div><div><h2>{t("role")}</h2><p>{t("currentRole")}：{ROLE_LABEL[locale][role]}。{locale === "ja" ? "役割ごとに表示と操作権限が異なります。" : "不同角色拥有不同的数据视图和操作权限。"}</p>
      <div className="setting-roles">{roles.map((r) => <span className={`role-chip ${r.id === role ? "current" : ""}`} key={r.id}>{ROLE_LABEL[locale][r.id]} {r.id === role && <Check size={13}/>}</span>)}</div></div></section>
      <section className="panel setting-card"><div className="setting-icon"><Languages size={19}/></div><div><h2>{t("language")}</h2><p>{t("languageNotice")}</p><span className="locale-pill">日本語 · 中文</span></div></section>
      <section className="panel setting-card"><div className="setting-icon"><ShieldCheck size={19}/></div><div><h2>{t("consent")}</h2><p>{t("privacySettingsNotice")}</p><span className="pill pill-green">L1 PROTECTED</span></div></section>
      <section className="panel setting-card preference-card" id="settings-preferences"><div className="setting-icon"><LayoutDashboard size={19}/></div><div><h2>{t("homeWidgets")}</h2>
        {[["focusTasks","showFocusTasks"],["overview","showOverview"],["dailyReport","showDailyReport"]].map(([key,label]) => <label className="preference-toggle" key={key}><input type="checkbox" checked={Boolean(preferences[key])} onChange={(e) => updatePreference(key,e.target.checked)}/>{t(label)}</label>)}</div></section>
      <section className="panel setting-card preference-card" id="settings-notifications"><div className="setting-icon"><Bell size={19}/></div><div><h2>{t("notificationSettings")}</h2>
        <label className="preference-toggle"><input type="checkbox" checked={Boolean(preferences.notifications)} onChange={(e) => updatePreference("notifications",e.target.checked)}/>{t("enableNotifications")}</label>
        <p>{t("badgeRule")}</p></div></section>
      <section className="panel setting-card production-note"><div className="setting-icon"><ShieldCheck size={19}/></div><div><h2>{t("productionNotes")}</h2><p>{t("noInvoiceGeneration")} {t("accountingSync")}</p><p>{t("productionRoleNotice")}</p></div></section>
      <section className="panel setting-card sla-setting-card" id="settings-sla"><div className="setting-icon"><Clock3 size={19}/></div><div><h2>{t("slaSettings")}</h2>
        <p>{t("remindersNotice")}</p><div className="sla-controls">{Object.entries(slaRules).map(([key, days]) => <SLASetting key={key} settingKey={key} days={days} t={t} role={role} api={api}/>)}</div>
        {role !== "hq_finance" && role !== "executive" && <small>{t("slaPermission")}</small>}</div></section>
      <section className="panel setting-card danger-setting" id="settings-reset"><div className="setting-icon danger"><Settings size={19}/></div><div><h2>{t("reset")}</h2><p>{t("resetNotice")}</p><button className="danger-btn" disabled={role !== "hq_finance"} onClick={onReset}>{t("reset")}</button>{role !== "hq_finance" && <small>{t("resetPermission")}</small>}</div></section>
    </div></>;
}
function SLASetting({ settingKey, days, t, role, api }) {
  const [value, setValue] = useState(days);
  useEffect(() => setValue(days), [days]);
  return <div className="sla-setting-row"><label>{t(`reminder_${settingKey}`) || settingKey}<input type="number" min="0" max="365" value={value}
    disabled={role !== "hq_finance" && role !== "executive"} onChange={(e) => setValue(Number(e.target.value))}/></label>
    <button className="mini-action" disabled={role !== "hq_finance" && role !== "executive"} onClick={() => api(`/api/settings/sla/${settingKey}`, "PUT", { days_before: value })}>{t("saveSla")}</button>
  </div>;
}
function HouseholdModal({ household: h, t, role, onClose, onActivity, api }) {
  const [stage, setStage] = useState(h.stage_events.at(-1)?.to_stage || "新規予約");
  const [disputeIntro, setDisputeIntro] = useState(null);
  return <Modal onClose={onClose} wide><div className="modal-heading"><div><div className="eyebrow">HOUSEHOLD 360° · #{String(h.id).padStart(4, "0")}</div><h2>{h.representative_name}</h2><p>{h.store_name} · {h.advisor_name} · {displayEnum(h.area_pref)}</p></div><button className="icon-btn" onClick={onClose}><X size={18}/></button></div>
    <div className="household-facts"><Fact label={t("budget")} value={h.budget_band}/><Fact label={t("area")} value={displayEnum(h.area_pref)}/><Fact label={t("land")} value={displayEnum(h.land_status)}/><Fact label={t("stage")} value={displayEnum(h.stage_events.at(-1)?.to_stage)}/></div>
    <div className="household-modal-grid"><div className="modal-column"><section className="modal-section"><div className="section-title"><h3>{t("people")}</h3><span className="count-badge">{h.persons.length}</span></div>
      {h.persons.map((p) => <div className="person-row" key={p.id}><div className="customer-avatar">{p.name.slice(0, 1)}</div><div><b>{p.name}</b><span>{displayEnum(p.relation)} · {p.phone}</span></div></div>)}</section>
      <section className="modal-section"><div className="section-title"><h3>{t("firstTouch")} / {t("latestTouch")}</h3></div><div className="touch-compare">{[["first", h.first_touch], ["last", h.latest_touch]].map(([key, touch]) => <div className="touch-card" key={key}><small>{t(key)}</small><b>{touch?.channel || "—"}</b><span>{touch?.touch_at || "—"}</span><em>{touch?.capture_method || "—"}</em></div>)}</div></section>
      <section className="modal-section"><div className="section-title"><h3>{t("stages")}</h3><div className="inline-stage"><select value={stage} onChange={(e) => setStage(e.target.value)}>{h.stage_events.length ? h.stage_events.map((e, i) => <option key={`${e.id}-${i}`} value={e.to_stage}>{displayEnum(e.to_stage)}</option>) : ["新規予約", "初回相談済", "FP診断済", "紹介済", "訪問・商談中", "契約", "着工", "完了・見送り"].map((s) => <option key={s} value={s}>{displayEnum(s)}</option>)}</select><button className="mini-action" onClick={() => api(`/api/households/${h.id}/stage`, "POST", { to_stage: stage })}>{t("record")}</button></div></div>
        <div className="timeline">{h.stage_events.map((e) => <div className="timeline-row" key={e.id}><i/><div><b>{displayEnum(e.to_stage)}</b><span>{e.changed_at} · {e.changed_by_name || ""}</span></div></div>)}</div></section>
      <section className="modal-section"><div className="section-title"><h3>{t("consent")}</h3></div>{h.consents.map((c) => <div className="consent-row" key={c.id}><ShieldCheck size={15}/><div><b>{displayEnum(c.scope)} · {displayEnum(c.purpose)}</b><span>{t("consented")}: {c.granted_at} {c.revoked_at && ` · ${t("revoked")}: ${c.revoked_at}`}</span></div></div>)}
        {h.disclosures.map((d) => <div className="consent-row" key={d.id}><FileText size={15}/><div><b>{displayEnum(d.scope)} → {d.disclosed_to}</b><span>{t("shared")}: {d.disclosed_at}</span></div></div>)}
        <div className="privacy-lock"><ShieldCheck size={15}/>{t("privacyNotice")}</div></section>
    </div><div className="modal-column"><section className="modal-section"><div className="section-title"><h3>{t("negotiations")}</h3><button className="mini-action" onClick={onActivity}><Plus size={13}/>{t("quickActivity")}</button></div>
      {h.introductions.map((intro) => <div className="negotiation-mini" key={intro.id}><div className="partner-icon"><Building2 size={16}/></div><div className="nego-mini-main"><b>{intro.partner_name}</b><span>{intro.staff_name} · {intro.introduced_at}</span><div className="nego-progress">{displayEnum(intro.status)} / {displayEnum(intro.negotiation_status)}</div>
        {intro.contract_id && <small>{t("contract")} ¥{Number(intro.contract_amount).toLocaleString()} · {t("actualStart")} {intro.actual_start_date || "—"} · {t("confirmStart")} {intro.confirmed_start_date || t("unconfirmed")}</small>}</div>
        {intro.existing_customer_flag ? <StateBadge state="Disputed"/> : <button className="text-button compact-link" onClick={() => setDisputeIntro(intro.id)}>{t("existingCustomerDispute")}</button>}</div>)}
      {!h.introductions.length && <div className="empty-state">{t("noRows")}</div>}
      {disputeIntro && <DisputeForm introId={disputeIntro} t={t} api={api} onCancel={() => setDisputeIntro(null)}/>}
      </section>
      <section className="modal-section"><div className="section-title"><h3>{t("activitiesHistory")}</h3><button className="mini-action" onClick={onActivity}><Plus size={13}/>{t("addActivity")}</button></div>
        {h.activities.slice(0, 6).map((a) => <div className="activity-row" key={a.id}><div className="activity-dot"><Activity size={13}/></div><div><b>{displayEnum(a.type)} · {a.user_name}</b><span>{a.acted_at}</span><p>{a.body}</p>{a.next_action && <small>{t("nextAction")}: {a.next_action} · {a.next_action_due}</small>}</div></div>)}</section>
      <section className="modal-section touch-list"><div className="section-title"><h3>{t("touchHistory")}</h3></div>{h.touches.map((touch) => <div key={touch.id}><span>{touch.touch_at}</span><b>{displayEnum(touch.channel)}</b><small>{touch.campaign_id || "—"} · {displayEnum(touch.capture_method)}</small></div>)}</section>
    </div></div>
  </Modal>;
}
function DisputeForm({ introId, t, api, onCancel }) {
  const [reason, setReason] = useState("");
  const [level, setLevel] = useState("B");
  return <div className="dispute-form">  <label className="field-label">{t("disputeReason")}<input value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t("disputePlaceholder")}/></label>
  <label className="field-label">{t("evidenceLevel")}<select value={level} onChange={(e) => setLevel(e.target.value)}><option value="A">A {t("evidenceA")}</option><option value="B">B {t("evidenceB")}</option><option value="C">C {t("evidenceC")}</option><option value="D">D {t("evidenceD")}</option></select></label>
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
