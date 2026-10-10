<script setup>
// 概念地图：用 frontmatter 的 related 字段画出概念之间的关系网。
// 力导向布局（d3-force）：有关联的概念互相吸引，同一分组的概念聚在一起。
import { ref, computed, onMounted, onBeforeUnmount, watch, markRaw } from 'vue'
import { forceSimulation, forceLink, forceManyBody, forceX, forceY, forceCollide } from 'd3-force'
import { concepts, edges as rawEdges, neighbors, byId, GROUPS, PRIORITY_LABEL, groupColor } from '../lib/content.js'

const props = defineProps({ focus: String, query: String, done: Set })
const emit = defineEmits(['open', 'update:focus'])

const W = 1000, H = 720
const R = { high: 9, medium: 7, low: 5.5 }
// 分组中心排成一个椭圆，同组概念围绕各自的中心
const centers = Object.fromEntries(GROUPS.map((g, i) => {
  const a = -Math.PI / 2 + (i / GROUPS.length) * Math.PI * 2
  return [g.id, { x: W / 2 + Math.cos(a) * 330, y: H / 2 + Math.sin(a) * 240 }]
}))

const nodes = markRaw(concepts.map((c, i) => ({
  id: c.id, title: c.title, group: c.group, priority: c.priority, r: R[c.priority] || 6,
  x: centers[c.group].x + Math.cos(i * 2.4) * 30, y: centers[c.group].y + Math.sin(i * 2.4) * 30,
})))
const links = markRaw(rawEdges.map(e => ({ ...e })))
const sim = forceSimulation(nodes)
  .force('link', forceLink(links).id(d => d.id).distance(70).strength(0.25))
  .force('charge', forceManyBody().strength(-170))
  .force('x', forceX(d => centers[d.group].x).strength(0.1))
  .force('y', forceY(d => centers[d.group].y).strength(0.1))
  .force('collide', forceCollide(d => d.r + 16))
  .stop()
for (let i = 0; i < 420; i++) sim.tick()

const frame = ref(0)
const view = ref({ x: 0, y: 0, k: 1 })
const svg = ref(null)
const hidden = ref(new Set())
const hover = ref(null)
const selected = computed(() => props.focus && byId[props.focus] ? props.focus : null)
const active = computed(() => hover.value || selected.value)

const degree = Object.fromEntries(concepts.map(c => [c.id, neighbors[c.id].size]))
const hubs = [...concepts].sort((a, b) => degree[b.id] - degree[a.id]).slice(0, 6)

const q = computed(() => (props.query || '').trim().toLowerCase())
const matches = computed(() => q.value ? new Set(concepts.filter(c => (c.title + c.en + c.lead).toLowerCase().includes(q.value)).map(c => c.id)) : null)

function nodeClass(n) {
  frame.value
  const cls = ['node']
  if (n.id === selected.value) cls.push('sel')
  if (props.done?.has(n.id)) cls.push('done')
  if (matches.value?.has(n.id)) cls.push('match')
  const a = active.value
  const dimmed = hidden.value.has(n.group) || (a && n.id !== a && !neighbors[a].has(n.id)) || (matches.value && !matches.value.has(n.id))
  if (dimmed) cls.push('dim')
  return cls
}
function edgeClass(e) {
  const a = active.value
  if (a && (e.source.id === a || e.target.id === a)) return 'edge hl'
  if (hidden.value.has(e.source.group) || hidden.value.has(e.target.group) || a || matches.value) return 'edge dim'
  return 'edge'
}

// 坐标换算：屏幕像素 → 画布坐标
function toWorld(ev) {
  const el = svg.value
  if (!el?.getScreenCTM) return { x: 0, y: 0 }
  const p = el.createSVGPoint(); p.x = ev.clientX; p.y = ev.clientY
  const s = p.matrixTransform(el.getScreenCTM().inverse())
  const v = view.value
  return { x: (s.x - v.x) / v.k, y: (s.y - v.y) / v.k, sx: s.x, sy: s.y }
}

function fit(pad = 40) {
  const xs = nodes.map(n => n.x), ys = nodes.map(n => n.y)
  const x0 = Math.min(...xs) - pad, x1 = Math.max(...xs) + pad, y0 = Math.min(...ys) - pad, y1 = Math.max(...ys) + pad + 14
  const k = Math.min(W / (x1 - x0), H / (y1 - y0), 1.6)
  view.value = { k, x: (W - (x0 + x1) * k) / 2, y: (H - (y0 + y1) * k) / 2 }
}
function centerOn(id) {
  const n = nodes.find(n => n.id === id); if (!n) return
  const k = Math.max(view.value.k, 1)
  view.value = { k, x: W / 2 - n.x * k - 80 * k, y: H / 2 - n.y * k }
}
function zoomBy(f, cx = W / 2, cy = H / 2) {
  const v = view.value, k = Math.min(4, Math.max(0.4, v.k * f))
  view.value = { k, x: cx - (cx - v.x) * (k / v.k), y: cy - (cy - v.y) * (k / v.k) }
}

// 拖动：拖节点 = 移动节点，拖空白 = 平移画布；位移很小算点击
let drag = null, raf = 0
function onDown(ev, n) {
  const w = toWorld(ev)
  drag = { n, start: { x: ev.clientX, y: ev.clientY }, last: w, moved: false, view: { ...view.value } }
  svg.value?.setPointerCapture?.(ev.pointerId)
  if (!n) svg.value?.classList.add('panning')
}
function onMove(ev) {
  if (!drag) return
  if (Math.hypot(ev.clientX - drag.start.x, ev.clientY - drag.start.y) > 4) drag.moved = true
  if (!drag.moved) return
  const w = toWorld(ev)
  if (drag.n) {
    drag.n.fx = w.x; drag.n.fy = w.y
    sim.alphaTarget(0.25); runSim()
  } else {
    const v = view.value
    // sx/sy 是 svg 自身坐标，不受画布平移缩放影响，可以直接相减
    view.value = { ...v, x: v.x + (w.sx - drag.last.sx), y: v.y + (w.sy - drag.last.sy) }
  }
  drag.last = w
}
function onUp() {
  if (!drag) return
  if (drag.n) {
    if (!drag.moved) emit('update:focus', drag.n.id)
    drag.n.fx = null; drag.n.fy = null; sim.alphaTarget(0)
  } else if (!drag.moved) emit('update:focus', null)
  svg.value?.classList.remove('panning')
  drag = null
}
function runSim() {
  if (raf) return
  const step = () => {
    sim.tick(); frame.value++
    raf = sim.alpha() > 0.02 ? requestAnimationFrame(step) : 0
  }
  sim.alpha(Math.max(sim.alpha(), 0.3)); raf = requestAnimationFrame(step)
}
function onWheel(ev) {
  const w = toWorld(ev)
  zoomBy(ev.deltaY < 0 ? 1.12 : 1 / 1.12, w.sx, w.sy)
}
function toggleGroup(g) {
  const s = new Set(hidden.value); s.has(g) ? s.delete(g) : s.add(g); hidden.value = s
}

onMounted(() => { fit(); if (selected.value) centerOn(selected.value) })
onBeforeUnmount(() => { cancelAnimationFrame(raf); sim.stop() })
watch(() => props.focus, id => { if (id) centerOn(id) })

const sel = computed(() => selected.value ? byId[selected.value] : null)
const selNeighbors = computed(() => sel.value ? [...neighbors[sel.value.id]].map(id => byId[id]) : [])
const groupName = id => GROUPS.find(g => g.id === id).name
</script>

<template>
  <div class="mapview">
    <div class="mapbox">
      <svg ref="svg" :viewBox="`0 0 ${W} ${H}`" role="img" aria-label="概念关系地图"
           @pointerdown.self="onDown($event, null)" @pointermove="onMove" @pointerup="onUp" @pointercancel="onUp"
           @wheel.prevent="onWheel">
        <rect :width="W" :height="H" fill="transparent" @pointerdown="onDown($event, null)" />
        <g :transform="`translate(${view.x},${view.y}) scale(${view.k})`">
          <line v-for="(e, i) in links" :key="i" :class="edgeClass(e)"
                :x1="e.source.x" :y1="e.source.y" :x2="e.target.x" :y2="e.target.y" :data-f="frame" />
          <g v-for="n in nodes" :key="n.id" :class="nodeClass(n)" :transform="`translate(${n.x},${n.y})`"
             @pointerdown.stop="onDown($event, n)" @pointerenter="hover = n.id" @pointerleave="hover = null">
            <circle :r="n.r" :style="{ fill: groupColor(n.group) }" />
            <text :y="n.r + 13" text-anchor="middle">{{ n.title }}</text>
          </g>
        </g>
      </svg>
      <div class="mapbar">
        <button v-for="g in GROUPS" :key="g.id" class="gchip" :class="{ off: hidden.has(g.id) }"
                :style="{ '--gc': groupColor(g.id) }" @click="toggleGroup(g.id)"><i></i>{{ g.name }}</button>
      </div>
      <div class="zoom">
        <button @click="zoomBy(1.25)" aria-label="放大">＋</button>
        <button @click="zoomBy(0.8)" aria-label="缩小">－</button>
        <button @click="fit()" aria-label="适应画面">⤢</button>
      </div>
      <div class="maphint">拖动画布平移 · 滚轮缩放 · 拖动节点 · 点击查看</div>
    </div>

    <aside class="mpanel" :style="sel ? { '--dc': groupColor(sel.group) } : {}">
      <template v-if="sel">
        <div class="kick">{{ groupName(sel.group) }} · {{ PRIORITY_LABEL[sel.priority] }}</div>
        <h2>{{ sel.title }}</h2>
        <div class="en">{{ sel.en }}</div>
        <p class="lead">{{ sel.lead }}</p>
        <h3 class="sec-h">直接关联 {{ selNeighbors.length }} 个概念</h3>
        <div class="nb">
          <button v-for="n in selNeighbors" :key="n.id" @click="emit('update:focus', n.id)">
            <i :style="{ background: groupColor(n.group) }"></i>{{ n.title }}
          </button>
        </div>
        <div class="acts">
          <button class="btn map" @click="emit('open', sel.id)">打开详细讲解</button>
          <button class="btn" @click="emit('update:focus', null)">取消选择</button>
        </div>
      </template>
      <template v-else>
        <h2>概念地图</h2>
        <p class="intro">每个点是一个概念，连线表示它们<b>互相关联</b>。颜色代表分组，点越大越重要。点击任意概念，会高亮它和它的邻居。</p>
        <p class="intro">{{ concepts.length }} 个概念 · {{ links.length }} 条关联</p>
        <h3 class="sec-h">关联最多的概念</h3>
        <div class="nb">
          <button v-for="h in hubs" :key="h.id" @click="emit('update:focus', h.id)">
            <i :style="{ background: groupColor(h.group) }"></i>{{ h.title }}<span style="margin-left:auto;color:var(--faint);font-size:12px">{{ degree[h.id] }} 条</span>
          </button>
        </div>
        <p class="intro" style="margin-top:12px">这些是串起整个知识体系的"枢纽"，优先吃透它们，其他概念会更容易连起来。</p>
      </template>
    </aside>
  </div>
</template>
