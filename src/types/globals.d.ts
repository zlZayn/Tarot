// 全局声明（原 index.html 经典脚本注入的 MediaPipe 全局，无 npm 类型包）
// 仅描述本应用用到的成员，不做完整类型化。

declare class Hands {
  constructor(opts: { locateFile: (file: string) => string });
  setOptions(opts: Record<string, number | boolean>): void;
  send(input: { image: HTMLVideoElement }): Promise<void>;
  onResults(cb: (results: any) => void): void;
}

declare class Camera {
  constructor(video: HTMLVideoElement, opts: { onFrame: () => Promise<void>; width: number; height: number });
  start(): Promise<void>;
}

// 原逻辑遗留约定：DOM 元素上直接挂 userData（three 风格自定义数据）
interface Element {
  userData?: any;
}