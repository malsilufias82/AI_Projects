<template>
  <q-page class="spreadsheet-page">
    <div class="spreadsheet-header">
      <!-- Top Row -->
      <div class="header-top-row">
        <div class="header-left">
          <q-avatar size="32px" class="q-mr-sm">
            <img src="/logo.png" alt="Logo">
          </q-avatar>
          <div class="sheet-info">
            <div class="row items-center">
              <q-input
                v-model="sheetName"
                dense
                borderless
                class="sheet-name-input"
                input-class="text-h6 text-weight-medium"
              />
              <q-btn
                flat
                dense
                round
                :icon="isStarred ? 'star' : 'star_border'"
                :color="isStarred ? 'warning' : 'grey-7'"
                size="sm"
                class="q-ml-xs"
                @click="toggleStar"
              />
              <q-btn
                flat
                dense
                round
                icon="sync"
                color="grey-7"
                size="sm"
                class="q-ml-xs"
                @click="syncSheet"
              />
            </div>
          </div>
        </div>

        <div class="header-right">
          <q-btn flat dense round icon="history" color="grey-7" size="md">
            <q-tooltip>History</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="chat_bubble_outline" color="grey-7" size="md">
            <q-tooltip>Comments</q-tooltip>
          </q-btn>
          <div class="share-button-wrapper">
            <q-btn unelevated dense no-caps icon="share" color="primary" size="md" label="Share" class="q-px-sm rounded-borders">
              <q-menu>
                <q-list style="min-width: 150px;">
                  <q-item clickable v-close-popup>
                    <q-item-section avatar>
                      <q-icon name="person_add" />
                    </q-item-section>
                    <q-item-section>Share with people</q-item-section>
                  </q-item>
                  <q-item clickable v-close-popup>
                    <q-item-section avatar>
                      <q-icon name="link" />
                    </q-item-section>
                    <q-item-section>Get shareable link</q-item-section>
                  </q-item>
                  <q-item clickable v-close-popup>
                    <q-item-section avatar>
                      <q-icon name="email" />
                    </q-item-section>
                    <q-item-section>Email collaborators</q-item-section>
                  </q-item>
                </q-list>
              </q-menu>
            </q-btn>
          </div>
          <q-btn flat dense round icon="account_circle" color="grey-7" size="md">
            <q-tooltip>Profile</q-tooltip>
          </q-btn>
        </div>
      </div>

      <!-- Bottom Row - Menu -->
      <div class="header-menu-row">
        <q-btn flat dense no-caps class="menu-item">File</q-btn>
        <q-btn flat dense no-caps class="menu-item">Edit</q-btn>
        <q-btn flat dense no-caps class="menu-item">View</q-btn>
        <q-btn flat dense no-caps class="menu-item">Insert</q-btn>
        <q-btn flat dense no-caps class="menu-item">Format</q-btn>
        <q-btn flat dense no-caps class="menu-item">Data</q-btn>
        <q-btn flat dense no-caps class="menu-item">Tools</q-btn>
        <q-btn flat dense no-caps class="menu-item">Extensions</q-btn>
        <q-btn flat dense no-caps class="menu-item">Help</q-btn>
      </div>
    </div>
    <div ref="univerContainer" class="spreadsheet-container"></div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { UniverSheetsCorePreset } from '@univerjs/preset-sheets-core'
import UniverPresetSheetsCoreEnUS from '@univerjs/preset-sheets-core/locales/en-US'
import { createUniver, LocaleType, mergeLocales } from '@univerjs/presets'
import '@univerjs/preset-sheets-core/lib/index.css'

const univerContainer = ref(null)
const sheetName = ref('Project Budget Sheet')
const isStarred = ref(false)
let univerInstance = null
let univerAPIInstance = null

onMounted(() => {
  const { univer, univerAPI } = createUniver({
    locale: LocaleType.EN_US,
    // darkMode: true,
    locales: {
      [LocaleType.EN_US]: mergeLocales(UniverPresetSheetsCoreEnUS),
    },
    presets: [
      UniverSheetsCorePreset({
        container: univerContainer.value,
      }),
    ],
  })

  univerAPI.createWorkbook({
    sheetName: 'Project Budget',
    cellData: {
      0: {
        0: { v: 'Project Budget Sheet' },
        1: { v: '' },
        2: { v: '' },
        3: { v: '' },
        4: { v: 'Q1' },
        5: { v: 'Q2' },
        6: { v: 'Q3' },
        7: { v: 'Q4' },
      },
      1: {
        0: { v: 'Category' },
        1: { v: 'Item' },
        2: { v: 'Description' },
        3: { v: 'Total' },
        4: { v: 15000 },
        5: { v: 18000 },
        6: { v: 22000 },
        7: { v: 25000 },
      },
      2: {
        0: { v: 'Personnel' },
        1: { v: 'Salaries' },
        2: { v: 'Team salaries' },
        3: { v: 80000 },
        4: { v: 20000 },
        5: { v: 20000 },
        6: { v: 20000 },
        7: { v: 20000 },
      },
      3: {
        0: { v: '' },
        1: { v: 'Contractors' },
        2: { v: 'External contractors' },
        3: { v: 25000 },
        4: { v: 5000 },
        5: { v: 6000 },
        6: { v: 7000 },
        7: { v: 7000 },
      },
      4: {
        0: { v: 'Infrastructure' },
        1: { v: 'Servers' },
        2: { v: 'Cloud infrastructure' },
        3: { v: 12000 },
        4: { v: 3000 },
        5: { v: 3000 },
        6: { v: 3000 },
        7: { v: 3000 },
      },
      5: {
        0: { v: '' },
        1: { v: 'Software' },
        2: { v: 'Licenses & tools' },
        3: { v: 8000 },
        4: { v: 2000 },
        5: { v: 2000 },
        6: { v: 2000 },
        7: { v: 2000 },
      },
      6: {
        0: { v: 'Marketing' },
        1: { v: 'Advertising' },
        2: { v: 'Digital marketing' },
        3: { v: 15000 },
        4: { v: 3000 },
        5: { v: 4000 },
        6: { v: 4000 },
        7: { v: 4000 },
      },
      7: {
        0: { v: '' },
        1: { v: 'Events' },
        2: { v: 'Conferences & events' },
        3: { v: 10000 },
        4: { v: 2000 },
        5: { v: 2500 },
        6: { v: 2500 },
        7: { v: 3000 },
      },
      8: {
        0: { v: 'Total' },
        1: { v: '' },
        2: { v: '' },
        3: { v: 150000 },
        4: { v: 35000 },
        5: { v: 37500 },
        6: { v: 40500 },
        7: { v: 37000 },
      },
    },
  })

  univerInstance = univer
  univerAPIInstance = univerAPI
})

onBeforeUnmount(() => {
  univerInstance?.dispose()
  univerAPIInstance?.dispose()
  univerInstance = null
  univerAPIInstance = null
})

const toggleStar = () => {
  isStarred.value = !isStarred.value
  console.log('Sheet starred:', isStarred.value)
}

const syncSheet = () => {
  console.log('Syncing sheet...')
}
</script>

<style scoped>
.spreadsheet-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 0;
}

.spreadsheet-header {
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
  border-bottom: 1px solid #E0E0E0;
}

.header-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
}

.header-left {
  display: flex;
  align-items: center;
}

.sheet-info {
  display: flex;
  align-items: center;
}

.sheet-name-input {
  width: auto;
  min-width: 200px;
}

.sheet-name-input :deep(.q-field__control) {
  padding: 0;
}

.sheet-name-input :deep(.q-field__native) {
  font-size: 18px;
  font-weight: 500;
  color: #202124;
}

.header-right {
  display: flex;
  gap: 4px;
}

.header-menu-row {
  display: flex;
  gap: 4px;
  padding: 4px 16px;
  border-top: 1px solid #F1F3F4;
}

.menu-item {
  font-size: 14px;
  color: #444746;
  border-radius: 4px;
  padding: 0 8px;
  min-height: 32px;
}

.menu-item:hover {
  background: #F1F3F4;
}

.spreadsheet-container {
  flex: 1;
  height: calc(100vh - 80px);
  overflow: hidden;
}
</style>
