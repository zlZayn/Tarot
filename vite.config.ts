import { defineConfig } from "vite";

export default defineConfig({
  root: "src",
  base: "./",
  publicDir: "../public",
  server: {
    port: 5173,
    open: false,
    strictPort: true,
    watch: {
      // 编辑器原子替换产生的临时目录会让 chokidar 在 Windows 上 EBUSY 崩溃，忽略之
      ignored: ["**/*.tmpdir/**"]
    }
  },
  build: {
    outDir: "../dist",
    emptyOutDir: true,
    assetsInlineLimit: 0,
    sourcemap: false
  }
});