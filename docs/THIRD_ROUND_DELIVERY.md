# MallBoard 第三轮施工交付记录

基线：`b819b02`（`main`）
实现：本次工作区变更
环境边界：仅使用隔离的 MySQL 8 测试容器；未连接或部署生产机，未运行本地浏览器验收。

## T01–T07 对应结果

| 编号 | 结果 | 实现与边界 |
| --- | --- | --- |
| T01 | 完成 | 修复 App 启动 effect 对未定义 `userId` 的依赖；将通知刷新逻辑移入 App 作用域，并以 ESLint `no-undef` 防止同类错误。 |
| T02 | 保持 | 保留 Dashboard、Households、Introductions、Revenue、Management、Settings 六个顶层业务页；新增功能仍通过页内区块与筛选承载。 |
| T03 | 条件不满足，未新增店铺商谈队列 | Negotiation 没有独立的次回行动字段，Activity 的行动字段属于 Household。将家庭级行动误当成商谈级待办会造成错误归属；当前继续使用既有 Task/Activity。 |
| T04 | 完成 | 使用 WeasyPrint；PDF 渲染移入独立子进程，加入并发、排队、超时与输出校验。住宅介绍状使用固定模板、L3 同意与字段白名单，生成/访问均审计，文件存于独立 Compose named volume。 |
| T05 | 完成 | 扩展费用申请日期、税额/税区分、会计连携引用等字段；演示数据补充费用及月结样例。导出下载增加 SHA-256 校验、记录与异常审计。 |
| T06 | 完成 | 保持现有月结状态机与快照做法，新增的费用及月结样例沿用现有数据模型；没有增加独立发票或部分入金模型。 |
| T07 | 完成 | 延续受权限和范围约束的 CSV/PDF 导出；增加下载时内容哈希核对、下载记录及异常审计。 |

## 本轮交付范围

- Management 增加七阶段 StageEvent 漏斗、异常卡片、门店运营维度、来源归因、Cohort 与住宅会社报酬处理质量；提供专项 PDF 报告。
- Household 搜索在服务端统一规范化，并按当前角色范围过滤家庭、人员、联系方式、住宅会社及担当者字段。
- 演示用户在 `DEMO_MODE` 下可直接切换角色，不再被随机初始化密码的强制改密状态拦截；非演示登录仍沿用账户认证流程。
- `bootstrap` 仅返回身份、权限、菜单、枚举与环境信息；Dashboard 汇总、待办及趋势通过独立 API 返回。

## 验证记录

- `npm.cmd --prefix frontend run build`：通过，包含 ESLint。
- `python -m py_compile backend\main.py backend\pdf_export.py`：通过。
- `git diff --check`：通过。
- 使用临时非生产变量执行 `docker compose config --quiet`：通过。
- Docker 应用镜像构建：通过，包含 WeasyPrint 运行库。
- 隔离 MySQL 8 API 验证：首次初始化成功；四种演示角色登录后可读取各自 Dashboard；`bootstrap` 不包含家庭或报酬明细；验证了 60 个家庭、72 条介绍、7 阶段漏斗、12 店运营维度、12 家住宅会社报酬质量及非空来源归因。
- 管理漏斗 PDF 与住宅介绍状 PDF 在应用容器内生成并返回 PDF 内容；撤销介绍状 Consent 后，文件访问被拒绝。
- 未执行本地浏览器验收或服务器部署/重启验收；按用户要求由服务器侧负责。

## 生产前待确认

- 店铺级商谈待办需先明确并实现 Negotiation 级次回行动与期限字段，不能以 Household 级 Activity 推断。
- 介绍状有效期、同意书文言及 Consent 保存期限需由公司确认；当前 30 日有效期仅为演示默认值。
- 生产版角色身份应由认证身份决定；演示版角色切换仅限 `DEMO_MODE`。
