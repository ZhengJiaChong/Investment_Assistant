<template>
  <div class="fufan-layout">
    <!-- 左侧导航栏 (仿 fufan-chat 风格) -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <el-icon class="logo-icon"><TrendCharts /></el-icon>
        <span class="app-title">投资助手</span>
      </div>
      
      <div class="new-chat-btn">
        <el-button type="primary" :icon="Plus" @click="clearChat" block>
          开启新对话
        </el-button>
      </div>

      <div class="history-list">
        <div class="history-label">快捷指令</div>
        <div 
          v-for="(action, index) in quickActions" 
          :key="index"
          class="history-item"
          @click="useQuickAction(action)"
        >
          <el-icon><component :is="action.icon" /></el-icon>
          <span>{{ action.label }}</span>
        </div>
      </div>

      <div class="sidebar-footer">
        <div class="model-badge">
          <el-icon><Cpu /></el-icon>
          <span>{{ currentModel }}</span>
        </div>
      </div>
    </aside>

    <!-- 右侧主聊天区 -->
    <main class="chat-main">
      <div class="chat-container">
        <!-- 消息列表 -->
        <div class="message-wrapper" ref="messageContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <div class="welcome-card">
              <h2>你好，我是你的投资分析助手</h2>
              <p>我可以帮你查询股票行情、生成技术图表或预测未来走势。</p>
              <div class="suggestion-chips">
                <el-tag 
                  v-for="tag in ['贵州茅台近一年走势', '预测明日收盘价', '检测超买超卖点']" 
                  :key="tag"
                  class="suggestion-tag"
                  @click="userInput = tag"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>
          </div>

          <div 
            v-for="(msg, index) in messages" 
            :key="index" 
            class="message-row"
            :class="msg.role"
            v-show="msg.content || msg.role === 'user' || (msg.role === 'assistant' && isLoading && index === messages.length - 1)"
          >
            <div class="avatar">
              <el-icon v-if="msg.role === 'user'"><User /></el-icon>
              <el-icon v-else><Service /></el-icon>
            </div>
            <div class="message-bubble">
              <!-- 加载中显示状态指示器 -->
              <div v-if="!msg.content && isLoading && index === messages.length - 1" class="streaming-status">
                <div class="thinking-dots">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                </div>
                <span class="status-text">AI 正在思考中...</span>
              </div>
              <!-- 有内容时显示文字 -->
              <div v-else class="message-content">
                <div class="message-text" v-html="formatMessage(msg.content)"></div>
                <span v-if="isLoading && index === messages.length - 1" class="cursor-blink">▍</span>
              </div>
              <div v-if="msg.images && msg.images.length > 0" class="image-grid">
                <el-image 
                  v-for="(img, i) in msg.images" 
                  :key="i"
                  :src="img" 
                  :preview-src-list="msg.images"
                  fit="cover"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 底部输入框 -->
        <div class="input-area">
          <div class="input-box">
            <el-input
              v-model="userInput"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 4 }"
              placeholder="输入任何问题..."
              @keyup.enter.ctrl="sendMessage"
              :disabled="isLoading"
              resize="none"
            />
            <el-button 
              type="primary" 
              circle 
              :icon="Promotion"
              @click="sendMessage"
              :loading="isLoading"
              :disabled="!userInput.trim()"
              class="send-btn"
            />
          </div>
          <div class="input-tip">按 Ctrl + Enter 发送</div>
        </div>
      </div>
    </main>
  </div>
  <!-- 图片预览对话框 -->
  <el-dialog
    v-model="previewVisible"
    width="90vw"
    top="5vh"
    :show-close="true"
    class="image-preview-dialog"
  >
    <div class="preview-container">
      <el-image
        :src="previewImageUrl"
        fit="contain"
        style="width: 100%; height: 85vh;"
      />
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { 
  TrendCharts, Plus, User, Service, Promotion, Cpu
} from '@element-plus/icons-vue'
import axios from 'axios'

const userInput = ref('')
const messages = ref([])
const isLoading = ref(false)
const messageContainer = ref(null)
const currentModel = ref('tencent/hy3-preview:free')

const quickActions = ref([
  { label: '收盘价走势', icon: 'TrendCharts', query: '查询贵州茅台2025年全年收盘价走势' },
  { label: '统计分析', icon: 'DataAnalysis', query: '统计2025年贵州茅台的日均成交量' },
  { label: '价格预测', icon: 'Monitor', query: '预测贵州茅台未来7天的收盘价' },
  { label: '异常检测', icon: 'Warning', query: '检测贵州茅台近一年超买超卖点' },
  { label: '周期分析', icon: 'Histogram', query: '分析贵州茅台近一年周期性规律' },
  { label: '热点新闻', icon: 'Reading', query: '贵州茅台最近的热点新闻' },
])

const formatMessage = (content) => {
  if (!content) return ''
  let formatted = content
    // 先处理代码块
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 处理加粗和斜体
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // 处理 Markdown 图片 ![alt](url)
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, url) => {
      // 确保 URL 是绝对路径
      const fullUrl = url.startsWith('http') ? url : `http://localhost:8000${url}`
      // 添加 data-url 属性用于点击预览
      return `<img src="${fullUrl}" alt="${alt}" class="markdown-image" loading="lazy" data-preview="true" />`
    })
    // 处理链接
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    // 处理换行
    .replace(/\n/g, '<br>')
  return formatted
}

// 图片预览功能
const previewVisible = ref(false)
const previewImageUrl = ref('')

const handleImagePreview = (event) => {
  if (event.target.tagName === 'IMG' && event.target.dataset.preview === 'true') {
    previewImageUrl.value = event.target.src
    previewVisible.value = true
  }
}

onMounted(() => {
  // 监听消息区域的点击事件
  const messageWrapper = document.querySelector('.message-wrapper')
  if (messageWrapper) {
    messageWrapper.addEventListener('click', handleImagePreview)
  }
})

onUnmounted(() => {
  const messageWrapper = document.querySelector('.message-wrapper')
  if (messageWrapper) {
    messageWrapper.removeEventListener('click', handleImagePreview)
  }
})

const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

const clearChat = () => {
  messages.value = []
}

const useQuickAction = (action) => {
  userInput.value = action.query
  sendMessage()
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const userMessage = userInput.value.trim()
  messages.value.push({ role: 'user', content: userMessage, images: [] })
  userInput.value = ''
  isLoading.value = true
  
  // 先添加一个空的助手消息
  messages.value.push({ role: 'assistant', content: '', images: [] })
  const assistantIndex = messages.value.length - 1  // 获取最后一条消息的索引
  
  await scrollToBottom()

  try {
    const response = await fetch('http://localhost:8000/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage,
        history: messages.value.slice(0, -1).slice(-10)  // 排除刚添加的空消息
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'content') {
              // 直接追加到当前助手消息
              messages.value[assistantIndex].content += data.data
              await scrollToBottom()
            }
          } catch (e) {
            console.error('解析流数据失败:', e)
          }
        }
      }
    }
    
    // 如果内容为空，显示默认提示
    if (!messages.value[assistantIndex].content) {
      messages.value[assistantIndex].content = '抱歉，我暂时无法回答这个问题。'
    }
  } catch (error) {
    console.error('请求失败:', error)
    messages.value[assistantIndex].content = `请求失败：${error.message}`
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}
</script>

<style scoped>
/* 隐藏全局滚动条 */
html, body {
  overflow: hidden !important;
  scrollbar-width: none !important; /* Firefox */
  -ms-overflow-style: none !important; /* IE/Edge */
}

html::-webkit-scrollbar, body::-webkit-scrollbar {
  display: none !important; /* Chrome/Safari */
}

.fufan-layout {
  display: flex;
  height: 100vh;
  background-color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden; /* 隐藏整个布局的滚动条 */
}

/* 隐藏 WebKit 浏览器的滚动条 */
.fufan-layout ::-webkit-scrollbar {
  display: none;
}

/* 隐藏 Firefox 浏览器的滚动条 */
.fufan-layout {
  scrollbar-width: none;
}

/* 左侧导航栏 */
.sidebar {
  width: 260px;
  background: #f9fafb;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  padding: 20px;
  transition: all 0.3s;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  color: #111827;
  font-weight: 600;
  font-size: 18px;
}

.logo-icon {
  font-size: 24px;
  color: #409eff;
}

.new-chat-btn {
  margin-bottom: 24px;
}

.history-label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: #4b5563;
  font-size: 14px;
  transition: background 0.2s;
}

.history-item:hover {
  background: #e5e7eb;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.model-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
  background: #fff;
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
}

/* 右侧主聊天区 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.chat-container {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.message-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 40px 20px;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.message-wrapper::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.welcome-card {
  text-align: center;
  max-width: 600px;
}

.welcome-card h2 {
  font-size: 28px;
  color: #111827;
  margin-bottom: 12px;
}

.welcome-card p {
  color: #6b7280;
  margin-bottom: 32px;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.suggestion-tag {
  cursor: pointer;
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 20px;
}

.message-row {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  flex-shrink: 0;
}

.message-row.user .avatar {
  background: #409eff;
  color: white;
}

.message-bubble {
  max-width: 75%;
  width: fit-content;
  padding: 12px 18px;
  border-radius: 12px;
  background: #f3f4f6;
  color: #1f2937;
  line-height: 1.6;
  font-size: 15px;
  overflow: hidden;
  word-wrap: break-word;
}

/* 确保 v-html 渲染的图片不会超出气泡 */
.message-bubble .message-text img {
  max-width: 60% !important;
  width: 60% !important;
  height: auto !important;
  max-height: 450px !important;
  object-fit: contain;
  display: block !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

.message-row.user .message-bubble {
  background: #409eff;
  color: white;
}

.thinking {
  display: flex;
  gap: 4px;
  padding: 16px;
}

.dot {
  width: 6px;
  height: 6px;
  background: #9ca3af;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.message-text {
  word-wrap: break-word;
  line-height: 1.6;
  display: inline;
}

.message-content {
  display: inline;
}

/* 流式输出状态指示器 */
.streaming-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
}

.thinking-dots {
  display: flex;
  gap: 4px;
}

.thinking-dots .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  animation: thinking 1.4s infinite ease-in-out both;
}

.thinking-dots .dot:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots .dot:nth-child(2) { animation-delay: -0.16s; }
.thinking-dots .dot:nth-child(3) { animation-delay: 0s; }

.status-text {
  color: #909399;
  font-size: 14px;
  font-style: italic;
}

@keyframes thinking {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 流式输出时的光标 */
.cursor-blink {
  display: inline-block;
  color: #409eff;
  font-weight: bold;
  font-size: 16px;
  line-height: 1;
  animation: blink 1s infinite;
  margin-left: 2px;
  vertical-align: text-bottom;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Markdown 图片样式 */
.markdown-image {
  max-width: 60% !important;
  width: 60% !important;
  height: auto !important;
  max-height: 450px !important;
  object-fit: contain;
  border-radius: 8px;
  margin-top: 12px;
  margin-bottom: 8px;
  cursor: zoom-in;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: block !important;
  margin-left: auto !important;
  margin-right: auto !important;
  /* 图片加载时的淡入效果 */
  opacity: 0;
  animation: imageFadeIn 0.6s ease forwards;
}

.markdown-image:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

@keyframes imageFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.input-area {
  padding: 24px;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
}

.input-box {
  position: relative;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 12px;
  background: #f9fafb;
  transition: all 0.2s;
}

.input-box:focus-within {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
  background: #fff;
}

.send-btn {
  position: absolute;
  right: 16px;
  bottom: 16px;
}

.input-tip {
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar { display: none; }
  .chat-container { max-width: 100%; }
}
</style>

<style>
/* 隐藏全局滚动条（非 scoped，作用于 html/body） */
html, body {
  overflow: hidden !important;
  scrollbar-width: none !important;
  -ms-overflow-style: none !important;
}

html::-webkit-scrollbar, body::-webkit-scrollbar {
  display: none !important;
}
</style>

<!-- 全局样式：v-html 动态渲染的图片样式 -->
<style>
.markdown-image {
  max-width: 60% !important;
  width: 60% !important;
  height: auto !important;
  max-height: 450px !important;
  object-fit: contain;
  border-radius: 8px;
  margin: 12px auto 8px auto !important;
  cursor: zoom-in;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: block !important;
  opacity: 0;
  animation: imageFadeIn 0.6s ease forwards;
}

.markdown-image:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

@keyframes imageFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
