<template>
  <q-page class="files-page">
    <div class="files-container">
      <!-- Page Header -->
      <div class="page-header q-mb-md">
        <div class="text-h5">Files</div>
        <q-tabs
          v-model="viewMode"
          dense no-caps
          class="bg-white tabs-style"
          active-color="white"
          active-bg-color="primary"
          indicator-color="primary"
          align="right"
        >
          <q-tab name="list" icon="list" />
          <q-tab name="grid" icon="grid_view" />
        </q-tabs>
      </div>
      <div class="sections-row">
        <!-- Left Section: Recent -->
        <div class="section-left q-mb-md">
          <q-card class="section-card">
            <q-card-section class="section-header">
              <div class="text-subtitle1 text-bold">Recent</div>
            </q-card-section>
            <q-card-section class="section-content q-pa-none">
              <!-- Recent List View -->
              <q-list v-if="viewMode === 'list'" separator class="files-list">
                <q-item
                  v-for="item in displayedRecentItems"
                  :key="item.id"
                  clickable
                  @click="item.type === 'folder' ? openFolder(item) : openFile(item)"
                  class="file-list-item"
                >
                  <q-item-section avatar>
                    <q-icon
                      :name="item.type === 'folder' ? 'folder' : getFileIcon(item.fileType)"
                      :color="item.type === 'folder' ? 'amber' : getFileColor(item.fileType)"
                      size="32px"
                    />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ item.name }}</q-item-label>
                    <q-item-label caption>{{ item.type === 'folder' ? `${item.itemCount} items` : item.modified }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="recentItems.length > 10 && !showAllRecent" clickable @click="showAllRecent = true">
                  <q-item-section>
                    <q-item-label class="text-primary text-center">View more</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>

              <!-- Recent Grid View -->
              <div v-else>
                <div class="files-grid">
                  <div
                    v-for="item in displayedRecentItems"
                    :key="item.id"
                    class="file-item"
                    @click="item.type === 'folder' ? openFolder(item) : openFile(item)"
                  >
                    <q-card class="file-card">
                      <q-card-section class="file-icon">
                        <q-icon
                          :name="item.type === 'folder' ? 'folder' : getFileIcon(item.fileType)"
                          :color="item.type === 'folder' ? 'amber' : getFileColor(item.fileType)"
                          size="48px"
                        />
                      </q-card-section>
                      <q-card-section class="file-info">
                        <div class="file-name">{{ item.name }}</div>
                        <div class="file-meta">{{ item.type === 'folder' ? `${item.itemCount} items` : item.modified }}</div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
                <q-btn
                  v-if="recentItems.length > 10 && !showAllRecent"
                  flat
                  color="primary"
                  label="View more"
                  class="full-width q-mt-md"
                  @click="showAllRecent = true"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Right Section: Pinned -->
        <div class="section-right q-mb-md">
          <q-card class="section-card">
            <q-card-section class="section-header">
              <div class="text-subtitle1 text-bold">Pinned</div>
            </q-card-section>
            <q-card-section class="section-content q-pa-none">
              <!-- Pinned List View -->
              <q-list v-if="viewMode === 'list'" separator class="files-list">
                <q-item
                  v-for="file in pinnedFiles"
                  :key="file.id"
                  clickable
                  @click="openFile(file)"
                  class="file-list-item"
                >
                  <q-item-section avatar>
                    <q-icon :name="getFileIcon(file.type)" :color="getFileColor(file.type)" size="32px" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ file.name }}</q-item-label>
                    <q-item-label caption>{{ file.modified }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-btn flat round dense icon="push_pin" color="amber" />
                  </q-item-section>
                </q-item>
              </q-list>

              <!-- Pinned Grid View -->
              <div v-else class="files-grid">
                <div
                  v-for="file in pinnedFiles"
                  :key="file.id"
                  class="file-item"
                  @click="openFile(file)"
                >
                  <q-card class="file-card">
                    <q-card-section class="file-icon">
                      <q-icon :name="getFileIcon(file.type)" :color="getFileColor(file.type)" size="48px" />
                    </q-card-section>
                    <q-card-section class="file-info">
                      <div class="file-name">{{ file.name }}</div>
                      <div class="file-meta">{{ file.modified }}</div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- File Manager Section -->
      <div class="file-manager-section q-mt-">
        <div class="file-manager-header flex items-center justify-between q-pa-md">
          <div class="breadcrumb flex items-center q-gutter-md">
            <div class="text-h6">All Files</div>
            <q-breadcrumbs>
              <template v-slot:separator>
                <q-icon size="1.5em" name="chevron_right" color="primary" />
              </template>
              <q-breadcrumbs-el icon="home" label="Home" @click="navigateToRoot" />
              <q-breadcrumbs-el 
                v-for="(folder, index) in currentPath" 
                :key="index"
                :label="folder.name"
                @click="navigateToFolder(index)"
              />
            </q-breadcrumbs>
          </div>
          <div>
            <q-btn label="New" dense unelevated color="primary" icon-right="add" class="q-px-md" />
          </div>
        </div>

        <!-- File Manager List View -->
        <q-list v-if="viewMode === 'list'" separator class="files-list">
          <q-item
            v-for="item in currentFolderContents"
            :key="item.id"
            clickable
            @click="item.type === 'folder' ? enterFolder(item) : openFile(item)"
            class="file-list-item"
          >
            <q-item-section avatar>
              <q-icon 
                :name="item.type === 'folder' ? 'folder' : getFileIcon(item.fileType)" 
                :color="item.type === 'folder' ? 'amber' : getFileColor(item.fileType)" 
                size="32px" 
              />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ item.name }}</q-item-label>
              <q-item-label caption>{{ item.type === 'folder' ? `${item.itemCount} items` : item.modified }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>

        <!-- File Manager Grid View -->
        <div v-else>
          <div class="files-grid">
            <div
              v-for="item in currentFolderContents"
              :key="item.id"
              class="file-item"
              @click="item.type === 'folder' ? enterFolder(item) : openFile(item)"
            >
              <q-card class="file-card">
                <q-card-section class="file-icon">
                  <q-icon 
                    :name="item.type === 'folder' ? 'folder' : getFileIcon(item.fileType)" 
                    :color="item.type === 'folder' ? 'amber' : getFileColor(item.fileType)" 
                    size="48px" 
                  />
                </q-card-section>
                <q-card-section class="file-info">
                  <div class="file-name">{{ item.name }}</div>
                  <div class="file-meta">{{ item.type === 'folder' ? `${item.itemCount} items` : item.modified }}</div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFileNavigationStore } from 'stores/file-navigation-store'

const fileNavigationStore = useFileNavigationStore()

const viewMode = ref('list')
const showAllRecent = ref(false)
const currentPath = ref([])

onMounted(() => {
  currentPath.value = fileNavigationStore.getCurrentPath
})

const fileSystem = ref({
  root: [
    { id: 1, name: 'Documents', type: 'folder', itemCount: 15 },
    { id: 2, name: 'Images', type: 'folder', itemCount: 23 },
    { id: 3, name: 'Projects', type: 'folder', itemCount: 8 },
    { id: 4, name: 'Reports', type: 'folder', itemCount: 12 },
    { id: 5, name: 'Templates', type: 'folder', itemCount: 34 },
    { id: 6, name: 'Archive', type: 'folder', itemCount: 45 },
    { id: 7, name: 'readme.txt', type: 'file', fileType: 'document', modified: '1 week ago' },
    { id: 8, name: 'notes.md', type: 'file', fileType: 'document', modified: '2 days ago' }
  ],
  'Documents': [
    { id: 1, name: 'Contract.pdf', type: 'file', fileType: 'pdf', modified: '2 days ago' },
    { id: 2, name: 'Invoice.docx', type: 'file', fileType: 'document', modified: '1 week ago' },
    { id: 3, name: 'Meeting Notes.txt', type: 'file', fileType: 'document', modified: '3 days ago' },
    { id: 4, name: 'Work', type: 'folder', itemCount: 5 }
  ],
  'Images': [
    { id: 1, name: 'logo.png', type: 'file', fileType: 'image', modified: '1 day ago' },
    { id: 2, name: 'banner.jpg', type: 'file', fileType: 'image', modified: '2 days ago' },
    { id: 3, name: 'Screenshots', type: 'folder', itemCount: 12 }
  ],
  'Projects': [
    { id: 1, name: 'Project A', type: 'folder', itemCount: 8 },
    { id: 2, name: 'Project B', type: 'folder', itemCount: 15 },
    { id: 3, name: 'Project C', type: 'folder', itemCount: 6 }
  ],
  'Reports': [
    { id: 1, name: 'Q1 Report.xlsx', type: 'file', fileType: 'spreadsheet', modified: '1 month ago' },
    { id: 2, name: 'Q2 Report.xlsx', type: 'file', fileType: 'spreadsheet', modified: '2 weeks ago' },
    { id: 3, name: 'Annual Report.pdf', type: 'file', fileType: 'pdf', modified: '3 months ago' }
  ],
  'Templates': [
    { id: 1, name: 'Email Template.docx', type: 'file', fileType: 'document', modified: '1 month ago' },
    { id: 2, name: 'Slide Template.pptx', type: 'file', fileType: 'presentation', modified: '2 months ago' }
  ],
  'Archive': [
    { id: 1, name: '2023', type: 'folder', itemCount: 20 },
    { id: 2, name: '2022', type: 'folder', itemCount: 25 }
  ],
  'Work': [
    { id: 1, name: 'task1.docx', type: 'file', fileType: 'document', modified: '1 week ago' },
    { id: 2, name: 'task2.docx', type: 'file', fileType: 'document', modified: '2 weeks ago' }
  ],
  'Screenshots': [
    { id: 1, name: 'screen1.png', type: 'file', fileType: 'image', modified: '1 day ago' },
    { id: 2, name: 'screen2.png', type: 'file', fileType: 'image', modified: '2 days ago' }
  ],
  'Project A': [
    { id: 1, name: 'proposal.pdf', type: 'file', fileType: 'pdf', modified: '1 month ago' },
    { id: 2, name: 'budget.xlsx', type: 'file', fileType: 'spreadsheet', modified: '3 weeks ago' }
  ],
  'Project B': [
    { id: 1, name: 'design.fig', type: 'file', fileType: 'design', modified: '2 weeks ago' },
    { id: 2, name: 'mockup.png', type: 'file', fileType: 'image', modified: '1 week ago' }
  ],
  'Project C': [
    { id: 1, name: 'specs.pdf', type: 'file', fileType: 'pdf', modified: '1 week ago' }
  ],
  '2023': [
    { id: 1, name: 'old_file1.txt', type: 'file', fileType: 'document', modified: '1 year ago' },
    { id: 2, name: 'old_file2.txt', type: 'file', fileType: 'document', modified: '1 year ago' }
  ],
  '2022': [
    { id: 1, name: 'ancient_file.txt', type: 'file', fileType: 'document', modified: '2 years ago' }
  ]
})

const pinnedFiles = ref([
  { id: 1, name: 'Important Project.docx', type: 'document', modified: '2 hours ago' },
  { id: 2, name: 'Budget Report.xlsx', type: 'spreadsheet', modified: '1 day ago' },
  { id: 3, name: 'Presentation.pptx', type: 'presentation', modified: '3 days ago' }
])

const recentItems = ref([
  { id: 1, name: 'Project Proposal.docx', type: 'file', fileType: 'document', modified: '2 hours ago' },
  { id: 2, name: 'Marketing Materials', type: 'folder', itemCount: 15 },
  { id: 3, name: 'Budget Report.xlsx', type: 'file', fileType: 'spreadsheet', modified: '4 hours ago' },
  { id: 4, name: 'Project Documents', type: 'folder', itemCount: 23 },
  { id: 5, name: 'Presentation.pptx', type: 'file', fileType: 'presentation', modified: '6 hours ago' },
  { id: 6, name: 'Team Resources', type: 'folder', itemCount: 8 },
  { id: 7, name: 'Team Photo.jpg', type: 'file', fileType: 'image', modified: '8 hours ago' },
  { id: 8, name: 'Client Files', type: 'folder', itemCount: 12 },
  { id: 9, name: 'Meeting Notes.pdf', type: 'file', fileType: 'pdf', modified: '1 day ago' },
  { id: 10, name: 'Design Assets', type: 'folder', itemCount: 34 },
  { id: 11, name: 'Code Review.zip', type: 'file', fileType: 'archive', modified: '1 day ago' },
  { id: 12, name: 'Archive', type: 'folder', itemCount: 45 },
  { id: 13, name: 'Design Mockup.fig', type: 'file', fileType: 'design', modified: '2 days ago' },
  { id: 14, name: 'Templates', type: 'folder', itemCount: 10 },
  { id: 15, name: 'API Documentation.md', type: 'file', fileType: 'document', modified: '2 days ago' },
  { id: 16, name: 'Reports', type: 'folder', itemCount: 18 },
  { id: 17, name: 'Data Analysis.csv', type: 'file', fileType: 'spreadsheet', modified: '3 days ago' },
  { id: 18, name: 'Meeting Notes', type: 'folder', itemCount: 25 },
  { id: 19, name: 'Logo Design.png', type: 'file', fileType: 'image', modified: '3 days ago' },
  { id: 20, name: 'Presentations', type: 'folder', itemCount: 7 },
  { id: 21, name: 'Video Intro.mp4', type: 'file', fileType: 'video', modified: '4 days ago' },
  { id: 22, name: 'Audio Recording.mp3', type: 'file', fileType: 'audio', modified: '5 days ago' }
])

const displayedRecentItems = computed(() => {
  return showAllRecent.value ? recentItems.value : recentItems.value.slice(0, 10)
})

const currentFolderContents = computed(() => {
  if (currentPath.value.length === 0) {
    return fileSystem.value.root
  }
  const currentFolderName = currentPath.value[currentPath.value.length - 1].name
  return fileSystem.value[currentFolderName] || []
})

const enterFolder = (folder) => {
  currentPath.value.push(folder)
  fileNavigationStore.addToPath(folder)
}

const navigateToRoot = () => {
  currentPath.value = []
  fileNavigationStore.navigateToRoot()
}

const navigateToFolder = (index) => {
  currentPath.value = currentPath.value.slice(0, index + 1)
  fileNavigationStore.navigateToFolder(index)
}

const getFileIcon = (type) => {
  const icons = {
    document: 'description',
    spreadsheet: 'table_chart',
    presentation: 'slideshow',
    image: 'image',
    pdf: 'picture_as_pdf',
    archive: 'folder_zip',
    design: 'brush',
    video: 'videocam',
    audio: 'audiotrack'
  }
  return icons[type] || 'insert_drive_file'
}

const getFileColor = (type) => {
  const colors = {
    document: 'blue',
    spreadsheet: 'green',
    presentation: 'orange',
    image: 'purple',
    pdf: 'red',
    archive: 'amber',
    design: 'pink',
    video: 'cyan',
    audio: 'teal'
  }
  return colors[type] || 'grey'
}

const openFile = (file) => {
  console.log('Opening file:', file.name)
}

const openFolder = (folder) => {
  console.log('Opening folder:', folder.name)
}
</script>

<style scoped>
.files-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.files-container {
  padding: 16px;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tabs-style {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}

.sections-row {
  display: flex;
  gap: 16px;
  max-height: 300px;
}

.section-left,
.section-right {
  flex: 1;
}

.section-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: none;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  flex: 0 0 auto;
  position: sticky;
  top: 0;
  z-index: 1;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 12px 16px;
}

.section-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.file-manager-section {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}
.file-manager-header {
  border-bottom: 1px solid #e0e0e0;
}

.files-list,
.folders-list {
  background: white;
  border-radius: 8px;
}

.files-grid,
.folders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  padding: 16px;
}

.file-item,
.folder-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.file-item:hover,
.folder-item:hover {
  transform: translateY(-4px);
}

.file-card,
.folder-card {
  box-shadow: none;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}

.file-icon,
.folder-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.file-info,
.folder-info {
  padding: 12px;
  text-align: center;
}

.file-name,
.folder-name {
  font-weight: 500;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta,
.folder-meta {
  font-size: 12px;
  color: #757575;
  margin-top: 4px;
}
</style>
