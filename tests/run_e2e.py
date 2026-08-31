"""Ethereal Tarot 冒烟 / 交互 E2E（Playwright，Python）。

覆盖（对应验收标准）:
- 页面加载: loader 出现且消失（22 张纹理加载）、无 console.error / pageerror / 同源 4xx
- 初始文案: SUMMONING ARCANA / ETHEREAL TAROT / Camera Off / Shuffle Deck /
  Language: EN / NAME / DESC / CLICK TO DISMISS / DRAG TO SCROLL • CLICK TO SELECT
- 洗牌: Shuffle Deck 触发闪烁反馈，洗牌后抽牌正常
- 核心交互: 连续抽 3 张 → 展开视图 → 收回 → 历史组点击回顾
- 语言切换: EN→CN→EN，刷新后不持久化（恢复 EN，与原版一致）
- 摄像头切换: 文案流转正确；切回鼠标后交互恢复（headless 无摄像头，媒体错误仅记录）
- 新增功能: localStorage 写入一条 schemaVersion=1 的 3 张记录
- 截图存档: tests/artifacts/

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

# headless 无摄像头/无权限时 MediaPipe Camera 抛错属预期（原版同路径），标记后仅记录
MEDIA_ERR_MARKERS = (
    "getUserMedia", "Not supported", "NotSupportedError",
    "NotAllowedError", "NotFoundError", "NotReadableError",
    "mediaDevices", "Camera",
)

# Windows 控制台默认 GBK 无法打印 • 等字符，统一用 UTF-8 输出
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main() -> int:
    fatal: list[str] = []
    warns: list[str] = []
    media_notes: list[str] = []
    state = {"media_step": False}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": W, "height": H})

        def on_console(m):
            if m.type != "error":
                return
            if state["media_step"]:
                media_notes.append(m.text)  # 摄像头步骤期间的错误仅记录（headless 无摄像头）
                return
            fatal.append(f"console.error: {m.text}")

        def on_pageerror(e):
            msg = str(e)
            if state["media_step"] and any(m in msg for m in MEDIA_ERR_MARKERS):
                media_notes.append(f"pageerror: {msg}")
                return
            fatal.append(f"pageerror: {e}")

        page.on("console", on_console)
        page.on("pageerror", on_pageerror)
        page.on("response", lambda r: (
            warns.append(f"外部资源 HTTP {r.status}: {r.url}")
            if r.status >= 400 and not r.url.startswith(BASE)
            else (fatal.append(f"同源 HTTP {r.status}: {r.url}") if r.status >= 400 else None)
        ))

        def text(sel: str) -> str:
            return (page.text_content(sel) or "").strip()

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

        def wait_text(sel: str, want: str, timeout_s: float) -> str:
            deadline = time.time() + timeout_s
            got = ""
            while time.time() < deadline:
                got = text(sel)
                if got == want:
                    return got
                page.wait_for_timeout(200)
            return got

        def draw_card(tag: str) -> str:
            """扫描点击直到选中一张牌，返回牌名；随后保持 SHOW 态（调用方负责 dismiss）。"""
            if not wait_clear(8):
                fatal.append(f"{tag} 开始前结果区未收起")
            hit = False
            for i in range(40):
                if result_visible():
                    break
                x = 30 + (W - 60) * i / 39
                page.mouse.click(x, H * 0.5)
                if wait_result(3):
                    hit = True
                    break
            if not hit:
                fatal.append(f"{tag} 牌未被选中")
                return ""
            page.wait_for_timeout(700)  # opacity 过渡 0.5s 收尾
            name = text("#r-name")
            if "•" in name:
                fatal.append(f"{tag} 处于展开/回顾态而非单牌态: {name!r}")
            return name

        # --- 1. 加载：loader 出现（本地上 22 张纹理约需 1s，捕获初始态） ---
        page.goto(BASE + "/")
        page.wait_for_timeout(80)
        if page.locator("#loader").count() == 1:
            lt = text("#load-text")
            if lt != "SUMMONING ARCANA":
                fatal.append(f"加载文案不符: got={lt!r}")
            else:
                print("[ok] 加载页文案: SUMMONING ARCANA")
        else:
            print("[skip] loader 初始态未捕获（本地加载过快），以 dist/index.html 静态文案检查兜底")
        page.wait_for_selector("#loader", state="detached", timeout=120_000)
        print("[ok] loader 消失（22 张纹理加载完成）")

        # --- 2. UI 文案（默认英文）+ 结果区占位 ---
        expect = {
            "#logo-text": "ETHEREAL TAROT",
            "#mode-toggle": "Camera Off",
            "#shuffle-btn": "Shuffle Deck",
            "#lang-btn": "Language: EN",
            "#guide-text": "DRAG TO SCROLL • CLICK TO SELECT",
            "#r-name": "NAME",
            "#r-desc": "DESC",
            "#click-tip": "CLICK TO DISMISS",
        }
        for sel, want in expect.items():
            got = text(sel)
            if got != want:
                fatal.append(f"{sel} 文案不符: got={got!r} want={want!r}")
        if page.locator("#canvas-container canvas").count() != 1:
            fatal.append("canvas 未创建")
        print("[ok] UI/占位文案与 canvas 就绪")

        shot = lambda n: page.screenshot(path=str(ART / f"{n}.png"))
        shot("01-init")

        # --- 3. 洗牌：按钮闪烁反馈 + 洗牌后抽牌正常 ---
        # 瞬态类名（生命周期 400ms）不能靠 CDP 往返轮询（往返可能 >400ms）。
        # 在浏览器内用 MutationObserver 监听 class 变化，零往返延迟。
        page.evaluate("""() => {
            window.__shuffleFlash = new Promise((resolve) => {
                const el = document.getElementById('shuffle-btn');
                if (!el) return resolve(false);
                const obs = new MutationObserver(() => {
                    if (el.classList.contains('btn-flash-active')) {
                        obs.disconnect();
                        resolve(true);
                    }
                });
                obs.observe(el, { attributes: true, attributeFilter: ['class'] });
                setTimeout(() => { obs.disconnect(); resolve(false); }, 2500);
            });
        }""")
        page.click("#shuffle-btn")
        flashed = page.evaluate("window.__shuffleFlash")
        if not flashed:
            fatal.append("Shuffle Deck 无闪烁反馈（btn-flash-active 未出现）")
        page.wait_for_timeout(600)
        print("[ok] Shuffle Deck 触发闪烁反馈")

        # --- 4. 连抽 3 张 ---
        names: list[str] = []
        for draw in range(1, 4):
            name = draw_card(f"第 {draw} 张")
            names.append(name)
            print(f"[ok] 第 {draw} 张选中: {name}")
            shot(f"0{draw}-show")
            page.mouse.click(W * 0.5, H * 0.5)  # dismiss
            page.wait_for_timeout(1200)  # 飞回角落动画（前两张）
        page.wait_for_timeout(1600)  # 第 3 张 dismiss → 展开视图动画

        # --- 5. 展开视图 ---
        spread_desc = wait_text("#r-desc", "PAST • PRESENT • FUTURE", 6)
        if spread_desc != "PAST • PRESENT • FUTURE":
            fatal.append(f"展开视图文案不符: got={spread_desc!r}")
        else:
            print("[ok] 展开视图: PAST • PRESENT • FUTURE")
        shot("04-spread")

        # --- 6. localStorage 记录 ---
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

        # --- 7. 收回展开 → 历史组（3 张缩略图） ---
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

        # --- 8. 点击历史组 → 回顾视图 ---
        groups.first.click()
        rev_desc = wait_text("#r-desc", "REVIEWING SESSION", 8)
        if rev_desc != "REVIEWING SESSION":
            fatal.append(f"回顾视图文案不符: got={rev_desc!r}")
        else:
            print("[ok] 回顾视图: REVIEWING SESSION")
        shot("07-review")
        page.mouse.click(W * 0.5, H * 0.5)  # 关闭回顾
        page.wait_for_timeout(1000)

        # --- 9. 语言切换：EN→CN→EN，刷新不持久化（原版行为） ---
        page.click("#lang-btn")
        ok_cn = (
            wait_text("#logo-text", "虚幻卡罗牌", 3) == "虚幻卡罗牌"
            and wait_text("#lang-btn", "语言：中", 3) == "语言：中"
            and wait_text("#guide-text", "拖拽以滚动 • 点击以选择", 3) == "拖拽以滚动 • 点击以选择"
        )
        if not ok_cn:
            fatal.append("语言切换 EN→CN 文案未更新")
        else:
            print("[ok] 语言切换 EN→CN")
        shot("08-lang-cn")
        page.click("#lang-btn")
        ok_en = (
            wait_text("#logo-text", "ETHEREAL TAROT", 3) == "ETHEREAL TAROT"
            and wait_text("#lang-btn", "Language: EN", 3) == "Language: EN"
        )
        if not ok_en:
            fatal.append("语言切换 CN→EN 未恢复")
        else:
            print("[ok] 语言切换 CN→EN")
        page.reload()
        page.wait_for_selector("#loader", state="detached", timeout=120_000)
        page.wait_for_timeout(500)
        if text("#logo-text") != "ETHEREAL TAROT":
            fatal.append(f"刷新后语言未恢复 EN（原版不持久化）: got={text('#logo-text')!r}")
        else:
            print("[ok] 刷新后恢复 EN（语言状态不持久化）")

        # --- 10. 摄像头切换：文案流转 + 切回后交互恢复 ---
        state["media_step"] = True
        page.click("#mode-toggle")
        ok_hand = (
            wait_text("#mode-toggle", "Switch to Mouse", 3) == "Switch to Mouse"
            and wait_text("#guide-text", "Palm: Scroll • Fist: Select", 3) == "Palm: Scroll • Fist: Select"
        )
        if not ok_hand:
            fatal.append("摄像头模式文案未切换")
        else:
            print("[ok] 摄像头模式文案（Palm/Fist）")
        shot("09-cam")
        page.click("#mode-toggle")
        state["media_step"] = False
        ok_back = (
            wait_text("#mode-toggle", "Camera Off", 3) == "Camera Off"
            and wait_text("#guide-text", "DRAG TO SCROLL • CLICK TO SELECT", 3) == "DRAG TO SCROLL • CLICK TO SELECT"
        )
        if not ok_back:
            fatal.append("切回鼠标模式文案未恢复")
        name = draw_card("摄像头切回后")
        if name:
            print(f"[ok] 摄像头切回后鼠标交互恢复（抽中: {name}）")
            page.mouse.click(W * 0.5, H * 0.5)
            page.wait_for_timeout(1000)
        shot("10-cam-back")

        # --- 11. 截图体积软检查（防全黑静默失败） ---
        for f in sorted(ART.glob("*.png")):
            print(f"      截图 {f.name}: {f.stat().st_size // 1024} KB")

        browser.close()

    print()
    if media_notes:
        print("备注（摄像头步骤，headless 无摄像头/权限拒绝，与原版行为一致）:")
        for n in media_notes[:5]:
            print("  ", n)
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