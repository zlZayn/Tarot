// UI 文案（英文），原样搬运自原 index.html 的 UI_TEXT.en，未改写。
export const uiTextEn = {
  logo: "ETHEREAL TAROT",
  camOff: "Camera Off",
  camOn: "Switch to Mouse",
  shuffle: "Shuffle Deck",
  langLabel: "Language: EN",
  guideMouse: "DRAG TO SCROLL • CLICK TO SELECT",
  guideHand: "Palm: Scroll • Fist: Select",
  clickTip: "CLICK TO DISMISS",
  clickTipHand: "OPEN PALM TO DISMISS",
  spreadTip: "CLICK TO RESET DECK",
  spreadTipHand: "FIST TO RESET DECK",
  spreadDesc: "PAST • PRESENT • FUTURE",
  reviewDesc: "REVIEWING SESSION",
  reviewTip: "CLICK TO DISMISS",
  rev: "REVERSED",
  upr: "UPRIGHT",
  revShort: "Rev.",
  uprShort: "Upr.",
  loading: "SUMMONING ARCANA",
  historyTitle: "READING SESSION",
  posNames: ["PAST", "PRESENT", "FUTURE"],
  defaultArcana: "ARCANA"
};

/** 文案形状的唯一真源：本文件原样搬运自原 index.html 的 UI_TEXT.en，zh 侧用 satisfies 对齐它。 */
export type UiText = typeof uiTextEn;