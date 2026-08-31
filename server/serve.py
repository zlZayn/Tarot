"""Ethereal Tarot 本地启动器（纯标准库，零依赖）。

解决三个实际问题：
1. 端口 8000 被占用 -> 自动顺延（8001、8002 ...）
2. 关窗口/Ctrl+C 残留 python 进程 -> 同进程运行 HTTP 服务，退出即零残留
3. dist 缺失/过期 -> 明确提示；开发机上有 src 时对比 mtime 警告"可能过期"

用法:
    python server/serve.py --dir dist [--port 8000] [--open] [--no-check]

退出码: 0 = 正常运行结束; 1 = dist 缺失等致命错误
"""
import argparse
import socket
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def err(msg: str) -> int:
    print(f"[Error] {msg}")
    return 1


def warn(msg: str) -> None:
    print(f"[警告] {msg}")


def latest_mtime(base: Path) -> float:
    return max((f.stat().st_mtime for f in base.rglob("*") if f.is_file()), default=0.0)


def check_stale(dist: Path) -> bool:
    """源码（src + public）比 dist 新时返回 True；发布包（无 src/public）返回 False。"""
    src = ROOT / "src"
    pub = ROOT / "public"
    if not src.exists() and not pub.exists():
        return False
    src_newest = max(latest_mtime(src), latest_mtime(pub))
    return src_newest > latest_mtime(dist) + 1


def pick_port(start: int) -> int:
    for port in range(start, start + 10):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"端口 {start}~{start + 9} 均被占用")


def serve(dist: Path, start_port: int, open_browser: bool, check: bool = True) -> int:
    if not dist.is_dir() or not (dist / "index.html").is_file():
        return err(f"目录 {dist} 缺少 index.html，先运行 Build.bat 或 npm run build")
    if check and check_stale(dist):
        warn("检测到源码比 dist 新，当前启动的可能是旧版本；需要我可运行 Build.bat / npm run build")

    try:
        port = pick_port(start_port)
    except RuntimeError as e:
        return err(str(e))

    handler = partial(SimpleHTTPRequestHandler, directory=str(dist))
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://localhost:{port}"
    print(f"Ethereal Tarot 运行中: {url}  (目录: {dist})")
    print(f"按 Ctrl+C 退出")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("服务已停止（无残留进程）")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ethereal Tarot 本地启动器")
    ap.add_argument("--dir", default="dist", help="要服务的目录（默认 dist）")
    ap.add_argument("--port", type=int, default=8000, help="起始端口（默认 8000，被占用自动顺延）")
    ap.add_argument("--open", action="store_true", help="启动后自动打开浏览器")
    ap.add_argument("--no-check", action="store_true", help="跳过过期检查（默认不跳过）")
    args = ap.parse_args(argv)

    if args.no_check:
        return serve(ROOT / args.dir, args.port, args.open, check=False)
    return serve(ROOT / args.dir, args.port, args.open, check=True)


if __name__ == "__main__":
    sys.exit(main())