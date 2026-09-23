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
  userData?: any;
}
