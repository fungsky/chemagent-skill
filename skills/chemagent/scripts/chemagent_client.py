"""ChemAgent API 客户端（仅标准库，Python 3.8+）。

本地免登录版：后端以 `CHEM_AUTH_BYPASS=true` 启动时无需账号密码。

用法示例:
    python chemagent_client.py health
    python chemagent_client.py graph-stats
    python chemagent_client.py search-formulas "环氧" --category 涂料
    python chemagent_client.py formula F-001
    python chemagent_client.py similar F-001 --top-k 5
    python chemagent_client.py search-materials "硅" --function 填料
    python chemagent_client.py materials-detail "气相二氧化硅A200"
    python chemagent_client.py standards
    python chemagent_client.py compliance-domains
    python chemagent_client.py compliance-check              # 内置示例配方演示
    python chemagent_client.py compliance-check --file f.json --domains construction
    python chemagent_client.py kb-stats
    python chemagent_client.py kb-search "球形硅粉 应用"
    python chemagent_client.py kb-upload doc.md
    python chemagent_client.py import-formula f.json        # 登记/批量导入配方
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

DEFAULT_BASE = "http://localhost:8000"


def _setup_utf8():
    """Windows 控制台/管道下强制 UTF-8 输出，避免中文乱码。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def _call(base, method, path, body=None, headers=None, timeout=30):
    """底层请求：body 为原始字节或 None；headers 为 dict。"""
    url = base.rstrip("/") + path
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"raw": raw}
            return resp.status, parsed
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"detail": raw}
        return e.code, parsed
    except urllib.error.URLError as e:
        return 0, {"error": f"无法连接 {base}: {e.reason}"}


def _request(base, method, path, payload=None, timeout=30):
    """JSON 请求：payload 自动序列化为 UTF-8 JSON。"""
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    return _call(base, method, path, body=data, headers=headers, timeout=timeout)


def _upload(base, path, file_path, timeout=30):
    """multipart/form-data 文件上传（字段名固定为 file）。"""
    if not os.path.isfile(file_path):
        return 0, {"error": f"文件不存在: {file_path}"}
    boundary = "----chemagent-" + uuid.uuid4().hex
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        content = f.read()
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    body = head + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    return _call(base, "POST", path, body=body, headers=headers, timeout=timeout)


def _print(data):
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _sample_formula():
    """内置示例配方（水性内墙涂料），便于快速演示合规初筛。"""
    return {
        "name": "水性内墙涂料样品",
        "code": "T-DEMO-001",
        "category": "涂料",
        "items": [
            {"material": {"name": "水", "cas_number": "7732-18-5"}, "weight_percent": 80.0},
            {"material": {"name": "苯", "cas_number": "71-43-2"}, "weight_percent": 3.0},
            {"material": {"name": "甲醛", "cas_number": "50-00-0"}, "weight_percent": 0.5},
            {"material": {"name": "钛白粉", "cas_number": "13463-67-7"}, "weight_percent": 10.0},
            {"material": {"name": "丙烯酸乳液", "cas_number": "9003-01-4"}, "weight_percent": 6.5},
        ],
    }


def main():
    _setup_utf8()
    ap = argparse.ArgumentParser(description="ChemAgent API 客户端（本地免登录，仅标准库）")
    ap.add_argument("--api-base", default=os.environ.get("CHEMAGENT_API_BASE", DEFAULT_BASE))
    ap.add_argument("--timeout", type=int, default=30)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("health", help="服务健康检查")
    sub.add_parser("graph-stats", help="图谱统计概览")

    p = sub.add_parser("search-formulas", help="检索配方")
    p.add_argument("keyword", nargs="?", default="")
    p.add_argument("--category", default="")
    p.add_argument("--materials", default="")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("formula", help="配方详情")
    p.add_argument("code")
    p = sub.add_parser("similar", help="相似配方")
    p.add_argument("code")
    p.add_argument("--top-k", type=int, default=5)

    p = sub.add_parser("search-materials", help="检索原料")
    p.add_argument("keyword", nargs="?", default="")
    p.add_argument("--function", default="")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("materials-detail", help="原料详情与关联配方")
    p.add_argument("name")
    p = sub.add_parser("materials-stats", help="原料使用统计")
    p.add_argument("name")

    p = sub.add_parser("chat", help="AI 问答（后端未配 LLM 时不可用）")
    p.add_argument("message")
    p.add_argument("--agent", action="store_true", help="使用 ReAct 智能体模式")

    sub.add_parser("standards", help="国标/行标登记索引")
    sub.add_parser("compliance-domains", help="合规领域列表")
    p = sub.add_parser("compliance-check", help="配方合规初筛（GB/EU 规则库）")
    p.add_argument("--file", default="", help="JSON 文件：{\"formula\": {...}, \"domains\": [...]}")
    p.add_argument("--formula", default="", help="配方 JSON 字符串（与 --file 二选一）")
    p.add_argument("--domains", default="construction", help="法规领域，逗号分隔，如 construction,cosmetics")

    p = sub.add_parser("kb-stats", help="知识库统计")
    p = sub.add_parser("kb-documents", help="知识库文档列表")
    p = sub.add_parser("kb-search", help="知识库语义检索（需配置 embedding）")
    p.add_argument("query")
    p.add_argument("--top-k", type=int, default=5)
    p = sub.add_parser("kb-upload", help="上传文档到知识库（PDF/DOCX/TXT/XLSX，需配置 embedding）")
    p.add_argument("file")

    p = sub.add_parser("import-formula", help="登记/批量导入配方（JSON 或 4-Sheet Excel）")
    p.add_argument("file")

    args = ap.parse_args()
    base = args.api_base
    timeout = args.timeout

    if args.cmd == "health":
        code, data = _request(base, "GET", "/health", timeout=timeout)
        _print({"status_code": code, **data})
        sys.exit(0 if code == 200 else 1)

    if args.cmd in ("standards", "compliance-domains"):
        path = "/api/compliance/standards" if args.cmd == "standards" else "/api/compliance/domains"
        code, data = _request(base, "GET", path, timeout=timeout)
        _print({"status_code": code, **data} if isinstance(data, dict) else data)
        sys.exit(0 if code == 200 else 1)

    if args.cmd == "graph-stats":
        code, data = _request(base, "GET", "/api/graph/stats", timeout=timeout)
    elif args.cmd == "search-formulas":
        params = {"limit": args.limit}
        if args.keyword:
            params["keyword"] = args.keyword
        if args.category:
            params["category"] = args.category
        if args.materials:
            params["materials"] = args.materials
        qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        code, data = _request(base, "GET", f"/api/formulas?{qs}", timeout=timeout)
    elif args.cmd == "formula":
        code, data = _request(base, "GET", f"/api/formulas/{args.code}", timeout=timeout)
    elif args.cmd == "similar":
        code, data = _request(base, "GET",
                              f"/api/formulas/{args.code}/similar?top_k={args.top_k}",
                              timeout=timeout)
    elif args.cmd == "search-materials":
        params = {"limit": args.limit}
        if args.keyword:
            params["keyword"] = args.keyword
        if args.function:
            params["function"] = args.function
        qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        code, data = _request(base, "GET", f"/api/materials?{qs}", timeout=timeout)
    elif args.cmd == "materials-detail":
        code, data = _request(base, "GET",
                              f"/api/materials/{urllib.parse.quote(args.name)}/detail", timeout=timeout)
    elif args.cmd == "materials-stats":
        code, data = _request(base, "GET",
                              f"/api/materials/{urllib.parse.quote(args.name)}/stats", timeout=timeout)
    elif args.cmd == "chat":
        code, data = _request(base, "POST", "/api/chat",
                              payload={"message": args.message, "use_agent": args.agent},
                              timeout=timeout)
    elif args.cmd == "compliance-check":
        if args.file:
            with open(args.file, encoding="utf-8") as f:
                payload = json.load(f)
        else:
            formula = json.loads(args.formula) if args.formula else _sample_formula()
            payload = {
                "formula": formula,
                "domains": [d.strip() for d in args.domains.split(",") if d.strip()],
            }
        code, data = _request(base, "POST", "/api/compliance/check",
                              payload=payload, timeout=timeout)
    elif args.cmd == "kb-stats":
        code, data = _request(base, "GET", "/api/kb/stats", timeout=timeout)
    elif args.cmd == "kb-documents":
        code, data = _request(base, "GET", "/api/kb/documents", timeout=timeout)
    elif args.cmd == "kb-search":
        code, data = _request(base, "POST", "/api/kb/search",
                              payload={"query": args.query, "top_k": args.top_k},
                              timeout=timeout)
    elif args.cmd == "kb-upload":
        code, data = _upload(base, "/api/kb/upload", args.file, timeout=timeout)
    elif args.cmd == "import-formula":
        code, data = _upload(base, "/api/formulas/import", args.file, timeout=timeout)
    else:
        raise SystemExit(f"未知命令: {args.cmd}")

    if code != 200:
        sys.exit(f"请求失败 ({code}): {data}")
    _print(data)


if __name__ == "__main__":
    main()