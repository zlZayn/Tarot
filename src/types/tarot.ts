// 塔罗牌数据类型定义
// 与 src/legacy/app.ts 中的原数据结构一一对应（n=牌名 / u=正位关键词 / r=逆位关键词）。
export type Language = "en" | "cn";

export interface TarotCardData {
  n: string;
  u: string;
  r: string;
  id: number;
}