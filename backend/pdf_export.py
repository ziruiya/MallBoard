import html

from weasyprint import HTML


PDF_RESOURCE_LABELS = {
    "households": "顧客一覧 / 客户列表",
    "introductions": "紹介一覧 / 介绍列表",
    "expenses": "経費一覧 / 费用列表",
    "fee_entitlements": "報酬一覧 / 报酬列表",
    "invoice_data": "会計連携データ一覧 / 会计对接数据列表",
}
PDF_TEMPLATE_VERSION = "export-pdf-v1"


def build_pdf(headers, rows, resource, created_at, created_by):
    title = PDF_RESOURCE_LABELS[resource]
    head = "".join(f"<th>{html.escape(str(value))}</th>" for value in headers)
    body = "".join(
        "<tr>" + "".join(
            f"<td>{html.escape('' if value is None else str(value))}</td>" for value in row
        ) + "</tr>"
        for row in rows
    )
    if not body:
        body = f'<tr><td class="empty" colspan="{len(headers)}">データがありません / 暂无数据</td></tr>'
    document = f"""<!doctype html>
<html lang="ja">
<head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
  @page {{ size: A4 landscape; margin: 12mm; @bottom-right {{ content: counter(page) " / " counter(pages); color: #64748b; font-size: 8pt; }} }}
  body {{ font-family: "Noto Sans CJK JP", "Noto Sans CJK SC", sans-serif; color: #1e293b; font-size: 8pt; }}
  h1 {{ font-size: 17pt; margin: 0 0 5mm; }}
  .meta {{ color: #475569; font-size: 8pt; margin-bottom: 5mm; }}
  table {{ width: 100%; border-collapse: collapse; table-layout: auto; }}
  th, td {{ border: 0.4pt solid #cbd5e1; padding: 4pt; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
  th {{ background: #eef2ff; font-weight: bold; }}
  tr {{ break-inside: avoid; }}
  .empty {{ text-align: center; color: #64748b; padding: 14pt; }}
  footer {{ margin-top: 5mm; color: #64748b; font-size: 7pt; }}
</style></head>
<body>
  <h1>MallBoard データ出力 / 数据导出</h1>
  <div class="meta">{html.escape(title)} · {len(rows)} 件 / 条 ·
    {html.escape(str(created_at))} · {html.escape(created_by)} · Template {PDF_TEMPLATE_VERSION}
  </div>
  <table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
  <footer>非公式プロトタイプ／デモデータは全て架空です。 / 非官方原型，演示数据均为虚构。</footer>
</body></html>"""

    def deny_external_resources(url, *args, **kwargs):
        raise ValueError(f"External PDF resource is not allowed: {url}")

    return HTML(string=document, url_fetcher=deny_external_resources).write_pdf()
