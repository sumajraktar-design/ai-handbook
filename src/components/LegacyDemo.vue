<script setup>
// 包装第一版手册里的原生 JS 动画，让它们能在 Vue 里直接使用。
// 动画函数会直接改写容器的 innerHTML，所以容器内部不交给 Vue 管理。
// 以后把某个动画改写成独立 Vue 组件时，只需要替换这里的映射。
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { DEMOS, clearTimers } from '../lib/legacy-demos.js'

const props = defineProps({ name: { type: String, required: true } })
const el = ref(null)

onMounted(() => {
  const fn = DEMOS[props.name]
  if (!fn) { el.value.textContent = `还没有名为 ${props.name} 的动画`; return }
  try { fn(el.value) } catch (e) { el.value.textContent = '动画加载失败：' + e.message }
})
onBeforeUnmount(clearTimers)
</script>

<template>
  <div class="vz" ref="el"></div>
</template>
