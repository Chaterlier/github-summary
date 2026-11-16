#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发送日报邮件到网易邮箱。

用法: python send_email.py <report_md_path> [subject]
配置: 同目录 mail_config.json（smtp_host/smtp_port/user/password/to）
"""
import json
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.stdout.reconfigure(encoding="utf-8")


def md_to_html(text):
    try:
        from markdown_it import MarkdownIt
        body = MarkdownIt().render(text)
    except Exception:
        import html
        body = ('<pre style="font-family: Consolas, monospace; '
                f'white-space: pre-wrap;">{html.escape(text)}</pre>')
    return (
        "<html><body style=\"font-family: 'Microsoft YaHei', sans-serif; "
        f"max-width: 860px; margin: auto; padding: 24px; line-height: 1.6;\">"
        f"{body}</body></html>"
    )


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法: python send_email.py <report_md_path> [subject]")
    report_path = sys.argv[1]
    with open(report_path, encoding="utf-8") as f:
        content = f.read()

    subject = sys.argv[2] if len(sys.argv) > 2 else \
        f"GitHub Issue 日报 {datetime.now():%Y-%m-%d}"

    with open(os.path.join(BASE_DIR, "mail_config.json"), encoding="utf-8") as f:
        cfg = json.load(f)

    msg = MIMEText(md_to_html(content), "html", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr((str(Header("GitHub 日报", "utf-8")), cfg["user"]))
    msg["To"] = cfg["to"]

    with smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"], timeout=30) as smtp:
        smtp.login(cfg["user"], cfg["password"])
        smtp.sendmail(cfg["user"], [cfg["to"]], msg.as_string())

    print(f"[ok] 邮件已发送: {subject} -> {cfg['to']}")


if __name__ == "__main__":
    main()
