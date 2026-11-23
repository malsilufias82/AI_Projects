<template>
  <q-page class="bg-grey-2 q-pa-lg">
    <div class="page-content q-gutter-y-lg">
      <div class="page-header row items-center justify-between q-col-gutter-md">
        <div>
          <h1 class="text-h4 text-weight-bold q-my-none">Onboarding Metrics</h1>
          <p class="text-grey-7 q-mt-sm q-mb-none">
            BGV, VCF, Client Credentials, and onboarded employee counts sourced from the onboarding collection.
          </p>
        </div>
        <q-btn outline icon="arrow_back" label="Back" to="/onboarding-dashboard" />
      </div>

      <div v-if="loading" class="row justify-center q-py-xl">
        <q-spinner color="primary" size="40px" />
      </div>

      <div v-else class="row q-col-gutter-md">
        <div v-for="metric in chartMetrics" :key="metric.key" class="col-12 col-md-6 col-lg-3">
          <q-card flat bordered class="metric-card">
            <q-card-section>
              <div class="text-body1 text-weight-medium q-mb-md">{{ metric.label }}</div>
              <div style="height: 260px;">
                <q-resize-observer @resize="() => metricChartRefresh(metric.key)" />
                <div :ref="setChartRef(metric.key)" style="width: 100%; height: 100%;" />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
defineOptions({
  name: 'OnboardingMetricsPage'
})

import { computed, onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import { api } from 'boot/axios'

const loading = ref(false)
const metricsData = ref({
  bgv: { Green: 0, Amber: 0, Red: 0 },
  vcf: { Green: 0, Amber: 0, Red: 0 },
  clientCredentials: { Green: 0, Amber: 0, Red: 0 },
  onboardedEmployees: { Completed: 0, InProgress: 0, Pending: 0, Cancelled: 0 }
})

const chartRefs = ref({})
const chartInstances = ref({})

const chartMetrics = computed(() => [
  { key: 'bgv', label: 'BGV', color: '#4f46e5' },
  { key: 'vcf', label: 'VCF', color: '#ec4899' },
  { key: 'clientCredentials', label: 'Client Credentials', color: '#f59e0b' },
  { key: 'onboardedEmployees', label: 'Onboarded Employees', color: '#10b981' }
])

const piePalette = {
  Completed: '#10b981',
  InProgress: '#f59e0b',
  Pending: '#94a3b8',
  Cancelled: '#ef4444',
  Green: '#10b981',
  Amber: '#f59e0b',
  Red: '#ef4444'
}

const statusOrder = ['Completed', 'InProgress', 'Pending', 'Cancelled']
const ragOrder = ['Green', 'Amber', 'Red']

function setChartRef(key) {
  return (el) => {
    chartRefs.value[key] = el
    if (el && chartInstances.value[key]) {
      chartInstances.value[key].resize()
    }
  }
}

function getChartData(metricKey) {
  const bucket = metricsData.value[metricKey] || {}
  const order = metricKey === 'onboardedEmployees' ? statusOrder : ragOrder

  return order
    .map((status) => ({
      value: Number(bucket[status] || 0),
      name: status,
      itemStyle: { color: piePalette[status] || '#94a3b8' }
    }))
    .filter((item) => item.value > 0)
}

function renderChart(metricKey) {
  const container = chartRefs.value[metricKey]
  if (!container) return

  const existing = chartInstances.value[metricKey]
  if (existing) {
    existing.dispose()
  }

  const chart = echarts.init(container)
  chartInstances.value[metricKey] = chart

  const data = getChartData(metricKey)
  const metricLabel = chartMetrics.value.find((metric) => metric.key === metricKey)?.label || metricKey
  const totalEmployees = data.reduce((sum, item) => sum + Number(item.value || 0), 0)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => `${metricLabel}<br />${params.name}: ${params.value}<br />Total employees: ${totalEmployees}`
    },
    legend: {
      bottom: 0,
      left: 'center',
      itemWidth: 12,
      itemHeight: 12,
      textStyle: { color: '#374151' }
    },
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '46%',
        style: {
          text: `Total\n${totalEmployees}`,
          fill: '#111827',
          fontSize: 16,
          fontWeight: 700,
          lineHeight: 22,
          textAlign: 'center'
        }
      }
    ],
    series: [
      {
        type: 'pie',
        radius: ['38%', '72%'],
        center: ['50%', '42%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          formatter: '{b}: {c}',
          color: '#111827',
          fontSize: 11
        },
        labelLine: {
          length: 10,
          length2: 6
        },
        data,
        itemStyle: {
          borderWidth: 2,
          borderColor: '#ffffff'
        }
      }
    ]
  }

  chart.setOption(option)
  chart.resize()
}

function metricChartRefresh(metricKey) {
  renderChart(metricKey)
}

async function fetchOnboardingMetrics() {
  loading.value = true
  try {
    const { data } = await api.get('/v1/users/onboarding/metrics')
    metricsData.value = {
      bgv: data?.bgv || { Green: 0, Amber: 0, Red: 0 },
      vcf: data?.vcf || { Green: 0, Amber: 0, Red: 0 },
      clientCredentials: data?.clientCredentials || { Green: 0, Amber: 0, Red: 0 },
      onboardedEmployees: data?.onboardedEmployees || { Completed: 0, InProgress: 0, Pending: 0, Cancelled: 0 }
    }

    chartMetrics.value.forEach((metric) => {
      renderChart(metric.key)
    })
  } catch (error) {
    console.error('Error loading onboarding metrics:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchOnboardingMetrics()
})

onUnmounted(() => {
  Object.values(chartInstances.value).forEach((chart) => chart.dispose())
})
</script>

<style scoped>
.page-content {
  max-width: 1440px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.metric-card {
  min-height: 340px;
}
</style>
