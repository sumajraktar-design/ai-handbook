// 在构建时读取 wiki/ 下的 Markdown，解析成页面需要的数据。
// 内容只有一个来源：wiki/concepts/*.md。改 Markdown，页面自动更新。
import { marked } from 'marked'

const files = import.meta.glob('../../wiki/concepts/*.md', { query: '?raw', import: 'default', eager: true })
import indexMd from '../../wiki/index.md?raw'

export const GROUPS = [
  { id: 'base', name: '基础原理', sub: '机器怎么"学"' },
  { id: 'arch', name: '大模型结构', sub: 'Transformer 和它的零件' },
  { id: 'train', name: '训练与对齐', sub: '一个模型怎么造出来' },
  { id: 'deploy', name: '使用模型', sub: '推理、成本、部署' },
  { id: 'app', name: '应用开发', sub: '提示词、RAG、上下文工程' },
  { id: 'agent', name: 'Agent 智能体', sub: '让模型动手干活' },
  { id: 'frame', name: '开发框架', sub: 'LangChain、LangGraph 等' },
  { id: 'safe', name: '安全与风险', sub: '做产品必须考虑' },
]
export const groupColor = g => `var(--c-${g})`

export const STAGES = [
  { name: '① 原理', desc: '机器怎么从数据中学', groups: ['base'], color: 'base' },
  { name: '② 结构', desc: 'Transformer 长什么样', groups: ['arch'], color: 'arch' },
  { name: '③ 训练', desc: '产出唯一成果：权重', groups: ['train'], color: 'train' },
  { name: '④ 推理', desc: '每次提问都在发生', groups: ['deploy'], color: 'deploy' },
  { name: '⑤ 上下文', desc: '决定模型能看见什么', groups: ['app'], color: 'app' },
  { name: '⑥ Agent', desc: '模型 + 工具 + 循环', groups: ['agent', 'frame'], color: 'agent' },
  { name: '贯穿全程', desc: '安全与风险', groups: ['safe'], color: 'safe' },
]
export const PRIORITY_LABEL = { high: '开发者必知', medium: '很常见，要懂', low: '了解即可' }

// frontmatter 由我们自己的模板生成，格式固定：key: value / key: [a, b] / key: "带引号的字符串"
function parseFrontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?/)
  if (!m) return { data: {}, body: text }
  const data = {}
  for (const line of m[1].split('\n')) {
    const i = line.indexOf(':')
    if (i < 0) continue
    const key = line.slice(0, i).trim()
    let v = line.slice(i + 1).trim()
    if (v.startsWith('[')) v = v.slice(1, -1).split(',').map(s => s.trim()).filter(Boolean)
    else if (v.startsWith('"')) v = JSON.parse(v)
    data[key] = v
  }
  return { data, body: text.slice(m[0].length) }
}

// 概念页之间的链接 ./xxx.md 改成页面内跳转
marked.use({
  renderer: {
    link({ href, tokens }) {
      const text = this.parser.parseInline(tokens)
      const m = href.match(/^\.\/([\w-]+)\.md$/)
      if (m) return `<a href="#" data-concept="${m[1]}">${text}</a>`
      return `<a href="${href}" target="_blank" rel="noopener">${text}</a>`
    },
  },
})
const wrapTables = html => html.replace(/<table>/g, '<div class="tbl"><table>').replace(/<\/table>/g, '</table></div>')

function parseBody(body) {
  const parts = body.split(/^## /m)
  const head = parts.shift()
  const lead = (head.match(/^> (.+)$/m) || [])[1] || ''
  const sections = parts.map(p => {
    const nl = p.indexOf('\n')
    const title = p.slice(0, nl).trim()
    const md = p.slice(nl + 1).trim()
    return { title, md, html: wrapTables(marked.parse(md)) }
  })
  return { lead, sections }
}

const order = [...indexMd.matchAll(/concepts\/([\w-]+)\.md/g)].map(m => m[1])

export const concepts = Object.entries(files).map(([path, raw]) => {
  const { data, body } = parseFrontmatter(raw)
  const { lead, sections } = parseBody(body)
  return { ...data, related: data.related || [], lead, sections }
}).sort((a, b) => order.indexOf(a.id) - order.indexOf(b.id))

export const byId = Object.fromEntries(concepts.map(c => [c.id, c]))

// 概念地图的边：related 是有向的，这里合并成无向边
const seen = new Set()
export const edges = []
for (const c of concepts) for (const r of c.related) {
  if (!byId[r]) continue
  const key = [c.id, r].sort().join('|')
  if (seen.has(key)) continue
  seen.add(key); edges.push({ source: c.id, target: r })
}
export const neighbors = Object.fromEntries(concepts.map(c => [c.id, new Set()]))
for (const e of edges) { neighbors[e.source].add(e.target); neighbors[e.target].add(e.source) }
