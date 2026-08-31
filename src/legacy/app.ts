// 原 src/index.html 内联 <script type="module"> 的整体搬运区（不拆分、不重写）。
// 改动点（仅此四处，其余均为原样搬运）：
//   1. three 及插件改为从 npm 包解析（版本仍为 0.160.0，与原 CDN 完全一致）
//   2. 数据/文案/资源配置抽到 src/data、src/i18n、src/config/assets.ts
//   3. 新增抽牌记录保存（src/services/records.ts），仅在 3 张抽牌完成时写入
//   4. 类型化（2026-09-01 移除 @ts-nocheck）：显式类型/受控断言，运行时语义不变
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { TAROT_EN, TAROT_CN } from '../data/cards';
import { UI_TEXT } from '../i18n';
import { IMG_URL, BACK_URL } from '../config/assets';
import { saveDrawSession } from '../services/records';

// 当前语言设置
let curLang: 'en' | 'cn' = 'en';

// --- 三维场景与渲染 ---
// 初始化 scene、camera、renderer 与灯光
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x050505);
scene.fog = new THREE.FogExp2(0x050505, 0.015);

const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 16);

const renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: "high-performance" });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
container.appendChild(renderer.domElement);

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
bloom.threshold = 0.2; bloom.strength = 0.5; bloom.radius = 0.5;
composer.addPass(bloom);
composer.addPass(new OutputPass());

const ambLight = new THREE.AmbientLight(0xffffff, 1.0);
scene.add(ambLight);

const topLight = new THREE.SpotLight(0xffd700, 8);
topLight.position.set(0, 15, 5);
topLight.angle = 0.6; topLight.penumbra = 0.5;
scene.add(topLight);

const frontLight = new THREE.PointLight(0xffeedd, 0.8, 30);
frontLight.position.set(0, 2, 15);
scene.add(frontLight);

scene.add(new THREE.PointLight(0x4466ff, 3.0, 25).translateY(0).translateX(-10).translateZ(-5));
scene.add(new THREE.PointLight(0x4466ff, 3.0, 25).translateY(0).translateX(10).translateZ(-5));

// --- 全局状态对象 ---
interface CardState { id: number; isRev: boolean; }
interface AppState {
    mode: 'MOUSE' | 'HAND';
    cards: THREE.Mesh[];
    data: CardState[];
    activeCards: number[];
    discardPile: THREE.Mesh[];
    offset: number; velocity: number;
    phase: string;
    selected: THREE.Mesh | null;
    handX: number; handY: number; targetHandX: number; targetHandY: number; isHandVisible: boolean;
    isFist: boolean; fistFrames: number;
    isDrag: boolean; lastX: number; startX: number; startY: number;
    mousePos: THREE.Vector2;
    raycaster: THREE.Raycaster;
    isHoveringUI: boolean;
}
const STATE: AppState = {
    mode: 'MOUSE',
    cards: [], data: [], activeCards: [], discardPile: [],
    offset: 0, velocity: 0,
    phase: 'INTRO',
    selected: null,
    handX: 0.5, handY: 0.5, targetHandX: 0.5, targetHandY: 0.5, isHandVisible: false,
    isFist: false, fistFrames: 0,
    isDrag: false, lastX: 0, startX: 0, startY: 0,
    mousePos: new THREE.Vector2(),
    raycaster: new THREE.Raycaster(),
    isHoveringUI: false
};
// 纹理加载器
const TEX_LOADER = new THREE.TextureLoader();

// --- 辅助函数 ---
function getScreenBounds() {
    const vFOV = THREE.MathUtils.degToRad(camera.fov);
    const height = 2 * Math.tan(vFOV / 2) * camera.position.z;
    const width = height * camera.aspect;
    return { left: -width / 2, bottom: -height / 2 };
}

// --- 语言与UI文本更新 ---
function getTarotData(id) {
    return curLang === 'en' ? TAROT_EN[id] : TAROT_CN[id];
}

function getText() {
    return UI_TEXT[curLang];
}

function updateUIText() {
    const T = getText();
    document.getElementById('logo-text').innerText = T.logo;
    document.getElementById('shuffle-btn').innerText = T.shuffle;
    document.getElementById('lang-btn').innerText = T.langLabel;

    const modeToggle = document.getElementById('mode-toggle');
    modeToggle.innerText = STATE.mode === 'MOUSE' ? T.camOff : T.camOn;

    const guide = document.getElementById('guide-text');
    guide.innerText = STATE.mode === 'MOUSE' ? T.guideMouse : T.guideHand;

    const loadText = document.querySelector<HTMLElement>('.load-text');
    if (loadText) loadText.innerText = T.loading;

    // 如果当前正在展示卡牌结果，更新结果文字
    if (STATE.phase === 'SHOW' && STATE.selected) {
        const id = STATE.selected.userData.id;
        const d = getTarotData(id);
        const isRev = STATE.data[id].isRev; // Use stored rev state
        document.getElementById('r-name').innerText = d.n;
        document.getElementById('r-desc').innerHTML = `<strong>${isRev ? T.rev : T.upr}</strong> ${isRev ? d.r : d.u}`;
        document.getElementById('click-tip').innerText = STATE.mode === 'HAND' ? T.clickTipHand : T.clickTip;
    } else if (STATE.phase === 'SPREAD_VIEW') {
        const names = STATE.discardPile.map(mesh => {
            const d = getTarotData(mesh.userData.id);
            const isRev = STATE.data[mesh.userData.id].isRev;
            return isRev ? `${d.n} (${T.revShort})` : d.n;
        });
        document.getElementById('r-name').innerText = names.join("  •  ");
        document.getElementById('r-desc').innerHTML = T.spreadDesc;
        document.getElementById('click-tip').innerText = STATE.mode === 'HAND' ? T.spreadTipHand : T.spreadTip;
    } else if (STATE.phase === 'REVIEW_VIEW') {
        // 重新计算名字串，因为语言变了
        const hBox = document.getElementById('history-box');
        // 找到最近的组
        const groups = hBox.querySelectorAll('.h-group');
        if (groups.length > 0) {
            const snapshots = groups[0].userData.snapshots;
            const names = snapshots.map(s => {
                const d = getTarotData(s.id);
                return s.isRev ? `${d.n} (${T.revShort})` : d.n;
            });
            document.getElementById('r-name').innerText = names.join("  •  ");
        }
        document.getElementById('r-desc').innerHTML = T.reviewDesc;
        document.getElementById('click-tip').innerText = T.reviewTip;
    }
}

const langBtn = document.getElementById('lang-btn');
langBtn.onclick = () => {
    // 1. Toggle Language
    curLang = curLang === 'en' ? 'cn' : 'en';
    document.body.classList.toggle('lang-cn', curLang === 'cn');

    // 2. Full Reset Logic ("Like just opened")
    // A. Reset UI elements
    document.getElementById('result-area').style.opacity = "0";
    const hBox = document.getElementById('history-box');

    // B. Clean up 3D clones in history before clearing DOM
    const groups = hBox.querySelectorAll('.h-group');
    groups.forEach(g => {
        if (g.userData && g.userData.clones) {
            g.userData.clones.forEach(c => {
                scene.remove(c);
                if (c.geometry) c.geometry.dispose();
            });
        }
    });
    hBox.innerHTML = ''; // Clear history DOM

    // C. Reset internal state
    STATE.discardPile = [];
    STATE.activeCards = []; // performShuffleAndSpin will repopulate this
    STATE.selected = null;
    STATE.phase = 'IDLE';
    STATE.velocity = Math.random() * 2.5 + 2.5;

    // D. Reset Card Orientations (re-randomize upright/reversed for a fresh deck feel)
    STATE.cards.forEach(m => {
        const isRev = Math.random() > 0.5;
        STATE.data[m.userData.id].isRev = isRev;
        m.visible = true; // Make sure they are visible
    });

    // E. Reset Input Mode to Mouse (to be strictly "like just opened")
    if (STATE.mode === 'HAND') {
        // Manually trigger click to reset UI and stop camera
        document.getElementById('mode-toggle').click();
    }

    // F. Update Text & Reshuffle positions
    updateUIText();
    performShuffleAndSpin();

    // Flash effect for the button
    langBtn.classList.add('btn-flash-active');
    setTimeout(() => { langBtn.classList.remove('btn-flash-active'); }, 400);
};

// --- 卡片生成 ---
function createCard(tex, i, isRev) {
    const geo = new THREE.BoxGeometry(2.6, 4.4, 0.03);
    tex.colorSpace = THREE.SRGBColorSpace;
    const matSide = new THREE.MeshStandardMaterial({ color: 0x000000, roughness: 1.0, metalness: 0.0 });
    const matFace = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.4, metalness: 0.1, emissive: 0x111111 });
    let backTex = TEX_LOADER.load(BACK_URL);
    backTex.colorSpace = THREE.SRGBColorSpace;
    const matBack = new THREE.MeshStandardMaterial({
        map: backTex, color: 0xffffff, roughness: 0.4, metalness: 0.3,
        emissive: 0xffeebb, emissiveMap: backTex, emissiveIntensity: 1.0
    });
    const mesh = new THREE.Mesh(geo, [matSide, matSide, matSide, matSide, matBack, matFace]);
    mesh.rotation.z = isRev ? Math.PI : 0;
    mesh.userData = { id: i, originalIndex: i, isRev, seed: Math.random() };
    mesh.position.set(0, 0, -30);
    scene.add(mesh);
    STATE.cards[i] = mesh;
}

// --- 占位纹理生成 ---
function getFallbackTexture(text) {
    const cvs = document.createElement('canvas'); cvs.width = 512; cvs.height = 800;
    const ctx = cvs.getContext('2d');
    const grd = ctx.createRadialGradient(256, 400, 0, 256, 400, 400);
    grd.addColorStop(0, '#2b2b2b'); grd.addColorStop(1, '#000000');
    ctx.fillStyle = grd; ctx.fillRect(0, 0, 512, 800);
    ctx.strokeStyle = '#d4af37'; ctx.lineWidth = 15; ctx.strokeRect(30, 30, 452, 740);
    ctx.fillStyle = '#F9EDC3'; ctx.font = 'bold 60px serif'; ctx.textAlign = 'center';
    ctx.fillText(text.toUpperCase(), 256, 400);
    return new THREE.CanvasTexture(cvs);
}

// --- 牌组初始化 ---
function initDeck() {
    const indices = Array.from({ length: 22 }, (_, i) => i);
    let loaded = 0;
    indices.forEach((id, idx) => {
        // Initialize with EN data structure for IDs, text fetched dynamically later
        const d = TAROT_EN[id];
        const isRev = Math.random() > 0.5;
        STATE.data[idx] = { id: d.id, isRev }; // Only store ID and State
        TEX_LOADER.load(
            IMG_URL + (d.id) + ".jpg",
            (t) => { createCard(t, idx, isRev); checkLoad(); },
            undefined,
            () => { createCard(getFallbackTexture(d.n), idx, isRev); checkLoad(); }
        );
    });

    function checkLoad() {
        loaded++;
        if (loaded === 22) {
            const l = document.getElementById('loader');
            if (l) { l.style.opacity = "0"; setTimeout(() => l.remove(), 1000); }
            performShuffleAndSpin();
        }
    }
}

// --- 洗牌与重置 ---
function performShuffleAndSpin() {
    STATE.cards.forEach(m => {
        m.position.set(0, 0, -30); m.rotation.set(0, 0, 0); m.scale.setScalar(1.1);
        m.visible = true; // 确保重新洗牌后所有原牌可见
    });
    STATE.activeCards = Array.from({ length: 22 }, (_, i) => i);
    STATE.discardPile = [];
    STATE.selected = null;
    STATE.activeCards.sort(() => Math.random() - 0.5);
    STATE.phase = 'IDLE';
    STATE.velocity = Math.random() * 2.5 + 2.5;
    const T = getText();
    const tip = document.getElementById('click-tip');
    tip.innerText = STATE.mode === 'HAND' ? T.clickTipHand : T.clickTip;
}

// --- 动画与更新循环 ---
function update(dt) {
    if (STATE.isHoveringUI) { STATE.velocity = 0; }
    if (STATE.phase !== 'IDLE' && STATE.phase !== 'SCROLL') return;
    if (STATE.mode === 'HAND') {
        const diff = STATE.handX - 0.5;
        if (Math.abs(diff) > 0.1) STATE.velocity += (diff > 0 ? 1 : -1) * (Math.abs(diff) - 0.1) * 0.1;
        STATE.mousePos.set(STATE.handX * 2 - 1, -(0.5 * 2 - 1));
    }
    STATE.velocity *= 0.95;
    if (Math.abs(STATE.velocity) < 0.0005 && STATE.mode === 'MOUSE') STATE.velocity = 0;
    STATE.offset -= STATE.velocity;

    const SPACING = 5.5;
    const count = STATE.activeCards.length;
    if (count === 0) return;
    const TOTAL_WIDTH = count * SPACING;

    STATE.raycaster.setFromCamera(STATE.mousePos, camera);
    const activeMeshes = STATE.activeCards.map(id => STATE.cards[id]);
    const intersects = STATE.raycaster.intersectObjects(activeMeshes);
    const hoveredMesh = intersects.length > 0 ? intersects[0].object : null;

    STATE.activeCards.forEach((idx, i) => {
        const m = STATE.cards[idx];
        if (STATE.phase === 'FLYING' || m === STATE.selected) return;

        let x = i * SPACING + STATE.offset;
        const half = TOTAL_WIDTH / 2;
        while (x > half) x -= TOTAL_WIDTH;
        while (x < -half) x += TOTAL_WIDTH;

        const dist = Math.abs(x);
        let targetZ = -Math.pow(dist / 1.8, 1.15);
        targetZ = Math.max(targetZ, -40);

        if (hoveredMesh === m && Math.abs(x) < 8.0) targetZ += 1;

        const maxAngle = Math.PI / 1.7;
        const transition = x / 4.0;
        const targetRotY = -(transition / Math.sqrt(1 + transition * transition)) * maxAngle;

        if (Math.abs(x - m.position.x) > SPACING * 3) {
            m.position.x = x;
            m.rotation.y = targetRotY;
        } else {
            m.position.x += (x - m.position.x) * 0.12;
        }
        m.position.y += (Math.sin(dt * 2 + i) * 0.15 - m.position.y) * 0.1;
        m.position.z += (targetZ - m.position.z) * 0.1;

        let currentRotY = m.rotation.y;
        let diffY = targetRotY - currentRotY;
        while (diffY < -Math.PI) diffY += Math.PI * 2;
        while (diffY > Math.PI) diffY -= Math.PI * 2;
        m.rotation.y += diffY * 0.05;

        const d = STATE.data[m.userData.id];
        const targetRotZ = d.isRev ? Math.PI : 0;
        let diffZ = targetRotZ - m.rotation.z;
        while (diffZ < -Math.PI) diffZ += Math.PI * 2;
        while (diffZ > Math.PI) diffZ -= Math.PI * 2;
        m.rotation.z += diffZ * 0.03;

        m.rotation.x *= 0.9;
        const baseScale = 1.1;
        m.scale.setScalar(dist < 2.0 ? baseScale + (2.0 - dist) * 0.11 : baseScale);
    });
}

// --- 选择与翻牌逻辑 ---
function selectCard(clientX, clientY) {
    if (STATE.activeCards.length === 0) return;
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    if (clientX !== undefined && clientY !== undefined) {
        mouse.x = (clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(clientY / window.innerHeight) * 2 + 1;
    } else { mouse.x = 0; mouse.y = 0; }

    raycaster.setFromCamera(mouse, camera);
    const activeMeshes = STATE.activeCards.map(id => STATE.cards[id]);
    const intersects = raycaster.intersectObjects(activeMeshes);

    if (intersects.length > 0) {
        const m = intersects[0].object;
        if (Math.abs(m.position.x) > 8.0) return;

        STATE.phase = 'FLIP'; STATE.selected = m;
        const d = STATE.data[m.userData.id]; // get state (isRev, id)

        // 简短：对当前 Z 角度做数值归一化以避免累积圈数
        const targetZ = d.isRev ? Math.PI : 0;
        const diffZ = m.rotation.z - targetZ;
        const turns = Math.round(diffZ / (Math.PI * 2));
        m.rotation.z -= turns * Math.PI * 2;

        const startP = m.position.clone();
        const startR = m.rotation.clone(); // 现在这里克隆的是净化后的角度
        const endP = new THREE.Vector3(0, 0, 8);

        let p = 0;
        function flip() {
            p += 0.02; const ease = 1 - Math.pow(1 - p, 3);
            m.position.lerpVectors(startP, endP, ease);

            // Y轴：左右翻转 (从当前角度转到 PI)
            m.rotation.y = THREE.MathUtils.lerp(startR.y, Math.PI, ease);

            // Z轴：正逆位调整 (因为上面已经净化过数据，这里几乎不会产生视觉旋转，或者只是微调)
            m.rotation.z = THREE.MathUtils.lerp(startR.z, targetZ, ease);

            // X轴：修正倾斜 (归零，防止看起来像跟头)
            m.rotation.x = THREE.MathUtils.lerp(startR.x, 0, ease);

            if (p < 1) requestAnimationFrame(flip);
            else { STATE.phase = 'SHOW'; showUI(d); }
        }
        flip();
    }
}

// --- 收牌逻辑 ---
function dismiss() {
    if (!STATE.selected || STATE.phase === 'FLYING') return;
    document.getElementById('result-area').style.opacity = "0";
    const m = STATE.selected;
    STATE.discardPile.push(m);
    STATE.activeCards = STATE.activeCards.filter(id => id !== m.userData.id);
    if (STATE.discardPile.length >= 3) {
        // 新增：一次完整 3 张抽牌完成，保存记录（只写 localStorage，不影响 UI）
        saveDrawSession({
            language: curLang,
            mode: STATE.mode,
            cards: STATE.discardPile.map(mesh => ({
                id: mesh.userData.id,
                isRev: STATE.data[mesh.userData.id].isRev
            }))
        });
        flyToSpreadView();
    } else {
        STATE.phase = 'FLYING';
        flyToCorner(m, STATE.discardPile.length - 1);
    }
}

// --- 飞回角落动画 ---
function flyToCorner(m, stackIdx) {
    const bounds = getScreenBounds();
    const targetX = bounds.left + 1.0 + (stackIdx * 1.4);
    const targetY = bounds.bottom + 1.4;
    const startP = m.position.clone(); const startS = m.scale.x;
    const startR = m.rotation.clone();
    let p = 0;
    function anim() {
        p += 0.05; const ease = p * p;
        m.position.x = THREE.MathUtils.lerp(startP.x, targetX, ease);
        m.position.y = THREE.MathUtils.lerp(startP.y, targetY, ease);
        m.position.z = THREE.MathUtils.lerp(startP.z, 0, ease);
        m.rotation.x = THREE.MathUtils.lerp(startR.x, 0, ease);
        m.rotation.y = THREE.MathUtils.lerp(startR.y, Math.PI, ease);
        m.scale.setScalar(THREE.MathUtils.lerp(startS, 0.35, ease));
        if (p < 1) requestAnimationFrame(anim);
        else {
            if (STATE.phase === 'FLYING') {
                STATE.selected = null; STATE.phase = 'IDLE'; STATE.velocity = Math.random() * 2.5 + 2.5;
            }
        }
    }
    anim();
}

// --- 展开阅读视图 ---
function flyToSpreadView() {
    STATE.phase = 'SPREAD_VIEW';
    STATE.selected = null;
    const T = getText();
    const names = STATE.discardPile.map(mesh => {
        const cardState = STATE.data[mesh.userData.id];
        const d = getTarotData(mesh.userData.id);
        return cardState.isRev ? `${d.n} (${T.revShort})` : d.n;
    });
    const targets = [{ x: -4.5, y: 0, z: 5 }, { x: 0.0, y: 0, z: 5 }, { x: 4.5, y: 0, z: 5 }];
    const starts = STATE.discardPile.map(mesh => ({ p: mesh.position.clone(), r: mesh.rotation.clone(), s: mesh.scale.x }));
    let p = 0;
    function anim() {
        p += 0.02; const ease = 1 - Math.pow(1 - p, 3);
        STATE.discardPile.forEach((mesh, i) => {
            mesh.position.set(
                THREE.MathUtils.lerp(starts[i].p.x, targets[i].x, ease),
                THREE.MathUtils.lerp(starts[i].p.y, targets[i].y, ease),
                THREE.MathUtils.lerp(starts[i].p.z, targets[i].z, ease)
            );
            const d = STATE.data[mesh.userData.id];
            const targetZ = d.isRev ? Math.PI : 0;
            mesh.rotation.set(
                THREE.MathUtils.lerp(starts[i].r.x, 0, ease),
                THREE.MathUtils.lerp(starts[i].r.y, Math.PI, ease),
                THREE.MathUtils.lerp(starts[i].r.z, targetZ, ease)
            );
            mesh.scale.setScalar(THREE.MathUtils.lerp(starts[i].s, 1.2, ease));
        });
        if (p < 1) requestAnimationFrame(anim);
        else {
            document.getElementById('r-name').innerText = names.join("  •  ");
            document.getElementById('r-desc').innerHTML = T.spreadDesc;
            document.getElementById('click-tip').innerText = STATE.mode === 'HAND' ? T.spreadTipHand : T.spreadTip;
            document.getElementById('result-area').style.opacity = "1";
        }
    }
    anim();
}

// --- 收回展开并恢复牌组 ---
function resetSpread() {
    if (STATE.phase !== 'SPREAD_VIEW') return;
    STATE.phase = 'FLYING';
    document.getElementById('result-area').style.opacity = "0";

    // 获取当前历史组，以便我们将牌替换为副本
    const hBox = document.getElementById('history-box');
    const targetGroup = hBox.querySelector('.h-group');

    const starts = STATE.discardPile.map(m => ({ p: m.position.clone(), r: m.rotation.clone(), s: m.scale.x }));
    let p = 0;
    function anim() {
        p += 0.04; const ease = 1 - Math.pow(1 - p, 3);
        STATE.discardPile.forEach((m, i) => {
            m.position.lerpVectors(starts[i].p, new THREE.Vector3(0, 0, -20), ease);
            m.rotation.x = THREE.MathUtils.lerp(starts[i].r.x, 0, ease);
            m.rotation.y = THREE.MathUtils.lerp(starts[i].r.y, 0, ease);
            m.rotation.z = THREE.MathUtils.lerp(starts[i].r.z, 0, ease);
            m.scale.setScalar(THREE.MathUtils.lerp(starts[i].s, 0.8, ease));
        });
        if (p < 1) requestAnimationFrame(anim);
        else {
            // 简短：收回时隐藏原牌（历史使用克隆）
            STATE.discardPile.forEach((m, i) => { m.visible = false; });
            performShuffleAndSpin();
        }
    }
    anim();
}

// --- 显示结果并记录历史 ---
function showUI(dataState) {
    const T = getText();
    const d = getTarotData(dataState.id);
    const isRev = dataState.isRev;

    document.getElementById('r-name').innerText = d.n;
    document.getElementById('r-desc').innerHTML = `<strong>${isRev ? T.rev : T.upr}</strong> ${isRev ? d.r : d.u}`;
    document.getElementById('result-area').style.opacity = "1";

    const hBox = document.getElementById('history-box');
    const currentCount = STATE.discardPile.length;
    let targetGroup;

    if (currentCount === 0) {
        targetGroup = document.createElement('div');
        targetGroup.className = 'h-group';
        targetGroup.id = 'latest-group-' + Date.now();
        targetGroup.userData = { clones: [], snapshots: [] };
        targetGroup.innerHTML = `<div class="h-group-title">${T.historyTitle}</div>`;
        targetGroup.onclick = (e) => {
            e.stopPropagation();
            if (targetGroup.userData.clones.length === 3 && STATE.phase !== 'REVIEW_VIEW') {
                showReviewSpread(targetGroup);
            }
        };
        hBox.prepend(targetGroup);
    } else {
        targetGroup = hBox.querySelector('.h-group');
    }

    // 克隆当前卡牌并加入历史（原牌保留或隐藏）
    const originalMesh = STATE.selected;
    const clone = originalMesh.clone();
    clone.visible = false; // 初始不可见，只在查看历史时显示
    scene.add(clone);

    targetGroup.userData.clones.push(clone);
    targetGroup.userData.snapshots.push({
        isRev: isRev,
        n: d.n, id: d.id // Store ID so we can translate later if needed
    });

    if (targetGroup.userData.clones.length === 3) targetGroup.style.cursor = 'pointer';

    const div = document.createElement('div');
    div.className = 'h-item';
    div.style.alignItems = 'center'; div.style.gap = '10px';
    const thumbUrl = `${IMG_URL}${d.id}.jpg`;
    div.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px;">
            <div class="h-thumb" style="background-image: url('${thumbUrl}'); ${isRev ? 'transform: rotate(180deg);' : ''}"></div>
            <div>
                <small style="color:#666; font-size:0.6rem;">${T.posNames[currentCount] || T.defaultArcana}</small>
                <div style="font-size:0.9rem;"><span>${isRev ? T.revShort : T.uprShort}</span> ${d.n}</div>
            </div>
        </div>
    `;
    targetGroup.appendChild(div);
    requestAnimationFrame(() => hBox.scrollTo({ top: 0, behavior: 'smooth' }));
}

// --- 历史回顾视图 ---
function showReviewSpread(targetGroup) {
    const T = getText();
    const clones = targetGroup.userData.clones;
    const snapshots = targetGroup.userData.snapshots;
    const bounds = getScreenBounds();

    STATE.phase = 'REVIEW_VIEW';
    STATE.selected = null;

    const names = snapshots.map(s => {
        const d = getTarotData(s.id);
        return s.isRev ? `${d.n} (${T.revShort})` : d.n;
    });
    const targets = [{ x: -4.5, y: 0, z: 5 }, { x: 0, y: 0, z: 5 }, { x: 4.5, y: 0, z: 5 }];

    clones.forEach((c, i) => {
        c.visible = true;
        // 将克隆体位置重置到左下角暂存区，准备起飞
        c.position.set(bounds.left + 1.8 + (i * 1.4), bounds.bottom + 1.5, 0);
        c.scale.setScalar(0.35);
        c.rotation.set(0, Math.PI, snapshots[i].isRev ? Math.PI : 0);
    });

    const starts = clones.map(c => ({ p: c.position.clone(), r: c.rotation.clone(), s: c.scale.x }));
    let p = 0;
    function anim() {
        p += 0.03; const ease = 1 - Math.pow(1 - p, 3);
        clones.forEach((c, i) => {
            c.position.lerpVectors(starts[i].p, new THREE.Vector3(targets[i].x, targets[i].y, targets[i].z), ease);
            const snapIsRev = snapshots[i].isRev;
            c.rotation.y = THREE.MathUtils.lerp(starts[i].r.y, Math.PI, ease);
            c.rotation.z = THREE.MathUtils.lerp(starts[i].r.z, snapIsRev ? Math.PI : 0, ease);
            c.scale.setScalar(THREE.MathUtils.lerp(starts[i].s, 1.2, ease));
        });
        if (p < 1) requestAnimationFrame(anim);
        else {
            document.getElementById('r-name').innerText = names.join("  •  ");
            document.getElementById('r-desc').innerHTML = T.reviewDesc;
            document.getElementById('click-tip').innerText = T.reviewTip;
            document.getElementById('result-area').style.opacity = "1";
        }
    }
    anim();
}

// --- UI 事件：按钮处理 ---
const shuffleBtn = document.getElementById('shuffle-btn');
shuffleBtn.onclick = () => {
    if (STATE.phase === 'SHOW') dismiss();
    if (STATE.phase === 'SPREAD_VIEW') resetSpread();
    STATE.velocity = Math.random() * 2.5 + 1.5;
    STATE.activeCards.forEach(idx => {
        const m = STATE.cards[idx];
        STATE.data[m.userData.id].isRev = Math.random() > 0.5;
        const dir = Math.random() > 0.5 ? 1 : -1;
        m.rotation.z = dir * (Math.random() * 1.5 + 3.5) * Math.PI * 2;
    });
    STATE.activeCards.sort(() => Math.random() - 0.5);
    shuffleBtn.classList.add('btn-flash-active');
    setTimeout(() => { shuffleBtn.classList.remove('btn-flash-active'); }, 400);
};

// --- 鼠标交互 ---
window.addEventListener('mousedown', e => {
    if (STATE.mode === 'MOUSE') {
        STATE.isDrag = true; STATE.lastX = e.clientX; STATE.startX = e.clientX; STATE.startY = e.clientY;
    }
});
window.addEventListener('mouseup', () => STATE.isDrag = false);
window.addEventListener('mousemove', e => {
    if (STATE.mode === 'MOUSE') {
        STATE.mousePos.x = (e.clientX / window.innerWidth) * 2 - 1;
        STATE.mousePos.y = -(e.clientY / window.innerHeight) * 2 + 1;
        if (STATE.isDrag && !STATE.isHoveringUI) {
            const dx = e.clientX - STATE.lastX; STATE.lastX = e.clientX; STATE.velocity += dx * 0.002;
        }
    }
});
window.addEventListener('click', (e) => {
    const evTarget = e.target as Element;
    if (evTarget.closest('.btn') || evTarget.closest('.h-group')) return;
    if (STATE.mode === 'MOUSE') {
        const moveDist = Math.hypot(e.clientX - STATE.startX, e.clientY - STATE.startY);
        if (moveDist < 10) {
            if (STATE.phase === 'IDLE') selectCard(e.clientX, e.clientY);
            else if (STATE.phase === 'SHOW') dismiss();
            else if (STATE.phase === 'REVIEW_VIEW') {
                // 简短：关闭回顾视图并将克隆飞回角落
                document.getElementById('result-area').style.opacity = "0";
                const bounds = getScreenBounds();
                const groups = document.querySelectorAll('.h-group');
                groups.forEach(g => {
                    if (g.userData && g.userData.clones) {
                        g.userData.clones.forEach((c, i) => {
                            const targetX = bounds.left + 1.8 + (i * 1.4);
                            const targetY = bounds.bottom + 1.5;
                            const startP = c.position.clone();
                            const startS = c.scale.x;
                            let p2 = 0;
                            function animBack() {
                                p2 += 0.04; const ease = p2 * p2;
                                c.position.set(THREE.MathUtils.lerp(startP.x, targetX, ease), THREE.MathUtils.lerp(startP.y, targetY, ease), THREE.MathUtils.lerp(startP.z, 0, ease));
                                c.scale.setScalar(THREE.MathUtils.lerp(startS, 0.35, ease));
                                if (p2 < 1) requestAnimationFrame(animBack);
                                else c.visible = false;
                            }
                            animBack();
                        });
                    }
                });
                STATE.phase = 'IDLE';
                setTimeout(() => { if (STATE.phase === 'IDLE') STATE.velocity = Math.random() * 2.5 + 2.5; }, 300);
            }
            else if (STATE.phase === 'SPREAD_VIEW') resetSpread();
        }
    }
});
window.addEventListener('wheel', e => {
    if (STATE.mode === 'MOUSE' && STATE.phase === 'IDLE' && !STATE.isHoveringUI) { STATE.velocity -= e.deltaY * 0.001; }
});

// --- 模式切换与光标 ---
const toggle = document.getElementById('mode-toggle');
const cursor = document.getElementById('cursor');
toggle.onclick = () => {
    STATE.mode = STATE.mode === 'MOUSE' ? 'HAND' : 'MOUSE';
    const T = getText();
    if (STATE.mode === 'HAND') {
        toggle.innerText = T.camOn; toggle.classList.add('active');
        document.getElementById('guide-text').innerText = T.guideHand;
        startCam();
    } else {
        toggle.innerText = T.camOff; toggle.classList.remove('active');
        document.getElementById('guide-text').innerText = T.guideMouse;
        cursor.style.display = 'none';
        const v = document.getElementById('input-video') as HTMLVideoElement;
        if (v.srcObject) { (v.srcObject as MediaStream).getTracks().forEach(track => track.stop()); v.srcObject = null; }
        camStarted = false;
    }
    // Update tips if spread/show is active
    const tip = document.getElementById('click-tip');
    if (STATE.phase === 'SHOW') tip.innerText = STATE.mode === 'HAND' ? T.clickTipHand : T.clickTip;
    if (STATE.phase === 'SPREAD_VIEW') tip.innerText = STATE.mode === 'HAND' ? T.spreadTipHand : T.spreadTip;
};

// --- 手势识别与摄像头 ---
let camStarted = false;
const hands = new Hands({ locateFile: f => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${f}` });
hands.setOptions({ maxNumHands: 1, minDetectionConfidence: 0.5, modelComplexity: 0 });

// MediaPipe 结果回调（更新状态）
hands.onResults(res => {
    if (STATE.mode !== 'HAND') return;
    if (res.multiHandLandmarks && res.multiHandLandmarks.length > 0) {
        STATE.isHandVisible = true;
        const lm = res.multiHandLandmarks[0];
        const wrist = lm[0];
        let dist = 0;
        [4, 8, 12, 16, 20].forEach(i => dist += Math.hypot(lm[i].x - wrist.x, lm[i].y - wrist.y));
        const isFist = (dist / 5) < 0.25;

        // 目标坐标
        STATE.targetHandX = 1 - lm[9].x;
        STATE.targetHandY = lm[9].y;

        if (isFist) {
            STATE.fistFrames++;
            if (STATE.fistFrames > 5 && !STATE.isFist) {
                STATE.isFist = true;
                if (STATE.phase === 'IDLE') selectCard(STATE.handX * window.innerWidth, STATE.handY * window.innerHeight);
                else if (STATE.phase === 'SPREAD_VIEW') resetSpread();
            }
        } else {
            if (STATE.isFist && STATE.phase === 'SHOW') dismiss();
            STATE.fistFrames = 0; STATE.isFist = false;
        }
    } else {
        STATE.isHandVisible = false;
    }
});

// 启动摄像头
async function startCam() {
    if (camStarted) return;
    const v = document.getElementById('input-video') as HTMLVideoElement;
    const cam = new Camera(v, { onFrame: async () => { await hands.send({ image: v }); }, width: 320, height: 240 });
    await cam.start(); camStarted = true;
}

// 启动流程
initDeck();
// 找到历史记录的容器
const historyBox = document.getElementById('history-box');

// 当鼠标进入右上角历史记录区域时
historyBox.onmouseenter = () => {
    STATE.isHoveringUI = true;
    STATE.velocity = 0; // 同时也让卡片立即停止滑动，不再有惯性
};

// 当鼠标离开该区域时
historyBox.onmouseleave = () => {
    STATE.isHoveringUI = false;
};
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const elapsed = clock.getElapsedTime();

    // 在高频渲染循环中平滑更新圆圈位置
    if (STATE.mode === 'HAND') {
        if (STATE.isHandVisible) {
            cursor.style.display = 'block';
            // 插值系数 0.2 兼顾灵敏度与流畅度
            STATE.handX += (STATE.targetHandX - STATE.handX) * 0.25;
            STATE.handY += (STATE.targetHandY - STATE.handY) * 0.25;

            cursor.style.left = STATE.handX * 100 + '%';
            cursor.style.top = STATE.handY * 100 + '%';
            cursor.className = STATE.isFist ? 'fist' : '';
        } else {
            cursor.style.display = 'none';
        }
    }

    update(elapsed);
    composer.render();
}

animate();
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight); composer.setSize(window.innerWidth, window.innerHeight);
});