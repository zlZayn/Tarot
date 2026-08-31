// 构建后清理：publicDir 会把 public/ 维护双件（README.md/AGENTS.md）拷入 dist，
// 它们属于文档网络而非运行时资源，必须在发布包中剔除。
// 不能用 Vite closeBundle 钩子：它早于 copyPublicDir 执行，删了会被拷回来。
import { existsSync, rmSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const excluded = ["README.md", "AGENTS.md"];

let removed = 0;
for (const name of excluded) {
  const p = join(root, "dist", name);
  if (existsSync(p)) {
    rmSync(p);
    removed++;
  }
}
if (removed > 0) {
  console.log(`[clean-dist] 已从 dist 排除 ${removed} 个维护文档`);
}