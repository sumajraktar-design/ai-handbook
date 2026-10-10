import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// base: './' 让构建产物使用相对路径，可以部署在任意子目录（GitHub Pages、Artifact）
export default defineConfig({
  base: './',
  plugins: [vue()],
  server: { port: 4321 },
})
