/**
 * 商品相关API接口
 */
import api from './index'

export const goodsAPI = {
  /** 获取所有监测商品列表 */
  getList() {
    return api.get('/goods')
  },

  /** 添加新的商品监测任务 */
  add(data) {
    return api.post('/goods', data)
  },

  /** 切换商品监测状态 */
  toggle(goodsId) {
    return api.put(`/goods/${goodsId}/toggle`)
  },

  /** 删除商品监测任务 */
  delete(goodsId) {
    return api.delete(`/goods/${goodsId}`)
  },

  /** 获取指定商品的价格统计数据 */
  getPriceStats(goodsId) {
    return api.get(`/goods/${goodsId}/price-stats`)
  },

  /** 获取指定商品的价格历史记录 */
  getPriceHistory(goodsId) {
    return api.get(`/goods/${goodsId}/price-history`)
  }
}

/**
 * 系统统计API
 */
export const statsAPI = {
  /** 获取系统统计数据 */
  getSystemStats() {
    return api.get('/stats')
  }
}

/**
 * 对话机器人API
 */
export const chatAPI = {
  /** 发送对话消息 */
  sendMessage(message, sessionId = '') {
    return api.post('/chat', { message, session_id: sessionId })
  }
}
