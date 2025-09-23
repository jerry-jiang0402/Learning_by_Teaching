<template>
  <div class="h-full flex flex-col">
    <!-- 仪表板标题 -->
    <div class="p-6 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-800">Teaching Session Dashboard</h2>
    </div>

    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 gap-4">
        <div class="bg-blue-50 rounded-lg p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <MessageSquare class="w-4 h-4 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-blue-600">Total Messages</p>
              <p class="text-2xl font-bold text-blue-900">{{ stats.total_messages }}</p>
            </div>
          </div>
        </div>

        <div class="bg-green-50 rounded-lg p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                <Activity class="w-4 h-4 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-green-600">Last Thinking Time</p>
              <p class="text-2xl font-bold text-green-900">{{ stats.last_thinking_time }}s</p>
            </div>
          </div>
        </div>

        <div class="bg-purple-50 rounded-lg p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                <Activity class="w-4 h-4 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-purple-600">Average Thinking Time</p>
              <p class="text-2xl font-bold text-purple-900">{{ stats.avg_thinking_time }}s</p>
            </div>
          </div>
        </div>

        <!-- 注释掉的原有统计卡片 -->
        <!--
        <div class="bg-green-50 rounded-lg p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                <Users class="w-4 h-4 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-green-600">Online Users</p>
              <p class="text-2xl font-bold text-green-900">{{ stats.active_connections }}</p>
            </div>
          </div>
        </div>

        <div class="bg-purple-50 rounded-lg p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                <Activity class="w-4 h-4 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-purple-600">System Status</p>
              <p class="text-lg font-semibold text-purple-900">{{ stats.uptime }}</p>
            </div>
          </div>
        </div>
        -->
      </div>

      <!-- 注释掉的其他功能 -->
      <!--
      <!-- 最近消息 -->
      <div>
        <h3 class="text-md font-semibold text-gray-800 mb-3">Recent Messages</h3>
        <div class="space-y-3 max-h-60 overflow-y-auto">
          <div
            v-for="message in recentMessages"
            :key="message.id"
            class="bg-gray-50 rounded-lg p-3"
          >
            <div class="flex items-start space-x-2">
              <div
                :class="[
                  'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
                  message.type === 'user'
                    ? 'bg-blue-100 text-blue-600'
                    : 'bg-gray-100 text-gray-600'
                ]"
              >
                {{ message.type === 'user' ? 'U' : 'AI' }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-800 truncate">{{ message.content }}</p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ formatTime(message.timestamp) }}
                </p>
              </div>
            </div>
          </div>
          <div v-if="recentMessages.length === 0" class="text-center text-gray-500 py-4">
            <MessageSquare class="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p class="text-sm">No messages yet</p>
          </div>
        </div>
      </div>

      <!-- 系统信息 -->
      <div>
        <h3 class="text-md font-semibold text-gray-800 mb-3">System Information</h3>
        <div class="bg-gray-50 rounded-lg p-4 space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Server Status:</span>
            <span class="text-green-600 font-medium">Running</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">WebSocket:</span>
            <span class="text-green-600 font-medium">Connected</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Last Message:</span>
            <span class="text-gray-800">
              {{ stats.last_message_time ? formatTime(stats.last_message_time) : 'None' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div>
        <h3 class="text-md font-semibold text-gray-800 mb-3">Quick Actions</h3>
        <div class="space-y-2">
          <button
            @click="clearChat"
            class="w-full bg-red-50 hover:bg-red-100 text-red-600 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Trash2 class="w-4 h-4 inline mr-2" />
            Clear Chat History
          </button>
          <button
            @click="exportChat"
            class="w-full bg-blue-50 hover:bg-blue-100 text-blue-600 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Download class="w-4 h-4 inline mr-2" />
            Export Chat History
          </button>
        </div>
      </div>
      -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MessageSquare, Users, Activity, Trash2, Download } from 'lucide-vue-next'

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

interface Props {
  stats: DashboardStats
  messages: Message[]
}

const props = defineProps<Props>()

const recentMessages = computed(() => {
  return props.messages.slice(-5).reverse()
})

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const clearChat = () => {
  if (confirm('Are you sure you want to clear all chat history?')) {
    // Here you can call API to clear chat history
    console.log('Clear chat history')
  }
}

const exportChat = () => {
  if (props.messages.length === 0) {
    alert('No chat history to export')
    return
  }
  
  const chatData = props.messages.map(msg => ({
    Time: formatTime(msg.timestamp),
    Sender: msg.sender,
    Message: msg.content
  }))
  
  const dataStr = JSON.stringify(chatData, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `chat_history_${new Date().toISOString().split('T')[0]}.json`
  link.click()
  
  URL.revokeObjectURL(url)
}
</script>
