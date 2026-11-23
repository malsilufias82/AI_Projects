<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h4 text-weight-bold">Page Builder</div>
        <div class="text-subtitle1 text-grey-6">{{ currentPage?.name || 'New Page' }}</div>
      </div>
      <div class="row q-gutter-sm">
        <q-btn
          flat
          color="info"
          icon="visibility"
          label="Preview"
          @click="showPreview = true"
        />
        <q-btn
          unelevated
          color="primary"
          icon="save"
          label="Save Page"
          @click="savePage"
        />
        <q-btn
          flat
          color="grey"
          icon="close"
          label="Close"
          @click="goBack"
        />
      </div>
    </div>

    <div class="row q-col-gutter-md" style="height: calc(100vh - 120px);">
      <!-- Component Library -->
      <div class="col-3">
        <q-card class="bg-white text-dark" style="height: 100%;">
          <q-card-section class="q-pb-sm">
            <div class="text-subtitle2">Components</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <q-tabs
              v-model="selectedCategory"
              dense
              class="text-grey"
              active-color="primary"
              indicator-color="primary"
              align="left"
              no-caps
            >
              <q-tab
                v-for="category in componentCategories"
                :key="category.id"
                :name="category.id"
                :label="category.name"
                :icon="category.icon"
              />
            </q-tabs>
          </q-card-section>
          <q-separator dark />
          <q-card-section class="scroll" style="height: calc(100% - 150px); overflow-y: auto;">
            <div class="q-gutter-sm">
              <q-card
                v-for="component in filteredComponents"
                :key="component.id"
                class="bg-grey-2 cursor-pointer"
                flat
                bordered
                @click="addComponent(component)"
                @dragstart="onDragStart(component, $event)"
                draggable="true"
              >
                <q-card-section class="q-pa-sm">
                  <div class="row items-center">
                    <q-icon :name="component.icon" color="primary" class="q-mr-sm" />
                    <div class="text-subtitle2">{{ component.name }}</div>
                  </div>
                  <div class="text-caption text-grey-6">{{ component.description }}</div>
                </q-card-section>
              </q-card>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Canvas / Page Editor -->
      <div class="col-6">
        <q-card class="bg-white text-dark" style="height: 100%;">
          <q-card-section class="q-pb-sm">
            <div class="row items-center justify-between">
              <div class="text-subtitle2">Page Canvas</div>
              <q-btn
                flat
                dense
                size="sm"
                icon="delete_sweep"
                color="negative"
                label="Clear All"
                @click="clearCanvas"
              />
            </div>
          </q-card-section>
          <q-separator dark />
          <q-card-section
            class="scroll q-pa-md"
            style="height: calc(100% - 60px); overflow-y: auto; background: #f5f5f5;"
            @drop="onDrop"
            @dragover.prevent
          >
            <div
              v-if="pageComponents.length === 0"
              class="text-center text-grey-6 q-py-xl"
            >
              <q-icon name="add_circle_outline" size="64px" class="q-mb-md" />
              <div class="text-h6">Drag components here</div>
              <div class="text-caption">or click on components from the library</div>
            </div>
            <div v-else class="q-gutter-md">
              <component-renderer
                v-for="(comp, index) in pageComponents"
                :key="comp.id"
                :component="comp"
                :index="index"
                @move-up="moveComponent(index, -1)"
                @move-down="moveComponent(index, 1)"
                @remove="removeComponent(index)"
                @edit="editComponent(index)"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Properties Panel -->
      <div class="col-3">
        <q-card class="bg-white text-dark" style="height: 100%;">
          <q-card-section class="q-pb-sm">
            <div class="text-subtitle2">Properties</div>
          </q-card-section>
          <q-separator dark />
          <q-card-section class="scroll" style="height: calc(100% - 60px); overflow-y: auto;">
            <div v-if="selectedComponent" class="q-gutter-md">
              <div class="text-subtitle2 text-primary">{{ selectedComponent.name }}</div>

              <q-input
                v-for="(value, key) in selectedComponent.props"
                :key="key"
                v-model="selectedComponent.props[key]"
                :label="key"
                outlined
                dark
                dense
                color="primary"
              />

              <q-select
                v-if="selectedComponent.id === 'heading'"
                v-model="selectedComponent.props.level"
                :options="['h1', 'h2', 'h3', 'h4', 'h5', 'h6']"
                label="Heading Level"
                outlined
                dark
                dense
                color="primary"
              />

              <q-select
                v-if="selectedComponent.id === 'button'"
                v-model="selectedComponent.props.color"
                :options="['primary', 'secondary', 'accent', 'positive', 'negative', 'warning', 'info']"
                label="Button Color"
                outlined
                dark
                dense
                color="primary"
              />

              <q-select
                v-if="selectedComponent.id === 'button'"
                v-model="selectedComponent.props.size"
                :options="['xs', 'sm', 'md', 'lg', 'xl']"
                label="Button Size"
                outlined
                dark
                dense
                color="primary"
              />

              <q-toggle
                v-if="selectedComponent.id === 'button'"
                v-model="selectedComponent.props.outline"
                label="Outline"
                color="primary"
              />
            </div>
            <div v-else class="text-center text-grey-6 q-py-xl">
              <q-icon name="tune" size="48px" class="q-mb-md" />
              <div>Select a component</div>
              <div class="text-caption">to edit its properties</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Preview Dialog -->
    <q-dialog v-model="showPreview" maximized>
      <q-card class="bg-white text-dark">
        <q-card-section class="row items-center q-pb-sm">
          <div class="text-subtitle2">Page Preview</div>
          <q-space />
          <q-btn flat round icon="close" v-close-popup />
        </q-card-section>
        <q-card-section class="q-pa-none">
          <div class="q-pa-md" style="min-height: calc(100vh - 60px);">
            <page-preview :components="pageComponents" />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { componentLibrary, componentCategories } from '../components/pageBuilder/ComponentLibrary'
import ComponentRenderer from '../components/pageBuilder/ComponentRenderer.vue'
import PagePreview from '../components/pageBuilder/PagePreview.vue'

const router = useRouter()
const route = useRoute()

const selectedCategory = ref('layout')
const pageComponents = ref([])
const selectedComponent = ref(null)
const showPreview = ref(false)
const currentPage = ref(null)

const filteredComponents = computed(() => {
  return componentLibrary.filter(c => c.category === selectedCategory.value)
})

onMounted(() => {
  const pageId = route.params.pageId
  if (pageId) {
    // Load existing page data
    loadPageData(pageId)
  }
})

const loadPageData = (pageId) => {
  // In a real app, this would fetch from API
  const savedPages = JSON.parse(localStorage.getItem('zenith-pages') || '[]')
  currentPage.value = savedPages.find(p => p.id === pageId)
  if (currentPage.value) {
    pageComponents.value = currentPage.value.components || []
  }
}

const addComponent = (component) => {
  const newComponent = {
    id: `${component.id}-${Date.now()}`,
    type: component.id,
    name: component.name,
    icon: component.icon,
    props: { ...component.defaultProps }
  }
  pageComponents.value.push(newComponent)
  selectedComponent.value = newComponent
}

const onDragStart = (component, event) => {
  event.dataTransfer.setData('component', JSON.stringify(component))
}

const onDrop = (event) => {
  const componentData = event.dataTransfer.getData('component')
  if (componentData) {
    const component = JSON.parse(componentData)
    addComponent(component)
  }
}

const removeComponent = (index) => {
  pageComponents.value.splice(index, 1)
  if (selectedComponent.value && index === pageComponents.value.length) {
    selectedComponent.value = null
  }
}

const moveComponent = (index, direction) => {
  const newIndex = index + direction
  if (newIndex >= 0 && newIndex < pageComponents.value.length) {
    const temp = pageComponents.value[index]
    pageComponents.value[index] = pageComponents.value[newIndex]
    pageComponents.value[newIndex] = temp
  }
}

const editComponent = (index) => {
  selectedComponent.value = pageComponents.value[index]
}

const clearCanvas = () => {
  if (confirm('Are you sure you want to clear all components?')) {
    pageComponents.value = []
    selectedComponent.value = null
  }
}

const savePage = () => {
  const pageData = {
    id: currentPage.value?.id || Date.now().toString(),
    name: currentPage.value?.name || 'New Page',
    description: currentPage.value?.description || '',
    route: currentPage.value?.route || `/custom-${Date.now()}`,
    components: pageComponents.value
  }

  const savedPages = JSON.parse(localStorage.getItem('zenith-pages') || '[]')
  const existingIndex = savedPages.findIndex(p => p.id === pageData.id)

  if (existingIndex >= 0) {
    savedPages[existingIndex] = pageData
  } else {
    savedPages.push(pageData)
  }

  localStorage.setItem('zenith-pages', JSON.stringify(savedPages))

  // Show success notification
  alert('Page saved successfully!')
}

const goBack = () => {
  router.push('/page-manager')
}
</script>

<style scoped>
.scroll::-webkit-scrollbar {
  width: 8px;
}

.scroll::-webkit-scrollbar-track {
  background: #2d2d2d;
}

.scroll::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}

.scroll::-webkit-scrollbar-thumb:hover {
  background: #777;
}
</style>
