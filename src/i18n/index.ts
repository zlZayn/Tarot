// 多语言文案聚合入口，合并后的结构与原 index.html 的 UI_TEXT 完全一致。
import { uiTextEn } from "./en";
import { uiTextZh } from "./zh";
import type { UiText } from "./en";
import type { Language } from "../types/tarot";

export const UI_TEXT = {
  en: uiTextEn,
  cn: uiTextZh
} satisfies Record<Language, UiText>;