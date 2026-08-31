"""资源完整性校验脚本（构建产物验证，P0）。

检查三件事：
1. 本地文件清单：dist/textures 与 public/textures 一一对应（防止构建漏拷 / 新增资源忘记放进 public）
2. dist 根禁止文件（public 维护双件 AGENTS.md/README.md 不应进入发布包，vite.config 有清理钩子，此处防回归）
3. 运行中服务器：对 base_url 逐个 GET 全部纹理与入口页，断言全 200（防止路径坏了只显示黑屏/白模）

用法:
    python tests/run_checks.py                # 仅本地文件检查（不需要服务器）
    python tests/run_checks.py http://localhost:8000   # 本地检查 + HTTP 全量校验

退出码: 0 = 全部通过; 1 = 有失败
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
DIST = ROOT / "dist"

# public 维护双件会被 publicDir 拷入 dist，构建钩子负责清理；此处在测试侧防回归
DIST_FORBIDDEN = {"README.md", "AGENTS.md"}

failures: list[str] = []


def rel_set(base: Path) -> set[str]:
    out: set[str] = set()
    for p in (base / "textures").rglob("*"):
        if p.is_file():
            out.add(p.relative_to(base).as_posix())
    return out


def check_file_lists() -> None:
    if not DIST.exists():
        failures.append(f"dist 不存在: {DIST}（先跑 npm run build）")
        return
    pub, dst = rel_set(PUBLIC), rel_set(DIST)
    for f in sorted(pub - dst):
        failures.append(f"dist 缺失（public 有）: {f}")
    for f in sorted(dst - pub):
        failures.append(f"dist 多余（public 没有）: {f}")
    print(f"文件清单: public={len(pub)} dist={len(dst)}")


def check_http(base: str) -> None:
    import urllib.request

    targets = ["index.html"]
    tex = sorted(rel_set(PUBLIC))
    targets += tex
    if not tex:
        failures.append("public/textures 为空")
        return
    for t in targets:
        url = base.rstrip("/") + "/" + t
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                if r.status != 200:
                    failures.append(f"HTTP {r.status}: {url}")
                else:
                    print(f"OK  {url}")
        except Exception as e:
            failures.append(f"FAIL {url}: {e}")


def check_dist_root() -> None:
    for name in DIST_FORBIDDEN:
        if (DIST / name).exists():
            failures.append(f"dist 根出现不应打包的文件: {name}（public 维护双件被误拷，见 vite.config.ts closeBundle）")


def main() -> int:
    check_file_lists()
    check_dist_root()
    if len(sys.argv) > 1:
        check_http(sys.argv[1])
    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        print(f"\n{len(failures)} 项失败")
        return 1
    print("资源完整性校验全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())