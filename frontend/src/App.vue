<template>
  <div id="app">
    <el-container style="min-height: 100vh">
      <el-header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0 20px; display: flex; align-items: center; justify-content: space-between; height: 50px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <h1 style="color: white; margin: 0; font-size: 16px; font-weight: bold; white-space: nowrap;">🛒 淘宝商品价格监测系统</h1>
          <div style="display: flex; align-items: center; gap: 2px;">
            <div class="nav-item" :class="{ active: $route.path === '/home' }" @click="$router.push('/home')">
              <el-icon><HomeFilled /></el-icon>
              <span>主页</span>
            </div>
            <div class="nav-item" :class="{ active: $route.path === '/data' }" @click="$router.push('/data')">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据</span>
            </div>
            <div class="nav-item" :class="{ active: $route.path === '/chat' }" @click="$router.push('/chat')">
              <el-icon><ChatDotRound /></el-icon>
              <span>对话助手</span>
            </div>
          </div>
        </div>
        <div style="color: rgba(255,255,255,0.8); font-size: 12px; white-space: nowrap;">
          AI辅助开发 v1.0
        </div>
      </el-header>
      <el-main style="padding: 0;">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { HomeFilled, DataAnalysis, ChatDotRound } from '@element-plus/icons-vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  background-color: #f5f7fa;
}

#app {
  height: 100%;
}

.el-header {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  color: rgba(255, 255, 255, 0.85);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  white-space: nowrap;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.25);
  color: #ffd04b;
}
</style>
