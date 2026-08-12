#!/usr/bin/env python3
"""Store QQ Mail IMAP credentials in macOS Keychain after a live login check."""

from __future__ import annotations

import getpass
import imaplib
import json
import smtplib
import ssl
import subprocess
import sys
from pathlib import Path

SERVICE = "codex-qqmail"
ACCOUNT = "qqmail"


def keychain_write(payload: str) -> None:
    subprocess.run(
        ["security", "delete-generic-password", "-a", ACCOUNT, "-s", SERVICE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    subprocess.run(
        ["security", "add-generic-password", "-a", ACCOUNT, "-s", SERVICE, "-w", payload],
        check=True,
    )


def verify(email: str, password: str) -> None:
    with imaplib.IMAP4_SSL("imap.qq.com", 993, timeout=15) as imap:
        imap.login(email, password)
        imap.logout()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.qq.com", 465, context=context, timeout=15) as smtp:
        smtp.login(email, password)


def main() -> int:
    email = (sys.argv[1] if len(sys.argv) > 1 else input("QQ 邮箱地址: ")).strip()
    if not email or "@qq.com" not in email.lower():
        print("请输入完整的 QQ 邮箱地址，例如 name@qq.com", file=sys.stderr)
        return 2
    password = getpass.getpass("QQ 邮箱授权码（不是登录密码）: ")
    if not password:
        print("授权码不能为空", file=sys.stderr)
        return 2
    try:
        print("正在验证 IMAP/SMTP 登录…")
        verify(email, password)
    except Exception as exc:
        print(f"验证失败：{exc}", file=sys.stderr)
        print("请在 QQ 邮箱设置中开启 IMAP/SMTP，并使用生成的授权码。", file=sys.stderr)
        return 1
    payload = json.dumps({"email": email, "password": password}, ensure_ascii=False)
    keychain_write(payload)
    print(f"已将 {email} 的 QQ 邮箱凭证保存到 macOS 钥匙串（服务名：{SERVICE}）。")
    print("授权码不会写入配置文件。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
