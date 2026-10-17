"""把 public/textures 下的 PNG/JPG 全量转成 WebP（同分辨率、保持透明通道）。

用法:
    uv run python scripts/optimize_images.py              # 转换并删除原图（原图可由 git 历史找回）
    uv run python scripts/optimize_images.py --dry-run    # 只打印体积对比，不落盘、不删原图
    uv run python scripts/optimize_images.py --quality 88 # 质量 0-100，默认 85

退出码: 0 = 成功; 1 = 有文件转换失败或缺少 Pillow
"""

import argparse
import contextlib
import io
import sys
from pathlib import Path

# Windows 控制台默认 GBK 无法打印全角字符，统一用 UTF-8 输出
# （与 launcher.py / tests/run_checks.py / tests/run_e2e.py 同法，本仓第 4 个 Python 入口）
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        with contextlib.suppress(OSError, ValueError):
            stream.reconfigure(encoding="utf-8", errors="replace")

try:  # dev 组依赖；缺了给出可操作的提示，而不是抛 traceback
    from PIL import Image
except ImportError:  # pragma: no cover — 只在未 uv sync 的环境命中
    Image = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "public" / "textures"
SUFFIXES = {".png", ".jpg", ".jpeg"}
METHOD = 6  # 0-6，越大越慢、压缩越好


def convert(path: Path, quality: int, dry_run: bool) -> tuple[int, int, bool]:
    """返回 (原大小, 新大小, 是否成功)；dry_run 只估算体积，不写盘也不删原图。"""
    before = path.stat().st_size
    out = path.with_suffix(".webp")
    try:
        with Image.open(path) as im:
            im.load()
            has_alpha = im.mode in ("RGBA", "LA") or (
                im.mode == "P" and "transparency" in im.info
            )
            im = im.convert("RGBA" if has_alpha else "RGB")
            if dry_run:
                # 写进内存缓冲区只为拿体积，磁盘不留产物
                buf = io.BytesIO()
                im.save(buf, "WEBP", quality=quality, method=METHOD, alpha_quality=100)
                return before, buf.tell(), True
            im.save(out, "WEBP", quality=quality, method=METHOD, alpha_quality=100)
        after = out.stat().st_size
        path.unlink()
        return before, after, True
    except Exception as e:  # noqa: BLE001 — 单张失败不该中断整轮
        print(f"  [FAIL] {path.name}: {e}")
        return before, 0, False


def main() -> int:
    ap = argparse.ArgumentParser(description="纹理批量转 WebP")
    ap.add_argument(
        "--quality", type=int, default=85, help="WebP 质量 0-100（默认 85）"
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="只对比体积，不写文件、不删原图",
    )
    args = ap.parse_args()

    if Image is None:
        print("[Error] 缺少 Pillow：先跑 `uv sync`（dev 组已声明 pillow）")
        return 1

    files = sorted(p for p in TARGET.rglob("*") if p.suffix.lower() in SUFFIXES)
    if not files:
        print(f"没有待转换文件（{TARGET}）")
        return 0

    total_before = total_after = 0
    failed = 0
    for p in files:
        before, after, ok = convert(p, args.quality, args.dry_run)
        total_before += before
        total_after += after
        if not ok:
            failed += 1
            continue
        rel = p.relative_to(TARGET)
        print(
            f"  {rel.as_posix():28} {before / 1024:8.0f}KB -> {after / 1024:7.0f}KB"
            f"  ({after / before * 100:5.1f}%)"
        )

    saved = total_before - total_after
    tip = "  [dry-run：未落盘]" if args.dry_run else ""
    print(
        f"\n合计: {total_before / 1024 / 1024:.1f}MB -> {total_after / 1024 / 1024:.1f}MB"
        f"（省 {saved / 1024 / 1024:.1f}MB / {saved / total_before * 100:.0f}%）"
        f"  转换 {len(files) - failed}/{len(files)}{tip}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
