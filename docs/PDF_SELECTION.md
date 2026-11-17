# PDF 技术选型报告

## 结论 / 結論

**已按用户批准采用 WeasyPrint。**PDF 用于 Settings 中的数据列表导出，以及 Introduction 详情中的住宅介绍状；不提供发票或账单打印功能。

推荐理由：MallBoard 已有 FastAPI 单容器与静态前端，业务文书可用服务端 HTML 模板描述，再由 WeasyPrint 转为 PDF。相比直接逐坐标绘制，分页表格和日中双语布局更容易维护。

## 候选比较

| 方案 | 优点 | 代价 / 风险 | 判断 |
| --- | --- | --- | --- |
| WeasyPrint | HTML/CSS 模板；适合日中双语、表格和分页文书；官方提供 Python API | Debian 镜像需额外安装 Pango/HarfBuzz 运行库和日文字体；不可信 HTML/CSS 可能带来安全风险 | **推荐**。使用服务端固定模板、自动转义用户数据、限制资源读取到本地资产 |
| ReportLab | Python API；官方文档说明可使用 Unicode 文本和嵌入 TrueType 字体；不需要浏览器运行时 | 布局、分页、表格换页需在 Python 中显式维护；字体需随镜像受控分发 | 适合版式非常固定、页数少的表单；非首选 |
| Headless Chromium | 浏览器渲染能力和 CSS 覆盖面高 | 引入大型浏览器运行时和更多镜像/更新面；当前需求未要求运行 JavaScript 或浏览器级精确渲染 | 对此原型过重 |

## 官方依据

- WeasyPrint 安装说明列出了 Pango 等运行依赖，并指出 Debian 11 及以上可通过系统包安装；字体章节说明缺少字体会导致字符缺失或显示方框：
  <https://doc.courtbouillon.org/weasyprint/stable/first_steps.html>
- WeasyPrint Python API 支持 `HTML(...).write_pdf(...)`；官方同时警告，使用不可信 HTML/CSS 可能产生安全问题：
  <https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#python-library>
- ReportLab 官方字体章节说明文本输入为 Unicode/UTF-8，并记录了 TrueType 字体支持及字体嵌入方式：
  <https://docs.reportlab.com/reportlab/userguide/ch3_fonts/>

## 实现约束

1. `backend/requirements.txt` 固定 WeasyPrint 版本；Debian 镜像内安装 Pango/HarfBuzz 与 Noto CJK 字体，不要求宿主机安装 Node 或 PDF 软件。
2. 只用服务端固定 HTML/CSS 模板生成；字段内容进行 HTML 转义，不接受用户提供的 HTML、CSS、URL 或文件路径。资源 URL fetcher 默认拒绝任何外部资源读取。
3. PDF 使用现有 CSV 导出数据和资源权限，复用行数/文件大小限制、短期下载、个人信息授权、下载审计和记录级再授权。
4. 导出任务保存文书类型、模板版本、创建者/角色范围、记录 ID、生成时间和内容 SHA-256。下载响应使用 `application/pdf`、`no-store` 与 `nosniff`。
5. 日中双语界面可选择 CSV 或 PDF。PDF 是导出列表报表，不含签章/税务票据功能；会计连携数据也不代表发票或入金消込。
6. 介绍状使用独立的固定双语模板；仅包含 household code、希望地区、预算带、土地状态与家庭构成，不包含姓名、电话、邮件、FP 原始诊断或合同资料。内容在服务端转义，拒绝外部资源。
7. 生成必须有针对当前住宅会社、指定用途、L3 范围的有效 Consent；检查同意方法、版本、授权字段、撤回与失效时间。每次生成保存独立文书版本、文件 SHA-256、生成记录和 AuditEvent，并更新 Introduction 的最新介绍状 ID。
8. PDF 放在 Compose 的私有 `referral-documents` named volume，而非前端静态目录；数据库仅保存私有存储键和校验元数据。预览/下载再次校验家庭访问范围、到期时间、文件状态和 SHA-256，并写入审计。到期文件可通过受限清理接口单独删除，文书生成与审计记录保留。
9. 介绍状有效期默认 30 日并作为 SystemConfig 可配置项；这是演示暂定值，生产采用期限和同意文言须由公司确认。

## 确认状态 / 状态

用户已明确批准 **WeasyPrint**。实现已纳入项目镜像、导出界面和介绍状生成流程；部署和服务器验收由用户方负责。
