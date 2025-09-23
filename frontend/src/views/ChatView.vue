<template>
  <div class="flex h-screen bg-gray-50">
    <!-- 左侧聊天界面 -->
    <div class="flex-1 flex flex-col">
      <!-- 聊天标题栏 -->
      <div class="bg-white border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-semibold text-gray-800">Teaching Session: Dijkstra's Algorithm</h1>
            <p class="text-sm text-gray-600">You are the teacher 👨‍🏫 | Algorithm Apprentice is learning 👨‍🎓</p>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-green-500 rounded-full"></div>
            <span class="text-sm text-gray-500">Online</span>
          </div>
        </div>
      </div>

      <!-- 聊天消息区域 -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4" ref="messagesContainer">
        <div v-if="messages.length === 0" class="text-center text-gray-500 mt-20">
          <div class="text-4xl mb-4">🎓</div>
          <p>Ready to teach Dijkstra's algorithm? The Algorithm Apprentice is waiting to learn!</p>
        </div>
        
        <div
          v-for="message in messages"
          :key="message.id"
          :class="[
            'flex',
            message.type === 'user' ? 'justify-end' : 'justify-start'
          ]"
        >
          <div
            :class="[
              'max-w-xs lg:max-w-md px-4 py-2 rounded-lg',
              message.type === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-white text-gray-800 border border-gray-200'
            ]"
          >
            <p class="text-sm">{{ message.content }}</p>
            <p class="text-xs mt-1 opacity-70">
              {{ formatTime(message.timestamp) }}
            </p>
          </div>
        </div>
        
        <!-- 正在输入指示器 -->
        <div v-if="isTyping" class="flex justify-start">
          <div class="bg-white text-gray-800 border border-gray-200 px-4 py-2 rounded-lg">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="bg-white border-t border-gray-200 p-4">
        <form @submit.prevent="sendMessage" class="flex space-x-4">
          <input
            v-model="newMessage"
            type="text"
            placeholder="Explain Dijkstra's algorithm to your student..."
            class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            :disabled="isConnecting"
          />
          <button
            type="submit"
            :disabled="!newMessage.trim() || isConnecting"
            class="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>

    <!-- 右侧仪表板 -->
    <div class="w-80 bg-white border-l border-gray-200">
      <Dashboard :stats="dashboardStats" :messages="messages" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import Dashboard from '@/components/Dashboard.vue'

interface Message {
  id: number
  type: 'user' | 'bot'
  content: string
  timestamp: string
  sender: string
}

interface DashboardStats {
  total_messages: number
  thinking_times: number[]
  avg_thinking_time: number
  last_thinking_time: number
  // active_connections: number
  // uptime: string
  // last_message_time: string | null
}

const messages = ref<Message[]>([])
const newMessage = ref('')
const isConnecting = ref(true)
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement>()
const dashboardStats = ref<DashboardStats>({
  total_messages: 0,
  thinking_times: [],
  avg_thinking_time: 0,
  last_thinking_time: 0
  // active_connections: 0,
  // uptime: '运行中',
  // last_message_time: null
})

let ws: WebSocket | null = null

const connectWebSocket = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/chat`
  
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket connection established')
    isConnecting.value = false
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'history') {
      messages.value = data.messages
    } else {
      messages.value.push(data)
      if (data.type === 'user') {
        isTyping.value = true
      } else if (data.type === 'bot') {
        isTyping.value = false
      }
    }
    
    nextTick(() => {
      scrollToBottom()
    })
    
    updateDashboardStats()
  }
  
  ws.onclose = () => {
    console.log('WebSocket connection closed')
    isConnecting.value = true
    // Attempt to reconnect
    setTimeout(connectWebSocket, 3000)
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim() || !ws || ws.readyState !== WebSocket.OPEN) {
    return
  }
  
  ws.send(JSON.stringify({
    content: newMessage.value
  }))
  
  newMessage.value = ''
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const updateDashboardStats = async () => {
  try {
    const response = await fetch('/api/dashboard/stats')
    const stats = await response.json()
    dashboardStats.value = stats
  } catch (error) {
    console.error('获取仪表板统计信息失败:', error)
  }
}

onMounted(() => {
  connectWebSocket()
  // 定期更新仪表板统计信息
  setInterval(updateDashboardStats, 5000)
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>
