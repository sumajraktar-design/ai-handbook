<script setup>
import { computed } from 'vue'
import { GROUPS, groupColor } from '../lib/content.js'

const props = defineProps({ items: Array, current: String, done: Set })
const emit = defineEmits(['open'])
const groups = computed(() => GROUPS.map(g => ({ ...g, items: props.items.filter(c => c.group === g.id) })).filter(g => g.items.length))
</script>

<template>
  <nav class="toc" aria-label="概念目录">
    <div class="legend">
      <span><i class="pr high"></i>开发者必知</span>
      <span><i class="pr medium"></i>很常见，要懂</span>
      <span><i class="pr low"></i>了解即可</span>
      <span>▶ 有动画</span>
    </div>
    <section v-for="g in groups" :key="g.id" class="grp" :style="{ '--gc': groupColor(g.id) }">
      <div class="grp-h"><h2>{{ g.name }}</h2><small>{{ g.sub }} · {{ g.items.length }}</small></div>
      <div class="chips">
        <button v-for="c in g.items" :key="c.id" class="chip" :class="{ on: c.id === current, done: done.has(c.id) }" @click="emit('open', c.id)">
          <i class="pr" :class="c.priority"></i>{{ c.title }}<span v-if="c.demo" class="anim" title="有动画演示">▶</span>
        </button>
      </div>
    </section>
    <div v-if="!groups.length" class="empty">没有找到匹配的概念，换个关键词试试。</div>
  </nav>
</template>
