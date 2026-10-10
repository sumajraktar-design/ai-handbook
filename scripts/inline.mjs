// 把 vite 构建出来的 dist/index.html 和它引用的 JS、CSS 合并成一个自包含的页面片段，
// 用于发布成 Artifact（单文件、无外部依赖，字体除外）。
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const dist = 'dist'
const html = readFileSync(join(dist, 'index.html'), 'utf8')
const css = [...html.matchAll(/<link rel="stylesheet"[^>]*href="\.\/([^"]+\.css)"[^>]*>/g)].map(m => readFileSync(join(dist, m[1]), 'utf8'))
const js = [...html.matchAll(/<script type="module"[^>]*src="\.\/([^"]+\.js)"[^>]*><\/script>/g)].map(m => readFileSync(join(dist, m[1]), 'utf8'))
if (!css.length || !js.length) throw new Error('没有在 dist/index.html 里找到构建产物')

const fonts = (html.match(/<link rel="preconnect"[^>]*>|<link rel="stylesheet" href="https:\/\/fonts[^>]*>/g) || []).join('\n')
// 依赖库里有字面量的 U+FFFD（解码失败时的替换字符），改成转义写法，避免被当成损坏的字符
const safe = s => s.replace(/<\/script/gi, '<\\/script').replace(/�/g, '\\uFFFD')
const out = `<title>AI 概念手册</title>
${fonts}
<style>${css.join('\n')}</style>
<div id="app"></div>
<script type="module">${safe(js.join('\n'))}</script>
`
writeFileSync(join(dist, 'artifact.html'), out)
console.log(`dist/artifact.html  ${(out.length / 1024).toFixed(0)} KB`)
