// 全局声明（原 index.html 经典脚本注入的 MediaPipe 全局，无 npm 类型包）
// 仅描述本应用用到的成员，不做完整类型化。

/** MediaPipe 手掌关键点：本应用只用 21 点里的手腕与中指根部（索引 0/9）。 */
interface HandLandmark {
  x: number;
  y: number;
}

/** 本应用用到的 `hands.onResults` 结果子集（完整字段见 MediaPipe 官方类型）。 */
interface HandsResults {
  multiHandLandmarks?: HandLandmark[][];
}

declare class Hands {
  constructor(opts: { locateFile: (file: string) => string });
  setOptions(opts: Record<string, number | boolean>): void;
  send(input: { image: HTMLVideoElement }): Promise<void>;
  onResults(cb: (results: HandsResults) => void): void;
}

declare class Camera {
  constructor(video: HTMLVideoElement, opts: { onFrame: () => Promise<void>; width: number; height: number });
  start(): Promise<void>;
}

// 原逻辑遗留约定：DOM 元素上直接挂 userData（three 风格自定义数据）
interface Element {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- 异构动态包（网格挂 {id,isRev,seed}、分组挂 {clones,snapshots}）；收窄它等于要求改 src/legacy/app.ts 的 27 处调用点，而那是只搬不重写的受保护区。
  userData?: any;
}
