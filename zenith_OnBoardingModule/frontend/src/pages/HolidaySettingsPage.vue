<template>
  <q-page class="q-pa-lg">
    <div class="page-header q-mb-lg">
      <div class="text-h5">Holiday List</div>
      <div class="text-subtitle2 text-grey-7">Import a holiday schedule from a PDF.</div>
    </div>

    <q-card flat bordered>
      <q-card-section>
        <div class="text-h6">Import yearly holiday PDF</div>
        <div class="text-body2 text-grey-7 q-mt-xs">
          The PDF must include Holiday Name, Day, Date, and Type columns. Year is taken from Date.
        </div>
      </q-card-section>

      <q-card-section class="row items-center q-gutter-md">
        <q-file
          v-model="selectedFile"
          accept=".pdf,application/pdf"
          label="Choose holiday PDF"
          outlined
          dense
          clearable
          class="col-12 col-md-6"
          :disable="uploading"
        />
        <q-btn
          color="primary"
          label="Import PDF"
          icon="upload_file"
          :loading="uploading"
          :disable="!selectedFile || uploading"
          @click="importPdf"
        />
      </q-card-section>

      <q-card-section v-if="successMessage" class="q-pt-none">
        <q-banner class="bg-green-1 text-positive" rounded>{{ successMessage }}</q-banner>
      </q-card-section>
      <q-card-section v-if="errorMessage" class="q-pt-none">
        <q-banner class="bg-red-1 text-negative" rounded>{{ errorMessage }}</q-banner>
      </q-card-section>
    </q-card>

    <q-card flat bordered class="q-mt-lg">
      <q-card-section class="text-h6">Current year holidays</q-card-section>
      <q-table
        :rows="holidays"
        :columns="columns"
        row-key="date"
        :loading="loading"
        flat
        :pagination="{ rowsPerPage: 0 }"
        no-data-label="No holidays imported for this year"
      />
    </q-card>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from 'boot/axios'

const selectedFile = ref(null)
const holidays = ref([])
const loading = ref(false)
const uploading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const columns = [
  { name: 'holiday_name', label: 'Holiday Name', field: 'holiday_name', align: 'left' },
  { name: 'day', label: 'Day', field: 'day', align: 'left' },
  { name: 'date', label: 'Date', field: 'date', align: 'left' },
  { name: 'year', label: 'Year', field: 'year', align: 'left' },
  { name: 'type', label: 'Type', field: 'type', align: 'left' }
]

const loadHolidays = async () => {
  loading.value = true
  try {
    const response = await api.get('/v1/holidays')
    holidays.value = response.data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Could not load the holiday list.'
  } finally {
    loading.value = false
  }
}

const importPdf = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  successMessage.value = ''
  errorMessage.value = ''

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const response = await api.post('/v1/holidays/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    successMessage.value = response.data.message
    selectedFile.value = null
    await loadHolidays()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Could not import the holiday PDF.'
  } finally {
    uploading.value = false
  }
}

onMounted(loadHolidays)
</script>
