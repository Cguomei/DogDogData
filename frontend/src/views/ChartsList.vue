<template>
  <div class="charts-page">
    <h2>图表分析</h2>

    <div class="charts-grid">
      <div v-for="chart in chartList" :key="chart.name" class="chart-card">
        <el-card :header="chart.title" shadow="hover">
          <div v-if="chart.loading" class="chart-loading">
            <el-skeleton :rows="8" animated />
          </div>
          <div v-else-if="chart.error" class="chart-error">
            <el-alert type="error" :title="chart.error" :closable="false" show-icon />
          </div>
          <div v-else v-html="chart.html" class="chart-content" />
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { fetchChartHtml } from '../api'

const chartList = reactive([
  { name: 'scatter', title: '价格散点图', html: '', loading: true, error: '' },
  { name: 'line', title: '体重折线图', html: '', loading: true, error: '' },
  { name: 'bar', title: '级别柱状图', html: '', loading: true, error: '' },
  { name: 'hist', title: 'TOP10 直方图', html: '', loading: true, error: '' },
  { name: 'funnel', title: '价格段漏斗图', html: '', loading: true, error: '' },
  { name: 'map', title: '世界地图', html: '', loading: true, error: '' },
])

onMounted(() => {
  chartList.forEach((chart) => loadChart(chart))
})

async function loadChart(chart) {
  try {
    const { data } = await fetchChartHtml(chart.name)
    chart.html = data
  } catch (e) {
    chart.error = '加载失败: ' + e.message
  } finally {
    chart.loading = false
  }
}
</script>

<style scoped>
.charts-page {
  max-width: 1400px;
  margin: 0 auto;
}
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
  gap: 20px;
  margin-top: 10px;
}
.chart-card {
  min-height: 400px;
}
.chart-loading {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chart-content {
  display: flex;
  justify-content: center;
}
</style>
