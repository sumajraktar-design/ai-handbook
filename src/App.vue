<script setup>
import { ref, computed, watch } from 'vue'
import ConceptList from './components/ConceptList.vue'
import ConceptDetail from './components/ConceptDetail.vue'
import ConceptMap from './components/ConceptMap.vue'
import { concepts, byId, STAGES, groupColor } from './lib/content.js'

// 浏览器存储只用于个人便利（记住进度和上次位置），读写都包在 try 里
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d } catch { return d } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)) } catch {} },
}

const view = ref(store.get('aih-view', 'list'))
const current = ref(byId[store.get('aih-cur', '')] ? store.get('aih-cur', '') : 'transformer')
const mapFocus = ref(null)
const query = ref('')
const stage = ref(null)
const done = ref(new Set(store.get('aih-done', [])))

watch(view, v => store.set('aih-view', v))
watch(current, v => store.set('aih-cur', v))

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return concepts.filter(c =>
    (stage.value === null || STAGES[stage.value].groups.includes(c.group)) &&
    (!q || (c.title + c.en + c.lead).toLowerCase().includes(q)))
})

function open(id) { if (byId[id]) { current.value = id; view.value = 'list' } }
function showMap(id) { mapFocus.value = id; view.value = 'map' }
function toggleDone(id) {
  const s = new Set(done.value); s.has(id) ? s.delete(id) : s.add(id)
  done.value = s; store.set('aih-done', [...s])
}
function pickStage(i) { stage.value = stage.value === i ? null : i }
</script>

<template>
  <header class="top">
    <div class="brand"><h1>AI 概念手册</h1><small>{{ concepts.length }} 个概念</small></div>
    <div class="seg" role="tablist" aria-label="视图">
      <button :class="{ on: view === 'list' }" role="tab" :aria-selected="view === 'list'" @click="view = 'list'">列表</button>
      <button :class="{ on: view === 'map' }" role="tab" :aria-selected="view === 'map'" @click="view = 'map'">概念地图</button>
    </div>
    <label class="search" for="q">
      <span aria-hidden="true" style="color:var(--faint)">⌕</span>
      <input id="q" v-model="query" type="search" placeholder="搜索概念，比如 注意力、RAG" autocomplete="off">
    </label>
    <div class="prog">
      <span>已掌握</span><span class="bar"><i :style="{ width: done.size / concepts.length * 100 + '%' }"></i></span>
      <span>{{ done.size }} / {{ concepts.length }}</span>
    </div>
  </header>

  <nav v-if="view === 'list'" class="spine" aria-label="学习主线">
    <button v-for="(s, i) in STAGES" :key="i" class="st" :class="{ on: stage === i }"
            :style="{ '--sc': groupColor(s.color) }" :aria-pressed="stage === i" @click="pickStage(i)">
      <b>{{ s.name }}</b><span>{{ s.desc }}</span>
    </button>
  </nav>

  <main v-if="view === 'list'" class="listview">
    <ConceptList :items="filtered" :current="current" :done="done" @open="open" />
    <ConceptDetail :id="current" :done="done.has(current)" @open="open" @toggle-done="toggleDone" @show-map="showMap" />
  </main>

  <ConceptMap v-else v-model:focus="mapFocus" :query="query" :done="done" @open="open" />
</template>
