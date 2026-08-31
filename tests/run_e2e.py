"""Ethereal Tarot 冒烟 / 交互 E2E（Playwright，Python）。

覆盖（对应验收标准）:
- 页面加载：loader 消失（22 张纹理加载完）、无 console.error / pageerror / 同源 4xx
- UI 文案：logo、三个按钮、guide 初始为英文
- 核心交互：连续抽 3 张牌 → 展开视图 → 收回 → 历史组点击回顾
- 新增功能：localStorage 写入一条 schemaVersion=1 的 3 张记录
- 截图存档：tests/artifacts/

用法: python tests/run_e2e.py [base_url]   # 默认 http://localhost:8000
退出码: 0 = 全部通过; 1 = 有失败
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
ART = Path(__file__).resolve().parent / "artifacts"
ART.mkdir(parents=True, exist_ok=True)

W, H = 1280, 800

# Windows 控制台默认 GBK 无法打印 • 等字符，统一用 UTF-8 输出
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main() -> int:
    fatal: list[str] = []
    warns: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": W, "height": H})

        page.on("console", lambda m: fatal.append(f"console.error: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: fatal.append(f"pageerror: {e}"))
        page.on("response", lambda r: (
            warns.append(f"外部资源 HTTP {r.status}: {r.url}")
            if r.status >= 400 and not r.url.startswith(BASE)
            else (fatal.append(f"同源 HTTP {r.status}: {r.url}") if r.status >= 400 else None)
        ))

        def result_visible() -> bool:
            return page.evaluate(
                "parseFloat(getComputedStyle(document.getElementById('result-area')).opacity) > 0.5"
            )

        def wait_result(timeout_s: float) -> bool:
            deadline = time.time() + timeout_s
            while time.time() < deadline:
                if result_visible():
                    return True
                page.wait_for_timeout(150)
            return False

        def wait_clear(timeout_s: float) -> bool:
            deadline = time.time() + timeout_s
            while time.time() < deadline:
                if not result_visible():
                    return True
                page.wait_for_timeout(200)
            return False

        # --- 1. 加载 ---
        page.goto(BASE + "/")
        page.wait_for_selector("#loader", state="detached", timeout=120_000)
        print("[ok] loader 消失（22 张纹理加载完成）")

        # --- 2. UI 文案（默认英文） ---
        expect = {
            "#logo-text": "ETHEREAL TAROT",
            "#mode-toggle": "Camera Off",
            "#shuffle-btn": "Shuffle Deck",
            "#lang-btn": "Language: EN",
            "#guide-text": "DRAG TO SCROLL • CLICK TO SELECT",
        }
        for sel, want in expect.items():
            got = page.text_content(sel)
            if got != want:
                fatal.append(f"{sel} 文案不符: got={got!r} want={want!r}")
        if page.locator("#canvas-container canvas").count() != 1:
            fatal.append("canvas 未创建")
        print("[ok] UI 文案与 canvas 就绪")

        shot = lambda n: page.screenshot(path=str(ART / f"{n}.png"))
        shot("01-init")

        # --- 3. 连抽 3 张（点击 → 轮询翻牌动画 → 点击收起） ---
        names: list[str] = []
        for draw in range(1, 4):
            if not wait_clear(8):
                fatal.append(f"第 {draw} 张开始前结果区未收起")
            hit = False
            for i in range(40):
                if result_visible():
                    break  # 上一轮残留状态，直接判定
                x = 30 + (W - 60) * i / 39
                page.mouse.click(x, H * 0.5)
                if wait_result(3):
                    hit = True
                    break
            if not hit:
                fatal.append(f"第 {draw} 张牌未被选中")
                continue
            page.wait_for_timeout(700)  # opacity 过渡 0.5s 收尾
            name = (page.text_content("#r-name") or "").strip()
            if "•" in name:
                fatal.append(f"第 {draw} 张处于展开/回顾态而非单牌态: {name!r}")
            names.append(name)
            print(f"[ok] 第 {draw} 张选中: {name}")
            shot(f"0{draw}-show")
            page.mouse.click(W * 0.5, H * 0.5)  # dismiss
            page.wait_for_timeout(1200)  # 飞回角落动画（前两张）
        page.wait_for_timeout(1600)  # 第 3 张 dismiss → 展开视图动画

        # --- 4. 展开视图 ---
        def wait_text(sel: str, want: str, timeout_s: float) -> str:
            deadline = time.time() + timeout_s
            got = ""
            while time.time() < deadline:
                got = (page.text_content(sel) or "").strip()
                if got == want:
                    return got
                page.wait_for_timeout(200)
            return got

        spread_desc = wait_text("#r-desc", "PAST • PRESENT • FUTURE", 6)
        if spread_desc != "PAST • PRESENT • FUTURE":
            fatal.append(f"展开视图文案不符: got={spread_desc!r}")
        else:
            print("[ok] 展开视图: PAST • PRESENT • FUTURE")
        shot("04-spread")

        # --- 5. localStorage 记录 ---
        try:
            recs = page.evaluate("JSON.parse(localStorage.getItem('ethereal-tarot:records') || '[]')")
            ok = (
                len(recs) == 1
                and len(recs[0]["cards"]) == 3
                and recs[0]["mode"] == "MOUSE"
                and recs[0]["language"] == "en"
                and recs[0]["schemaVersion"] == 1
                and bool(recs[0]["id"]) and bool(recs[0]["time"])
            )
            if ok:
                print("[ok] localStorage 记录: 1 条 / 3 张 / MOUSE / en / schemaVersion=1")
            else:
                fatal.append(f"localStorage 记录异常: {recs}")
        except Exception as e:
            fatal.append(f"localStorage 检查失败: {e}")

        # --- 6. 收回展开 → 历史组（3 张缩略图） ---
        page.mouse.click(W * 0.5, H * 0.5)
        deadline = time.time() + 8
        groups_ok = False
        while time.time() < deadline:
            groups = page.locator("#history-box .h-group")
            hitem = page.locator("#history-box .h-item")
            if groups.count() >= 1 and hitem.count() == 3:
                groups_ok = True
                break
            page.wait_for_timeout(300)
        if not groups_ok:
            fatal.append(f"历史组异常: groups={groups.count()} h-items={hitem.count()}")
        else:
            print("[ok] 历史组: 1 组 / 3 张缩略图")

        # --- 7. 点击历史组 → 回顾视图 ---
        groups.first.click()
        rev_desc = wait_text("#r-desc", "REVIEWING SESSION", 8)
        if rev_desc != "REVIEWING SESSION":
            fatal.append(f"回顾视图文案不符: got={rev_desc!r}")
        else:
            print("[ok] 回顾视图: REVIEWING SESSION")
        shot("07-review")
        page.mouse.click(W * 0.5, H * 0.5)  # 关闭回顾
        page.wait_for_timeout(1000)

        # --- 8. 截图体积软检查（防全黑静默失败） ---
        for f in sorted(ART.glob("*.png")):
            print(f"      截图 {f.name}: {f.stat().st_size // 1024} KB")

        browser.close()

    print()
    if warns:
        print("警告（外部资源，不判定失败）:")
        for w in warns:
            print("  ", w)
    if fatal:
        print(f"\n{len(fatal)} 项失败:")
        for f in fatal:
            print("FAIL:", f)
        return 1
    print("E2E 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())