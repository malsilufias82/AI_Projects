<template>
  <div
    class="component-wrapper"
    :class="{ 'selected': isSelected }"
    @click="$emit('edit')"
  >
    <div class="component-actions">
      <q-btn
        flat
        dense
        round
        size="sm"
        icon="keyboard_arrow_up"
        color="grey"
        @click.stop="$emit('move-up')"
        :disable="index === 0"
      />
      <q-btn
        flat
        dense
        round
        size="sm"
        icon="keyboard_arrow_down"
        color="grey"
        @click.stop="$emit('move-down')"
        :disable="isLast"
      />
      <q-btn
        flat
        dense
        round
        size="sm"
        icon="edit"
        color="info"
        @click.stop="$emit('edit')"
      />
      <q-btn
        flat
        dense
        round
        size="sm"
        icon="delete"
        color="negative"
        @click.stop="$emit('remove')"
      />
    </div>

    <!-- Container -->
    <q-card
      v-if="component.type === 'container'"
      class="bg-grey-2"
      :style="containerStyle"
    >
      <q-card-section :class="paddingClass">
        <slot name="content" />
      </q-card-section>
    </q-card>

    <!-- Section -->
    <div v-else-if="component.type === 'section'" class="q-mb-md">
      <div class="text-h5 q-mb-md">{{ component.props.title }}</div>
      <q-card
        class="bg-white"
        :class="paddingClass"
        :style="{ borderRadius: '8px' }"
      >
        <slot name="content" />
      </q-card>
    </div>

    <!-- Card -->
    <q-card
      v-else-if="component.type === 'card'"
      class="bg-white"
      :class="paddingClass"
      :style="{ borderRadius: '8px' }"
    >
      <q-card-section v-if="component.props.title">
        <div class="text-subtitle2">{{ component.props.title }}</div>
      </q-card-section>
      <q-card-section>
        {{ component.props.content }}
      </q-card-section>
    </q-card>

    <!-- Button -->
    <q-btn
      v-else-if="component.type === 'button'"
      :label="component.props.label"
      :color="component.props.color"
      :size="component.props.size"
      :outline="component.props.outline"
      class="q-mb-md"
    />

    <!-- Text -->
    <div
      v-else-if="component.type === 'text'"
      :class="textVariantClass"
      :style="{ color: component.props.color }"
      class="q-mb-md"
    >
      {{ component.props.content }}
    </div>

    <!-- Heading -->
    <component
      v-else-if="component.type === 'heading'"
      :is="component.props.level"
      :style="{ color: component.props.color }"
      class="q-mb-md"
    >
      {{ component.props.content }}
    </component>

    <!-- Image -->
    <q-img
      v-else-if="component.type === 'image'"
      :src="component.props.src || 'https://via.placeholder.com/400x200'"
      :alt="component.props.alt"
      :contain="component.props.contain"
      class="q-mb-md"
      style="max-width: 100%;"
    >
      <template v-if="!component.props.src" v-slot:error>
        <div class="absolute-full flex flex-center bg-grey-2 text-grey-6">
          <div>
            <q-icon name="image" size="32px" />
            <div class="text-caption">No image</div>
          </div>
        </div>
      </template>
    </q-img>

    <!-- Divider -->
    <q-separator
      v-else-if="component.type === 'divider'"
      :color="component.props.color"
      :inset="component.props.inset"
      class="q-my-md"
    />

    <!-- Spacer -->
    <div
      v-else-if="component.type === 'spacer'"
      :style="{ height: spacerHeight }"
    />

    <!-- Grid -->
    <div
      v-else-if="component.type === 'grid'"
      class="row q-gutter-md q-mb-md"
    >
      <div
        v-for="i in component.props.columns"
        :key="i"
        :class="gridColClass"
        class="bg-grey-2"
        style="min-height: 100px; border-radius: 8px; display: flex; align-items: center; justify-content: center;"
      >
        <span class="text-grey-6">Column {{ i }}</span>
      </div>
    </div>

    <!-- Input -->
    <q-input
      v-else-if="component.type === 'input'"
      :label="component.props.label"
      :placeholder="component.props.placeholder"
      :outlined="component.props.outlined"
      dense
      color="primary"
      class="q-mb-md"
    />

    <!-- Select -->
    <q-select
      v-else-if="component.type === 'select'"
      :label="component.props.label"
      :options="component.props.options"
      :outlined="component.props.outlined"
      dense
      color="primary"
      class="q-mb-md"
    />

    <!-- Checkbox -->
    <q-checkbox
      v-else-if="component.type === 'checkbox'"
      :label="component.props.label"
      :color="component.props.color"
      class="q-mb-md"
    />

    <!-- Chart placeholder -->
    <q-card
      v-else-if="component.type === 'chart'"
      class="bg-grey-2 q-mb-md"
      style="min-height: 200px; border-radius: 8px;"
    >
      <q-card-section>
        <div class="text-subtitle2 q-mb-md">{{ component.props.title }}</div>
        <div class="flex flex-center text-grey-6" style="height: 150px;">
          <div class="text-center">
            <q-icon name="bar_chart" size="48px" />
            <div class="text-caption q-mt-sm">{{ component.props.type }} chart</div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Table placeholder -->
    <q-table
      v-else-if="component.type === 'table'"
      flat
      bordered
      :rows="tableRows"
      :columns="tableColumns"
      row-key="name"
      class="q-mb-md bg-white"
      style="border-radius: 8px;"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  component: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  isLast: {
    type: Boolean,
    default: false
  }
})

defineEmits(['move-up', 'move-down', 'remove', 'edit'])

const paddingClass = computed(() => {
  const padding = props.component.props.padding || 'md'
  return `q-pa-${padding === 'none' ? 'none' : padding === 'sm' ? 'sm' : padding === 'lg' ? 'lg' : 'md'}`
})

const containerStyle = computed(() => {
  const props = props.component.props
  return {
    padding: props.padding === 'none' ? '0' : props.padding === 'sm' ? '8px' : props.padding === 'lg' ? '24px' : '16px',
    margin: props.margin === 'none' ? '0' : '16px',
    backgroundColor: props.backgroundColor === 'transparent' ? 'transparent' : props.backgroundColor,
    borderRadius: props.borderRadius === 'none' ? '0' : '8px'
  }
})

const textVariantClass = computed(() => {
  const variant = props.component.props.variant || 'body1'
  return `text-${variant}`
})

const spacerHeight = computed(() => {
  const size = props.component.props.size || 'md'
  const heights = { xs: '8px', sm: '16px', md: '24px', lg: '32px', xl: '48px' }
  return heights[size] || '24px'
})

const gridColClass = computed(() => {
  const cols = props.component.props.columns || 2
  return `col-${12 / cols}`
})

const tableColumns = computed(() => {
  const columns = props.component.props.columns || ['Column 1', 'Column 2', 'Column 3']
  return columns.map((col, i) => ({
    name: `col${i}`,
    label: col,
    field: `col${i}`,
    align: 'left'
  }))
})

const tableRows = computed(() => {
  const rows = props.component.props.rows || 3
  const cols = props.component.props.columns?.length || 3
  return Array.from({ length: rows }, (_, i) => {
    const row = { name: `row${i}` }
    for (let j = 0; j < cols; j++) {
      row[`col${j}`] = `Data ${i + 1}-${j + 1}`
    }
    return row
  })
})
</script>

<style scoped>
.component-wrapper {
  position: relative;
  border: 2px solid transparent;
  border-radius: 8px;
  padding: 8px;
  transition: all 0.2s;
}

.component-wrapper:hover {
  border-color: rgba(0, 80, 213, 0.3);
}

.component-wrapper.selected {
  border-color: rgba(0, 80, 213, 1);
}

.component-actions {
  position: absolute;
  top: -12px;
  right: -12px;
  display: flex;
  gap: 4px;
  background: #2d2d2d;
  padding: 4px;
  border-radius: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 10;
}

.component-wrapper:hover .component-actions {
  opacity: 1;
}
</style>
