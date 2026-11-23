<template>
  <q-page class="q-pa-md">
    <div class="text-h4 text-weight-bold q-mb-md">Dashboard</div>
    <div class="text-subtitle1 text-grey-6 q-mb-lg">Project Overview & Analytics</div>

    <!-- Stats Cards -->
    <div class="row q-col-gutter-md q-mb-lg">
      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="bg-primary text-white">
          <q-card-section>
            <div class="text-subtitle2">Total Projects</div>
            <div class="text-h4 text-weight-bold">24</div>
            <div class="text-caption">+3 this month</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="bg-secondary text-white">
          <q-card-section>
            <div class="text-subtitle2">Active Tasks</div>
            <div class="text-h4 text-weight-bold">156</div>
            <div class="text-caption">12 pending review</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="bg-positive text-white">
          <q-card-section>
            <div class="text-subtitle2">Completed</div>
            <div class="text-h4 text-weight-bold">89</div>
            <div class="text-caption">94% completion rate</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="bg-warning text-white">
          <q-card-section>
            <div class="text-subtitle2">Team Members</div>
            <div class="text-h4 text-weight-bold">18</div>
            <div class="text-caption">Across 4 departments</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="row q-col-gutter-md q-mb-lg">
      <!-- Project Status Chart -->
      <div class="col-12 col-md-6">
        <q-card class="bg-white text-dark">
          <q-card-section>
            <div class="text-h6">Project Status Distribution</div>
          </q-card-section>
          <q-card-section>
            <div ref="statusChart" style="height: 300px;"></div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Task Completion Chart -->
      <div class="col-12 col-md-6">
        <q-card class="bg-white text-dark">
          <q-card-section>
            <div class="text-h6">Task Completion Trend</div>
          </q-card-section>
          <q-card-section>
            <div ref="trendChart" style="height: 300px;"></div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Department Performance Chart -->
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-card class="bg-white text-dark">
          <q-card-section>
            <div class="text-h6">Department Performance</div>
          </q-card-section>
          <q-card-section>
            <div ref="deptChart" style="height: 350px;"></div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const statusChart = ref(null)
const trendChart = ref(null)
const deptChart = ref(null)

let statusChartInstance = null
let trendChartInstance = null
let deptChartInstance = null

onMounted(() => {
  initStatusChart()
  initTrendChart()
  initDeptChart()
})

onUnmounted(() => {
  if (statusChartInstance) statusChartInstance.dispose()
  if (trendChartInstance) trendChartInstance.dispose()
  if (deptChartInstance) deptChartInstance.dispose()
})

const initStatusChart = () => {
  statusChartInstance = echarts.init(statusChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: '#fff',
      borderColor: '#0050D5',
      textStyle: { color: '#000' }
    },
    legend: {
      bottom: '0%',
      left: 'center',
      textStyle: { color: '#000' }
    },
    series: [
      {
        name: 'Project Status',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: '#000'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 8, name: 'In Progress', itemStyle: { color: '#0050D5' } },
          { value: 5, name: 'Completed', itemStyle: { color: '#10B981' } },
          { value: 6, name: 'Planning', itemStyle: { color: '#4A90E2' } },
          { value: 3, name: 'On Hold', itemStyle: { color: '#F59E0B' } },
          { value: 2, name: 'Review', itemStyle: { color: '#7C3AED' } }
        ]
      }
    ]
  }
  statusChartInstance.setOption(option)
}

const initTrendChart = () => {
  trendChartInstance = echarts.init(trendChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#0050D5',
      textStyle: { color: '#000' }
    },
    legend: {
      data: ['Completed', 'In Progress', 'Pending'],
      textStyle: { color: '#000' },
      top: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#eee' } }
    },
    series: [
      {
        name: 'Completed',
        type: 'line',
        smooth: true,
        data: [12, 18, 15, 22, 28, 35],
        itemStyle: { color: '#10B981' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0)' }
          ])
        }
      },
      {
        name: 'In Progress',
        type: 'line',
        smooth: true,
        data: [8, 12, 20, 18, 25, 22],
        itemStyle: { color: '#0050D5' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 80, 213, 0.3)' },
            { offset: 1, color: 'rgba(0, 80, 213, 0)' }
          ])
        }
      },
      {
        name: 'Pending',
        type: 'line',
        smooth: true,
        data: [5, 8, 10, 12, 15, 18],
        itemStyle: { color: '#F59E0B' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
            { offset: 1, color: 'rgba(245, 158, 11, 0)' }
          ])
        }
      }
    ]
  }
  trendChartInstance.setOption(option)
}

const initDeptChart = () => {
  deptChartInstance = echarts.init(deptChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#1D1D1D',
      borderColor: '#0050D5',
      textStyle: { color: '#fff' }
    },
    legend: {
      data: ['Projects', 'Tasks Completed'],
      textStyle: { color: '#fff' },
      top: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['Engineering', 'Design', 'Marketing', 'Sales', 'HR'],
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#eee' } }
    },
    series: [
      {
        name: 'Projects',
        type: 'bar',
        data: [8, 5, 4, 3, 4],
        itemStyle: { color: '#0050D5' }
      },
      {
        name: 'Tasks Completed',
        type: 'bar',
        data: [45, 32, 28, 22, 18],
        itemStyle: { color: '#4A90E2' }
      }
    ]
  }
  deptChartInstance.setOption(option)
}

// Handle window resize
window.addEventListener('resize', () => {
  if (statusChartInstance) statusChartInstance.resize()
  if (trendChartInstance) trendChartInstance.resize()
  if (deptChartInstance) deptChartInstance.resize()
})
</script>

<style scoped>
.q-card {
  border-radius: 12px;
}
</style>
