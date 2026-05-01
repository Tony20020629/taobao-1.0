<template>
  <div class="chat-page">
    <div class="chat-container">
      <el-card class="chat-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div>
              <span style="font-size: 18px; font-weight: bold;">💬 智能价格决策助手</span>
              <div style="font-size: 12px; color: #909399; margin-top: 4px;">基于AI对话交互，查询价格数据、解读趋势、辅助购买决策</div>
            </div>
            <el-button type="danger" size="small" @click="clearChat">清空对话</el-button>
          </div>
        </template>
        <div class="chat-messages" ref="messagesRef">
          <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
            <div class="message-avatar">
              <el-avatar :size="36" :style="{ background: msg.role === 'user' ? '#409eff' : '#67c23a' }">
                {{ msg.role === 'user' ? 'U' : 'AI' }}
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(msg.content)"></div>
              <div class="message-time">{{ msg.time }}</div>
            </div>
          </div>
          <div v-if="isTyping" class="message assistant">
            <div class="message-avatar">
              <el-avatar :size="36" style="background: #67c23a">AI</el-avatar>
            </div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
        <div class="chat-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入您的问题，如：查询XX商品的价格趋势、建议购买时机等..."
            @keyup.enter="handleSend"
            resize="none"
          />
          <el-button type="primary" @click="handleSend" :disabled="!inputMessage.trim()" :loading="isTyping">
            发送
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { chatAPI } from '../api/goods'

const messages = ref([])
const inputMessage = ref('')
const isTyping = ref(false)
const sessionId = ref('')
const messagesRef = ref(null)

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    content: '你好！我是淘宝商品价格智能决策助手。\n\n我可以帮您：\n• 查询商品价格走势\n• 分析价格高低水位\n• 给出购买时机建议\n\n请问有什么可以帮您？',
    time: getCurrentTime()
  })
})

const handleSend = async () => {
  if (!inputMessage.value.trim() || isTyping.value) return

  const userMsg = {
    role: 'user',
    content: inputMessage.value,
    time: getCurrentTime()
  }

  messages.value.push(userMsg)
  const userInput = inputMessage.value
  inputMessage.value = ''
  scrollToBottom()

  isTyping.value = true

  try {
    const res = await chatAPI.sendMessage(userInput, sessionId.value)
    sessionId.value = res.session_id
    
    const aiMsg = {
      role: 'assistant',
      content: res.reply,
      time: getCurrentTime()
    }
    messages.value.push(aiMsg)
  } catch (error) {
    ElMessage.error('发送消息失败')
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const clearChat = () => {
  sessionId.value = ''
  messages.value = [{
    role: 'assistant',
    content: '对话已清空。请问有什么可以帮您？',
    time: getCurrentTime()
  }]
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const getCurrentTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatMessage = (content) => {
  return content.replace(/\n/g, '<br/>')
}
</script>

<style scoped>
.chat-page {
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
  padding: 20px 40px;
}

.chat-container {
  max-width: 900px;
  margin: 0 auto;
}

.chat-card {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
}

.message {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}

.message.user .message-text {
  background: #409eff;
  color: white;
  border-top-right-radius: 4px;
}

.message.assistant .message-text {
  background: #f0f2f5;
  color: #303133;
  border-top-left-radius: 4px;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  padding: 0 4px;
}

.message.user .message-time {
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f0f2f5;
  border-radius: 12px;
  border-top-left-radius: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
}

.chat-input {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.chat-input .el-input {
  flex: 1;
}

.chat-input .el-button {
  align-self: flex-end;
}
</style>
