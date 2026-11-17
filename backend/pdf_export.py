import html
import json
import subprocess
import sys
import threading
import time

from weasyprint import HTML


PDF_RESOURCE_LABELS = {
    "households": "顧客一覧 / 客户列表",
    "introductions": "紹介一覧 / 介绍列表",
    "expenses": "経費一覧 / 费用列表",
    "fee_entitlements": "報酬一覧 / 报酬列表",
    "invoice_data": "会計連携データ一覧 / 会计对接数据列表",
    "referral_letter": "住宅紹介状 / 住宅介绍函",
    "management_report": "業務レポート / 业务报告",
}
PDF_TEMPLATE_VERSION = "export-pdf-v2"
PDF_RENDER_CONDITION = threading.Condition()
PDF_RENDER_ACTIVE = 0
PDF_RENDER_PENDING = 0


def build_pdf(headers, rows, resource, created_at, created_by, context=None):
    title = PDF_RESOURCE_LABELS[resource]
    if resource == "referral_letter":
        letter = context or {}
        fields = [
            ("書類番号 / 文书编号", "document_number"),
            ("紹介日 / 介绍日期", "introduced_at"),
            ("世帯コード / 家庭编号", "household_code"),
            ("希望地域 / 意向地区", "area_pref"),
            ("予算帯 / 预算范围", "budget_band"),
            ("土地状況 / 土地状态", "land_status"),
            ("家族構成 / 家庭成员", "family_summary"),
            ("担当顧問 / 负责顾问", "advisor_name"),
            ("店舗 / 门店", "store_name"),
        ]
        detail_rows = "".join(
            f"<tr><th>{html.escape(label)}</th><td>{html.escape(str(letter.get(key, '')))}</td></tr>"
            for label, key in fields
        )
        document = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
  @page {{ size: A4 portrait; margin: 20mm; @bottom-right {{ content: counter(page) " / " counter(pages); color: #64748b; font-size: 8pt; }} }}
  body {{ font-family: "Noto Sans CJK JP", "Noto Sans CJK SC", sans-serif; color: #1e293b; font-size: 10pt; line-height: 1.7; }}
  h1 {{ font-size: 19pt; text-align: center; margin: 12mm 0 16mm; }}
  .recipient {{ font-size: 12pt; font-weight: bold; border-bottom: 1px solid #334155; padding-bottom: 3mm; }}
  .date {{ text-align: right; margin: 8mm 0; }}
  .intro {{ margin: 10mm 0; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8mm; }}
  th, td {{ border: 0.5pt solid #cbd5e1; padding: 6pt; text-align: left; vertical-align: top; }}
  th {{ width: 34%; background: #f1f5f9; }}
  footer {{ margin-top: 12mm; color: #64748b; font-size: 7pt; }}
</style></head>
<body>
  <div class="recipient">{html.escape(str(letter.get("recipient_name", "")))} 御中</div>
  <div class="date">{html.escape(str(letter.get("issued_on", "")))}</div>
  <h1>住宅紹介状 / 住宅介绍函</h1>
  <p class="intro">下記のお客様をご紹介いたします。ご希望条件をご確認のうえ、ご連絡をお願いいたします。<br/>
  兹介绍以下客户。请确认其需求条件后联系客户。</p>
  <table><tbody>{detail_rows}</tbody></table>
  <footer>
    文書番号: {html.escape(str(letter.get("document_number", "")))} · Template {html.escape(str(letter.get("template_version", PDF_TEMPLATE_VERSION)))}<br/>
    作成者: {html.escape(created_by)} · {html.escape(str(created_at))}<br/>
    非公式プロトタイプ／デモデータは全て架空です。 / 非官方原型，演示数据均为虚构。
  </footer>
</body></html>"""

        def deny_external_resources(url, *args, **kwargs):
            raise ValueError(f"External PDF resource is not allowed: {url}")

        return HTML(string=document, url_fetcher=deny_external_resources).write_pdf()

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
  <h1>{html.escape(str((context or {}).get("title", "MallBoard データ出力 / 数据导出")))}</h1>
  <div class="meta">{html.escape(title)} · {len(rows)} 件 / 条 ·
    {html.escape(str(created_at))} · {html.escape(created_by)} · Template {PDF_TEMPLATE_VERSION}
  </div>
  <table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
  <footer>非公式プロトタイプ／デモデータは全て架空です。 / 非官方原型，演示数据均为虚构。</footer>
</body></html>"""

    def deny_external_resources(url, *args, **kwargs):
        raise ValueError(f"External PDF resource is not allowed: {url}")

    return HTML(string=document, url_fetcher=deny_external_resources).write_pdf()


def build_pdf_isolated(headers, rows, resource, created_at, created_by, timeout_seconds,
                       max_concurrency=1, max_pending=1, context=None):
    global PDF_RENDER_ACTIVE, PDF_RENDER_PENDING
    deadline = time.monotonic() + timeout_seconds
    with PDF_RENDER_CONDITION:
        if PDF_RENDER_ACTIVE >= max_concurrency:
            if PDF_RENDER_PENDING >= max_pending:
                raise RuntimeError("PDF_RENDER_QUEUE_FULL")
            PDF_RENDER_PENDING += 1
            try:
                while PDF_RENDER_ACTIVE >= max_concurrency:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError("PDF_RENDER_TIMEOUT")
                    PDF_RENDER_CONDITION.wait(remaining)
            finally:
                PDF_RENDER_PENDING -= 1
        PDF_RENDER_ACTIVE += 1
    try:
        payload = json.dumps({
            "headers": headers,
            "rows": rows,
            "resource": resource,
            "created_at": str(created_at),
            "created_by": created_by,
            "context": context,
        }, ensure_ascii=False, default=str).encode("utf-8")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "backend.pdf_export"],
                input=payload,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=max(1, deadline - time.monotonic()),
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise TimeoutError("PDF_RENDER_TIMEOUT") from error
        if result.returncode:
            raise RuntimeError("PDF_RENDER_FAILED")
        if not result.stdout.startswith(b"%PDF-"):
            raise RuntimeError("PDF_RENDER_INVALID_OUTPUT")
        return result.stdout
    finally:
        with PDF_RENDER_CONDITION:
            PDF_RENDER_ACTIVE -= 1
            PDF_RENDER_CONDITION.notify_all()


def main():
    request = json.load(sys.stdin)
    pdf = build_pdf(
        request["headers"], request["rows"], request["resource"],
        request["created_at"], request["created_by"], request.get("context"),
    )
    sys.stdout.buffer.write(pdf)


if __name__ == "__main__":
    main()
