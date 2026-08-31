"""分布式完整性校验（纯逻辑，零 Rich 依赖）。

依据 docs 里接收的校验维度：
- 源码指纹：src/**/*.{ts,css,html} 的 SHA-256（路径排序 + 内容哈希）
- 资源指纹：public/**/* 的目录树哈希
- 配置指纹：vite.config.ts / tsconfig.json / package.json 等直散
- 产物存在性：dist/index.html
- 元数据完整性：.ethereal-meta.json（项目根）可解析且版本一致

判定：need_rebuild + reasons 列表；全部通过才免重建。
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from . import config as C


@dataclass
class BuildStatus:
    need_rebuild: bool
    reasons: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _tree_hash(base: Path, exts: set[str] | None = None, relative_dir: Path | None = None) -> str:
    """递归对 base 下所有文件（可选后缀过滤）算统一哈希；无文件返回 'empty'。"""
    files: list[Path] = []
    root = relative_dir or base
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if exts is not None and p.suffix not in exts:
            continue
        files.append(p)
    if not files:
        return "empty"
    h = hashlib.sha256()
    for p in sorted(files, key=lambda f: f.relative_to(root).as_posix()):
        rel = p.relative_to(root).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(_hash_file(p).encode("utf-8"))
        h.update(b"\0")
    return h.hexdigest()


def src_hash() -> str:
    return _tree_hash(C.SRC, exts=C.SRC_EXTS, relative_dir=C.ROOT)


def res_hash() -> str:
    return _tree_hash(C.PUBLIC, relative_dir=C.ROOT)


def config_hash() -> str:
    h = hashlib.sha256()
    for name in C.CONFIG_FILES:
        p = C.ROOT / name
        if p.is_file():
            h.update(name.encode("utf-8"))
            h.update(b"\0")
            h.update(_hash_file(p).encode("utf-8"))
    return h.hexdigest()


def read_meta() -> dict | None:
    if not C.BUILD_META.is_file():
        return None
    try:
        data = json.loads(C.BUILD_META.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict) or data.get("version") != C.META_VERSION:
        return None
    return data


def write_meta(details: dict) -> None:
    C.BUILD_META.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": C.META_VERSION,
        "src_hash": details.get("src_hash", ""),
        "res_hash": details.get("res_hash", ""),
        "config_hash": details.get("config_hash", ""),
        "timestamp": details.get("timestamp", ""),
    }
    C.BUILD_META.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def check(force: bool = False) -> BuildStatus:
    """返回是否需要重建及原因。force=True 时仅返回状态（不比较哈希）。"""
    if force:
        return BuildStatus(need_rebuild=True, reasons=["--force 或 [R] 手动触发"])

    meta = read_meta()
    cur = {
        "src_hash": src_hash(),
        "res_hash": res_hash(),
        "config_hash": config_hash(),
    }
    if meta is None:
        return BuildStatus(need_rebuild=True, reasons=["缺少构建元数据（首次构建）"], details=cur)

    if not (C.DIST / "index.html").is_file():
        return BuildStatus(need_rebuild=True, reasons=["dist/index.html 不存在"], details=cur)

    reasons = []
    for key, label in (
        ("src_hash", "源码变更"),
        ("res_hash", "资源变更"),
        ("config_hash", "构建配置变更"),
    ):
        if meta.get(key) != cur[key]:
            reasons.append(f"{label}（{key}）")
    return BuildStatus(need_rebuild=bool(reasons), reasons=reasons, details=cur)