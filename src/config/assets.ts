// 运行时图片资源配置（唯一权威位置）
// 业务代码只从这里取路径：牌面走 `cardUrl(id)`，牌背走 `BACK_URL`。
// 2026-10-18：纹理统一转 WebP（原 PNG/JPG 已删除，转换脚本 scripts/optimize_images.py）。
// 目录与扩展名在此收口，换格式/换目录只改本文件，调用方不再硬编码任何后缀。
const CARDS_DIR = "./textures/cards/";
const BACKS_DIR = "./textures/backs/";
const EXT = ".webp";

/** 牌背纹理完整 URL（当前默认牌背 bm4） */
export const BACK_URL = `${BACKS_DIR}bm4${EXT}`;

/** 牌面纹理完整 URL：牌面目录 + 牌 id + 扩展名 */
export function cardUrl(id: number): string {
  return `${CARDS_DIR}${id}${EXT}`;
}
