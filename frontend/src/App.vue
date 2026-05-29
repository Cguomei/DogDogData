<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="header-title">🐕 狗狗数据分析系统</div>
      <el-menu
        mode="horizontal"
        :default-active="activeRoute"
        router
        class="header-menu"
      >
        <el-menu-item index="/dashboard">数据看板</el-menu-item>
        <el-menu-item index="/charts">图表分析</el-menu-item>
        <el-menu-item index="/food">狗粮数据</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeRoute = computed(() => route.path)
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
}
.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 24px;
}
.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-right: 40px;
  white-space: nowrap;
}
.header-menu {
  flex: 1;
  border-bottom: none !important;
}
</style>
