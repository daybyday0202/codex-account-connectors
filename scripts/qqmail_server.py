#!/usr/bin/env python3
"""Minimal stdio MCP server for read-only QQ Mail access over IMAP."""

from __future__ import annotations

import datetime as dt
import email
import email.header
import email.utils
import imaplib
import json
import re
import subprocess
import sys
from typing import Any

SERVICE = "codex-qqmail"
ACCOUNT = "qqmail"


def reply(request_id: Any, result: dict[str, Any] | None = None, error: dict[str, Any] | None = None) -> None:
    body = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        body["error"] = error
    else:
        body["result"] = result or {}
    raw = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii") + raw)
    sys.stdout.buffer.flush()


def read_message() -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        if b":" in line:
            key, value = line.decode("ascii", "replace").split(":", 1)
            headers[key.lower().strip()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    return json.loads(sys.stdin.buffer.read(length).decode("utf-8"))


def decode_header(value: str | None) -> str:
    if not value:
        return ""
    return str(email.header.make_header(email.header.decode_header(value)))


def credentials() -> tuple[str, str]:
    try:
        raw = subprocess.check_output(
            ["security", "find-generic-password", "-a", ACCOUNT, "-s", SERVICE, "-w"],
            stderr=subprocess.PIPE,
            text=True,
        ).strip()
        value = json.loads(raw)
        return value["email"], value["password"]
    except Exception as exc:
        raise RuntimeError(
            "QQ 邮箱尚未配置。请先运行：python3 scripts/qqmail_setup.py your-address@qq.com"
        ) from exc


def connection() -> imaplib.IMAP4_SSL:
    address, password = credentials()
    imap = imaplib.IMAP4_SSL("imap.qq.com", 993, timeout=20)
    try:
        imap.login(address, password)
    except Exception:
        imap.logout()
        raise
    return imap


def folders(imap: imaplib.IMAP4_SSL) -> list[str]:
    status, rows = imap.list()
    if status != "OK":
        raise RuntimeError("无法列出 QQ 邮箱文件夹")
    result: list[str] = []
    for row in rows or []:
        text = row.decode("utf-8", "replace") if isinstance(row, bytes) else str(row)
        match = re.search(r'"([^"]+)"\s*$', text)
        result.append(match.group(1) if match else text.rsplit(" ", 1)[-1])
    return result


def text_body(message: email.message.Message, limit: int = 4000) -> str:
    chunks: list[str] = []
    html_chunks: list[str] = []
    parts = message.walk() if message.is_multipart() else [message]
    for part in parts:
        if part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() != "text/plain":
            if part.get_content_type() == "text/html":
                try:
                    html = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
                    html = re.sub(r"(?is)<(script|style).*?>.*?</\\1>", " ", html)
                    html = re.sub(r"(?i)<br\\s*/?>", "\\n", html)
                    html = re.sub(r"(?s)<[^>]+>", " ", html)
                    html_chunks.append(re.sub(r"[ \\t]+", " ", html))
                except Exception:
                    pass
            continue
        try:
            text = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
        except Exception:
            continue
        chunks.append(text)
    return ("\n".join(chunks).strip() or "\n".join(html_chunks).strip())[:limit]


def fetch_email(imap: imaplib.IMAP4_SSL, uid: str, include_body: bool = False) -> dict[str, Any]:
    items = "(BODY.PEEK[] UID)" if include_body else "(BODY.PEEK[HEADER] UID RFC822.SIZE)"
    status, data = imap.uid("fetch", uid, items)
    if status != "OK" or not data:
        raise RuntimeError(f"无法读取邮件 UID {uid}")
    raw = b"".join(part[1] for part in data if isinstance(part, tuple) and isinstance(part[1], bytes))
    message = email.message_from_bytes(raw)
    result = {
        "uid": uid,
        "message_id": message.get("Message-ID", "").strip(),
        "subject": decode_header(message.get("Subject")),
        "from": decode_header(message.get("From")),
        "to": decode_header(message.get("To")),
        "date": message.get("Date", "").strip(),
        "has_attachment": any(p.get_content_disposition() == "attachment" for p in message.walk()),
    }
    if include_body:
        result["body"] = text_body(message)
    return result


def parse_query(query: str) -> tuple[str | None, list[str]]:
    since = None
    terms: list[str] = []
    for token in query.split():
        if token.startswith("after:"):
            since = token[6:].replace("/", "-")
        elif token.startswith("newer_than:") and token.endswith("d"):
            days = int(token[11:-1])
            since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
        elif token.startswith("subject:"):
            terms.append(token[8:])
        elif token.startswith("from:"):
            terms.append(token[5:])
        elif not token.startswith("-"):
            terms.append(token)
    return since, terms


def search(args: dict[str, Any]) -> dict[str, Any]:
    imap = connection()
    try:
        folder = args.get("folder", "INBOX")
        query = str(args.get("query", ""))
        max_results = max(1, min(int(args.get("max_results", 25)), 100))
        imap.select(folder, readonly=True)
        since, terms = parse_query(query)
        criteria: list[str] = ["ALL"]
        if since:
            try:
                date = dt.date.fromisoformat(since).strftime("%d-%b-%Y")
                criteria = ["SINCE", date]
            except ValueError:
                pass
        status, data = imap.uid("search", None, *criteria)
        if status != "OK":
            raise RuntimeError("QQ 邮箱搜索失败")
        uids = (data[0].decode().split() if data and data[0] else [])[-max_results:][::-1]
        rows = []
        for uid in uids:
            item = fetch_email(imap, uid)
            haystack = " ".join(str(item.get(k, "")) for k in ("subject", "from", "to")).lower()
            if terms and not all(term.lower() in haystack for term in terms):
                continue
            rows.append(item)
        return {"emails": rows, "folder": folder, "total": len(rows)}
    finally:
        try:
            imap.logout()
        except Exception:
            pass


TOOLS = [
    {"name": "qqmail_profile", "description": "查看已配置的 QQ 邮箱地址，不读取邮件。", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "qqmail_list_folders", "description": "列出 QQ 邮箱文件夹。", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "qqmail_search_emails", "description": "按日期、主题或发件人搜索 QQ 邮箱邮件。支持 after:YYYY-MM-DD、newer_than:7d、subject: 和 from:。", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "folder": {"type": "string", "default": "INBOX"}, "max_results": {"type": "integer", "minimum": 1, "maximum": 100, "default": 25}}, "required": ["query"]}},
    {"name": "qqmail_read_email", "description": "读取一封 QQ 邮件的正文和元数据，需要先用搜索工具取得 UID。", "inputSchema": {"type": "object", "properties": {"uid": {"type": "string"}, "folder": {"type": "string", "default": "INBOX"}}, "required": ["uid"]}},
]


def call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "qqmail_profile":
        address, _ = credentials()
        return {"email": address}
    imap = connection()
    try:
        if name == "qqmail_list_folders":
            return {"folders": folders(imap)}
    finally:
        try:
            imap.logout()
        except Exception:
            pass
    if name == "qqmail_search_emails":
        return search(args)
    if name == "qqmail_read_email":
        imap = connection()
        try:
            imap.select(args.get("folder", "INBOX"), readonly=True)
            return fetch_email(imap, str(args["uid"]), include_body=True)
        finally:
            try:
                imap.logout()
            except Exception:
                pass
    raise ValueError(f"未知工具：{name}")


def main() -> None:
    while True:
        request = read_message()
        if request is None:
            return
        method = request.get("method")
        request_id = request.get("id")
        if request_id is None:
            continue
        try:
            if method == "initialize":
                result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "qqmail", "version": "0.1.0"}}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                value = call_tool(request["params"]["name"], request["params"].get("arguments", {}))
                result = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}], "structuredContent": value}
            elif method == "ping":
                result = {}
            else:
                reply(request_id, error={"code": -32601, "message": f"Method not found: {method}"})
                continue
            reply(request_id, result=result)
        except Exception as exc:
            reply(request_id, error={"code": -32000, "message": str(exc)})


if __name__ == "__main__":
    main()
