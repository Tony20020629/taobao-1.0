<template>
  <div class="data-page">
    <el-row :gutter="20" style="padding: 30px 40px;">
      <el-col :span="24">
        <el-card class="filter-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📊 数据统计分析</span>
            </div>
          </template>
          <el-form :model="filterForm" inline>
            <el-form-item label="选择商品">
              <el-select v-model="filterForm.goodsId" placeholder="请选择商品" style="width: 200px;" @change="loadData">
                <el-option v-for="goods in goodsList" :key="goods.id" :label="goods.name" :value="goods.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadData" :disabled="!filterForm.goodsId">查询</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="padding: 0 40px 20px;">
      <el-col :span="6" v-for="stat in priceStats" :key="stat.label">
        <el-card class="price-stat-card" shadow="hover">
          <div class="price-stat-content">
            <div class="price-stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
            <div class="price-stat-label">{{ stat.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="padding: 0 40px 30px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📈 价格趋势图</span>
            </div>
          </template>
          <div ref="chartRef" style="width: 100%; height: 400px;"></div>
          <div v-if="priceTrend.length === 0" style="text-align: center; padding: 40px; color: #909399;">
            暂无价格数据，请先添加商品并启动监测
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="padding: 0 40px 30px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📋 历史价格记录</span>
            </div>
          </template>
          <el-table :data="historyList" style="width: 100%" v-loading="loading">
            <el-table-column prop="collected_at" label="采集时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.collected_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="120">
              <template #default="{ row }">
                <span style="color: #f56c6c; font-weight: bold;">¥{{ row.price }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="change_type" label="价格变化" width="120">
              <template #default="{ row }">
                <el-tag :type="getChangeType(row.change_type)">
                  {{ getChangeText(row.change_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="promotion_info" label="促销信息" min-width="200" />
          </el-table>
          <div v-if="historyList.length === 0" style="text-align: center; padding: 40px; color: #909399;">
            暂无历史记录数据
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { goodsAPI } from '../api/goods'

const filterForm = reactive({
  goodsId: ''
})

const goodsList = ref([])

const priceStats = ref([
  { label: '当前价格', value: '¥0.00', color: '#409eff' },
  { label: '周期均价', value: '¥0.00', color: '#67c23a' },
  { label: '历史最低价', value: '¥0.00', color: '#e6a23c' },
  { label: '历史最高价', value: '¥0.00', color: '#f56c6c' }
])

const priceTrend = ref([])
const historyList = ref([])
const loading = ref(false)

const chartRef = ref(null)
let chartInstance = null

onMounted(() => {
  loadGoodsList()
  initChart()
})

const loadGoodsList = async () => {
  try {
    const data = await goodsAPI.getList()
    goodsList.value = data
  } catch (error) {
    goodsList.value = []
  }
}

const loadData = async () => {
  if (!filterForm.goodsId) {
    ElMessage.warning('请选择商品')
    return
  }
  try {
    loading.value = true
    const stats = await goodsAPI.getPriceStats(filterForm.goodsId)
    
    priceStats.value[0].value = `¥${stats.current_price?.toFixed(2) || '0.00'}`
    priceStats.value[1].value = `¥${stats.avg_price?.toFixed(2) || '0.00'}`
    priceStats.value[2].value = `¥${stats.min_price?.toFixed(2) || '0.00'}`
    priceStats.value[3].value = `¥${stats.max_price?.toFixed(2) || '0.00'}`
    
    priceTrend.value = stats.price_trend || []
    updateChart()
    
    const history = await goodsAPI.getPriceHistory(filterForm.goodsId)
    historyList.value = history
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const initChart = () => {
  nextTick(() => {
    if (chartRef.value) {
      chartInstance = echarts.init(chartRef.value)
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>价格: ¥{c}'
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
          data: []
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '¥{value}'
          }
        },
        series: [{
          name: '价格',
          type: 'line',
          smooth: true,
          itemStyle: { color: '#409eff' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ])
          },
          data: []
        }]
      }
      chartInstance.setOption(option)

      window.addEventListener('resize', () => {
        chartInstance.resize()
      })
    }
  })
}

const updateChart = () => {
  if (chartInstance && priceTrend.value.length > 0) {
    const times = priceTrend.value.map(item => {
      const d = new Date(item.collected_at)
      return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
    })
    const prices = priceTrend.value.map(item => item.price)
    
    chartInstance.setOption({
      xAxis: { data: times },
      series: [{ data: prices }]
    })
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')} ${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}

const getChangeType = (type) => {
  const map = { 'up': 'danger', 'down': 'success', 'new': 'warning', 'unchanged': 'info' }
  return map[type] || 'info'
}

const getChangeText = (type) => {
  const map = { 'up': '上涨', 'down': '下降', 'new': '新增', 'unchanged': '持平' }
  return map[type] || '持平'
}
</script>

<style scoped>
.data-page {
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.filter-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.price-stat-card {
  margin-bottom: 20px;
}

.price-stat-content {
  text-align: center;
  padding: 10px 0;
}

.price-stat-value {
  font-size: 28px;
  font-weight: bold;
}

.price-stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>
