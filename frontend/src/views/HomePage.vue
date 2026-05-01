<template>
  <div class="home-page">
    <div class="hero-section">
      <el-row :gutter="20" style="padding: 40px 40px 0;">
        <el-col :span="24">
          <div class="hero-content">
            <h2 class="hero-title">🎯 淘宝商品价格监测助手</h2>
            <p class="hero-desc">实时监控商品价格变化，智能分析价格趋势，AI对话辅助购买决策</p>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="main-content">
      <el-row :gutter="20" style="padding: 0 40px 30px;">
        <el-col :span="24">
          <el-card class="input-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>➕ 添加监测商品</span>
              </div>
            </template>
            <el-form :model="form" label-width="100px" @submit.prevent="handleAdd">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="商品链接">
                    <el-input v-model="form.url" placeholder="请粘贴淘宝商品链接" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="监测频率">
                    <el-select v-model="form.frequency" placeholder="选择采集频率">
                      <el-option label="每1分钟" :value="1" />
                      <el-option label="每30分钟" :value="30" />
                      <el-option label="每1小时" :value="60" />
                      <el-option label="每6小时" :value="360" />
                      <el-option label="每天" :value="1440" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item>
                    <el-button type="primary" @click="handleAdd" :loading="loading">
                      添加监测
                    </el-button>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="padding: 0 40px 30px;">
        <el-col :span="6" v-for="stat in stats" :key="stat.label">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon" :style="{ background: stat.color }">
                <el-icon :size="30" color="#fff"><component :is="stat.icon" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="padding: 0 40px 30px;">
        <el-col :span="24">
          <el-card class="goods-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>📦 已监测商品</span>
                <el-button type="primary" size="small" @click="loadGoodsList">刷新</el-button>
              </div>
            </template>
            <el-table :data="goodsList" style="width: 100%" v-loading="loading">
              <el-table-column prop="name" label="商品名称" min-width="200" />
              <el-table-column prop="current_price" label="当前价格" width="120">
                <template #default="{ row }">
                  <span style="color: #f56c6c; font-weight: bold;">¥{{ formatPrice(row.current_price) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="avg_price" label="均价" width="120">
                <template #default="{ row }">
                  ¥{{ formatPrice(row.avg_price) }}
                </template>
              </el-table-column>
              <el-table-column prop="min_price" label="最低价" width="120">
                <template #default="{ row }">
                  <span style="color: #67c23a; font-weight: bold;">¥{{ formatPrice(row.min_price) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="max_price" label="最高价" width="120">
                <template #default="{ row }">
                  ¥{{ formatPrice(row.max_price) }}
                </template>
              </el-table-column>
              <el-table-column label="监测频率" width="120">
                <template #default="{ row }">
                  {{ formatFrequency(row.frequency) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'running' ? 'success' : 'info'">
                    {{ row.status === 'running' ? '监测中' : '未启动' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button type="success" size="small" @click="handleToggle(row)">
                    {{ row.status === 'running' ? '暂停' : '启动' }}
                  </el-button>
                  <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="goodsList.length === 0" style="text-align: center; padding: 40px; color: #909399;">
              暂无监测商品，请在上方添加商品链接
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Shop, Clock, Money, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { goodsAPI, statsAPI } from '../api/goods'

const form = reactive({
  url: '',
  frequency: 60
})

const loading = ref(false)

const stats = ref([
  { label: '监测商品数', value: 0, color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', icon: 'Shop' },
  { label: '运行中任务', value: 0, color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', icon: 'Clock' },
  { label: '今日采集次数', value: 0, color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', icon: 'TrendCharts' },
  { label: '低于均价商品', value: 0, color: 'linear-gradient(135deg, #43e97b 0%, #38f9d 100%)', icon: 'Money' }
])

const goodsList = ref([])

onMounted(() => {
  loadGoodsList()
  loadStats()
  setInterval(loadStats, 30000)
  setInterval(autoRefreshGoods, 60000)
})

const autoRefreshGoods = async () => {
  try {
    const data = await goodsAPI.getList()
    const hasPriceUpdate = data.some((item, index) => {
      const oldItem = goodsList.value[index]
      return oldItem && item.current_price !== oldItem.current_price
    })
    if (hasPriceUpdate) {
      goodsList.value = data
      ElMessage.info('价格数据已更新')
    }
  } catch (error) {
    // 静默失败
  }
}

const loadGoodsList = async () => {
  try {
    loading.value = true
    const data = await goodsAPI.getList()
    goodsList.value = data
  } catch (error) {
    ElMessage.error('加载商品列表失败')
    goodsList.value = []
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const data = await statsAPI.getSystemStats()
    stats.value[0].value = data.total_goods
    stats.value[1].value = data.running_tasks
    stats.value[2].value = data.today_collections
    stats.value[3].value = data.price_drop
  } catch (error) {
    // 静默失败
  }
}

const handleAdd = async () => {
  if (!form.url) {
    ElMessage.warning('请输入商品链接')
    return
  }
  try {
    loading.value = true
    await goodsAPI.add({
      url: form.url,
      name: '',
      frequency: form.frequency
    })
    ElMessage.success('商品添加成功')
    form.url = ''
    loadGoodsList()
    loadStats()
  } catch (error) {
    if (error.response?.status === 400) {
      ElMessage.warning('该商品链接已存在')
    } else {
      ElMessage.error('添加失败，请检查链接格式')
    }
  } finally {
    loading.value = false
  }
}

const handleToggle = async (row) => {
  try {
    await goodsAPI.toggle(row.id)
    const newStatus = row.status === 'running' ? 'stopped' : 'running'
    row.status = newStatus
    ElMessage.success(newStatus === 'running' ? '已启动监测' : '已暂停监测')
    loadStats()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该商品吗？相关的价格历史记录也会被删除', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await goodsAPI.delete(row.id)
    ElMessage.success('商品已删除')
    loadGoodsList()
    loadStats()
  } catch (error) {
    // 取消删除
  }
}

const formatFrequency = (minutes) => {
  if (minutes < 60) return `${minutes}分钟`
  if (minutes < 1440) return `${minutes / 60}小时`
  return `${minutes / 1440}天`
}

const formatPrice = (price) => {
  if (!price || price === 0) return '0.00'
  return parseFloat(price).toFixed(2)
}
</script>

<style scoped>
.home-page {
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding-bottom: 30px;
}

.hero-title {
  font-size: 32px;
  margin: 0 0 10px;
  text-align: center;
}

.hero-desc {
  font-size: 16px;
  opacity: 0.9;
  text-align: center;
}

.main-content {
  margin-top: -20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.input-card {
  margin-bottom: 20px;
}

.goods-card {
  margin-bottom: 20px;
}
</style>
