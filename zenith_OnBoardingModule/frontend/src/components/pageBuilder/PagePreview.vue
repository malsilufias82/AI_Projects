<template>
  <div class="page-preview">
    <component-renderer
      v-for="(comp, index) in components"
      :key="comp.id"
      :component="comp"
      :index="index"
      :is-selected="false"
      :is-last="index === components.length - 1"
    />
  </div>
</template>

<script setup>
import ComponentRenderer from './ComponentRenderer.vue'

defineProps({
  components: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.page-preview {
  min-height: 100%;
}
</style>
