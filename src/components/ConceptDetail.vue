<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import LegacyDemo from './LegacyDemo.vue'
import { GROUPS, PRIORITY_LABEL, byId, concepts, groupColor } from '../lib/content.js'

const props = defineProps({ id: String, done: Boolean })
const emit = defineEmits(['open', 'toggle-done', 'show-map'])

const c = computed(() => byId[props.id])
const group = computed(() => GROUPS.find(g => g.id === c.value.group))
const peers = computed(() => concepts.filter(x => x.group === c.value.group))
const prev = computed(() => peers.value[peers.value.findIndex(x => x.id === props.id) - 1])
const next = computed(() => peers.value[peers.value.findIndex(x => x.id === props.id) + 1])
// "相关概念"用 frontmatter 渲染成按钮；"动画演示"换成真正的动画；"打个比方"单独加底色
const sections = computed(() => c.value.sections.filter(s => s.title !== '相关概念'))
const related = computed(() => c.value.related.map(r => byId[r]).filter(Boolean))

const root = ref(null)
watch(() => props.id, async () => { await nextTick(); if (root.value) root.value.scrollTop = 0 })

function onClick(e) {
  const a = e.target.closest('a[data-concept]')
  if (a) { e.preventDefault(); emit('open', a.dataset.concept) }
}
</script>

<template>
  <article class="detail" ref="root" :style="{ '--dc': groupColor(c.group) }" @click="onClick">
    <div class="kick">{{ group.name }} · {{ PRIORITY_LABEL[c.priority] }}</div>
    <h2 class="ttl">{{ c.title }}</h2>
    <div class="en">{{ c.en }}</div>
    <p class="lead">{{ c.lead }}</p>

    <template v-for="s in sections" :key="s.title">
      <h3 class="sec-h">{{ s.title }}</h3>
      <LegacyDemo v-if="s.title === '动画演示' && c.demo" :name="c.demo" :key="c.id" />
      <div v-else-if="s.title === '打个比方'" class="md analogy" v-html="s.html"></div>
      <div v-else class="md" v-html="s.html"></div>
    </template>

    <template v-if="related.length">
      <h3 class="sec-h">相关概念</h3>
      <div class="rel">
        <button v-for="r in related" :key="r.id" @click="emit('open', r.id)">{{ r.title }}</button>
      </div>
    </template>

    <div class="dfoot">
      <div class="nav">
        <button v-if="prev" class="btn" @click="emit('open', prev.id)">← {{ prev.title }}</button>
        <button v-if="next" class="btn" @click="emit('open', next.id)">{{ next.title }} →</button>
      </div>
      <div class="nav">
        <button class="btn map" @click="emit('show-map', c.id)">在地图中查看</button>
        <button class="btn ok" :class="{ is: done }" @click="emit('toggle-done', c.id)">{{ done ? '已掌握 ✓' : '标记为已掌握' }}</button>
      </div>
    </div>
  </article>
</template>
