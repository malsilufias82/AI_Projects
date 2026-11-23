<template>
  <q-page class="q-pa-md">
    <div class="text-h4 text-weight-bold q-mb-md">Page Manager</div>
    <div class="text-subtitle1 text-grey-6 q-mb-lg">Create and manage custom pages</div>

    <!-- Page List -->
    <q-card class="bg-white text-dark q-mb-lg">
      <q-card-section>
        <div class="row items-center justify-between">
          <div class="text-subtitle2">Your Pages</div>
          <q-btn
            unelevated
            color="primary"
            icon="add"
            label="Create New Page"
            @click="createNewPage"
          />
        </div>
      </q-card-section>
      <q-card-section>
        <q-list separator>
          <q-item
            v-for="page in pages"
            :key="page.id"
            clickable
            @click="editPage(page)"
          >
            <q-item-section avatar>
              <q-icon name="description" color="primary" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ page.name }}</q-item-label>
              <q-item-label caption>{{ page.description || 'No description' }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <div class="row q-gutter-xs">
                <q-btn
                  flat
                  dense
                  round
                  icon="edit"
                  color="info"
                  @click.stop="editPage(page)"
                />
                <q-btn
                  flat
                  dense
                  round
                  icon="delete"
                  color="negative"
                  @click.stop="deletePage(page.id)"
                />
              </div>
            </q-item-section>
          </q-item>
          <q-item v-if="pages.length === 0">
            <q-item-section>
              <div class="text-center text-grey-6 q-py-lg">
                <q-icon name="folder_open" size="48px" class="q-mb-md" />
                <div>No pages created yet</div>
                <div class="text-caption">Click "Create New Page" to get started</div>
              </div>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const pages = ref([
  {
    id: '1',
    name: 'Dashboard',
    description: 'Main dashboard page',
    route: '/custom-dashboard',
    components: []
  }
])

const createNewPage = () => {
  const newPage = {
    id: Date.now().toString(),
    name: 'New Page',
    description: '',
    route: `/custom-${Date.now()}`,
    components: []
  }
  pages.value.push(newPage)
  editPage(newPage)
}

const editPage = (page) => {
  router.push({
    name: 'PageBuilder',
    params: { pageId: page.id }
  })
}

const deletePage = (pageId) => {
  pages.value = pages.value.filter(p => p.id !== pageId)
}
</script>

<style scoped>
.q-card {
  border-radius: 12px;
}
</style>
