<template>
  <div class="dashboard">
    <h2>数据看板</h2>

    <el-skeleton :loading="loading" animated :count="4">
      <template #default>
        <el-row :gutter="20" class="stats-row">
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-value">{{ stats.total_dogs?.toLocaleString() || 0 }}</div>
              <div class="stat-label">狗狗总数</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-value">¥{{ stats.avg_price?.toLocaleString() || 0 }}</div>
              <div class="stat-label">平均价格</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-value">{{ stats.total_shops?.toLocaleString() || 0 }}</div>
              <div class="stat-label">店铺总数</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-value">{{ stats.total_breeds?.toLocaleString() || 0 }}</div>
              <div class="stat-label">品种总数</div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="12">
            <el-card header="热门品种 TOP5">
              <el-table :data="topBreeds" stripe size="small" v-if="topBreeds.length">
                <el-table-column prop="name" label="品种" />
                <el-table-column prop="count" label="数量" width="100" />
              </el-table>
              <el-empty v-else description="暂无数据" />
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card header="热门店铺 TOP5">
              <el-table :data="topShops" stripe size="small" v-if="topShops.length">
                <el-table-column prop="name" label="店铺" />
                <el-table-column prop="count" label="数量" width="100" />
              </el-table>
              <el-empty v-else description="暂无数据" />
            </el-card>
          </el-col>
        </el-row>
      </template>
    </el-skeleton>

    <el-alert
      v-if="error"
      type="error"
      :title="error"
      :closable="false"
      show-icon
      style="margin-top: 20px"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchDashboardStats } from '../api'

const loading = ref(true)
const error = ref('')
const stats = ref({})

const topBreeds = computed(() =>
  (stats.value.top_breeds || []).map(([name, count]) => ({ name, count }))
)
const topShops = computed(() =>
  (stats.value.top_shops || []).map(([name, count]) => ({ name, count }))
)

onMounted(async () => {
  try {
    const { data } = await fetchDashboardStats()
    stats.value = data
  } catch (e) {
    error.value = '数据加载失败: ' + e.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}
.stats-row {
  margin-top: 10px;
}
.stat-card {
  text-align: center;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>
