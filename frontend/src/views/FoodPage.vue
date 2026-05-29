<template>
  <div class="food-page">
    <h2>狗粮数据</h2>

    <el-skeleton :loading="statsLoading" animated :count="3">
      <template #default>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover" class="food-stat-card">
              <div class="stat-value">{{ foodStats.total_brands || 0 }}</div>
              <div class="stat-label">品牌总数</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="food-stat-card">
              <div class="stat-value">¥{{ foodStats.avg_price || 0 }}</div>
              <div class="stat-label">平均价格</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="food-stat-card">
              <div class="stat-value">{{ foodList.length > 0 ? '已加载' : '0' }}</div>
              <div class="stat-label">数据条目</div>
            </el-card>
          </el-col>
        </el-row>
      </template>
    </el-skeleton>

    <el-card header="狗粮列表" style="margin-top: 20px">
      <el-table
        :data="foodList"
        stripe
        v-loading="listLoading"
        empty-text="暂无数据"
      >
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="price" label="价格 (¥)" width="120" />
        <el-table-column prop="origin" label="产地" width="120" />
      </el-table>

      <el-alert
        v-if="listError"
        type="error"
        :title="listError"
        :closable="false"
        show-icon
        style="margin-top: 12px"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchFoodStats, fetchFoodList } from '../api'

const foodStats = ref({})
const foodList = ref([])
const statsLoading = ref(true)
const listLoading = ref(true)
const listError = ref('')

onMounted(async () => {
  try {
    const { data } = await fetchFoodStats()
    foodStats.value = data
  } catch (e) {
    console.error('Failed to load food stats:', e)
  } finally {
    statsLoading.value = false
  }

  try {
    const { data } = await fetchFoodList({ page: 1, per_page: 200 })
    foodList.value = data.foods || []
  } catch (e) {
    listError.value = '数据加载失败: ' + e.message
  } finally {
    listLoading.value = false
  }
})
</script>

<style scoped>
.food-page {
  max-width: 1200px;
  margin: 0 auto;
}
.food-stat-card {
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
