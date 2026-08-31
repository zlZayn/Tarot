// 抽牌记录保存（localStorage，第一阶段方案，无后端依赖）
// 仅在完成一次完整 3 张抽牌时写入一条记录，不改变任何 UI 与交互。

export interface DrawCardEntry {
  id: number;
  isRev: boolean;
}

export interface DrawSessionRecord {
  id: string;
  time: string;
  schemaVersion: 1;
  language: "en" | "cn";
  mode: "MOUSE" | "HAND";
  cards: DrawCardEntry[];
}

const STORAGE_KEY = "ethereal-tarot:records";

function makeId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

export function saveDrawSession(
  record: Omit<DrawSessionRecord, "id" | "time">
): DrawSessionRecord {
  const full: DrawSessionRecord = {
    ...record,
    id: makeId(),
    schemaVersion: 1,
    time: new Date().toISOString()
  };

  const raw = localStorage.getItem(STORAGE_KEY);
  const records: DrawSessionRecord[] = raw ? JSON.parse(raw) : [];
  records.push(full);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
  } catch {
    // 存储已满或不可用时静默失败，不打断抽牌流程
  }
  return full;
}

export function getDrawSessions(): DrawSessionRecord[] {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}