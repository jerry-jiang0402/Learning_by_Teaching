<template>
  <div class="flex h-screen transition-all duration-1000" :class="getBackgroundClass()">
    <!-- 左侧聊天界面 -->
    <div class="flex-1 flex flex-col">
      <!-- 聊天标题栏 -->
      <div class="border-b px-6 py-4 transition-all duration-1000" :class="getHeaderClass()">
        <div class="flex items-center justify-between">
          <!-- 左上角粘贴控制按钮 -->
          <button 
            @click="togglePasteAllowed"
            class="flex items-center space-x-2 px-3 py-1.5 rounded-lg transition-all duration-300 hover:scale-105 shadow-sm"
            :class="pasteAllowed ? 'bg-green-100 hover:bg-green-200 text-green-700' : 'bg-red-100 hover:bg-red-200 text-red-700'"
            :title="pasteAllowed ? 'Click to disable paste' : 'Click to enable paste'"
          >
            <span class="text-lg">{{ pasteAllowed ? '📋' : '🚫' }}</span>
            <span class="text-sm font-medium">{{ pasteAllowed ? 'Paste Enabled' : 'Paste Disabled' }}</span>
          </button>
          
          <div>
            <h1 class="text-xl font-semibold transition-colors duration-500" :class="getTitleClass()">
              {{ getPageTitle() }}
            </h1>
            <div class="flex items-center space-x-4">
              <p class="text-sm transition-colors duration-500" :class="getSubtitleClass()">
                Teacher: You | Student: Algorithm Buddy
              </p>
              <div v-if="dashboardStats.current_phase" class="flex items-center space-x-2">
                <!-- 角色切换动画指示器 -->
                <div class="flex items-center space-x-2">
                  <div class="relative">
                    <span class="px-3 py-1 rounded-full text-xs font-medium transition-all duration-500 transform" 
                          :class="getPhaseIndicatorClass(dashboardStats.current_phase)"
                          :style="getPhaseAnimationStyle()">
                  {{ getPhaseText(dashboardStats.current_phase) }}
                    </span>
                    <!-- 脉冲动画 -->
                    <div v-if="isPhaseTransitioning" 
                         class="absolute inset-0 rounded-full animate-ping" 
                         :class="getPulseClass()"></div>
                  </div>
                  <!-- 当前分享者指示器 -->
                  <div class="flex items-center space-x-1 px-2 py-1 rounded-lg transition-all duration-500" 
                       :class="getCurrentSharerClass()">
                    <div class="w-2 h-2 rounded-full transition-colors duration-500" :class="getSharerDotClass()"></div>
                    <span class="text-xs font-medium">{{ getCurrentSharerText() }}</span>
                  </div>
                </div>
                <span class="text-xs transition-colors duration-500" :class="getTopicClass()">
                  {{ dashboardStats.current_knowledge_point }}
                </span>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span class="text-sm transition-colors duration-500" :class="getStatusClass()">Online</span>
          </div>
        </div>
      </div>

      <!-- 聊天消息区域 -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4" ref="messagesContainer">
        <!-- 角色切换通知 -->
        <div v-if="isPhaseTransitioning" class="flex justify-center">
          <div class="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-3 rounded-full shadow-lg animate-bounce">
            <div class="flex items-center space-x-2">
              <div class="w-3 h-3 bg-white rounded-full animate-ping"></div>
              <span class="font-medium">{{ getTransitionMessage() }}</span>
              <div class="w-3 h-3 bg-white rounded-full animate-ping" style="animation-delay: 0.5s"></div>
            </div>
          </div>
        </div>
        <!-- 算法选择界面 -->
        <div v-if="dashboardStats.current_phase === 'algorithm_selection'" class="flex items-center justify-center h-full">
          <div class="max-w-2xl w-full p-8">
            <div class="text-center mb-8">
              <div class="text-6xl mb-4">🤖</div>
              <h2 class="text-3xl font-bold text-gray-800 mb-4">Choose Your Learning Adventure!</h2>
              <p class="text-lg text-gray-600">Select an algorithm to explore together with Algorithm Buddy</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div 
                v-for="(info, key) in availableAlgorithms" 
                :key="key"
                @click="selectAlgorithm(key)"
                class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer border-2 border-transparent hover:border-blue-300 transform hover:scale-105"
              >
                <div class="text-center">
                  <div class="text-4xl mb-4">{{ info.icon }}</div>
                  <h3 class="text-xl font-semibold text-gray-800 mb-2">{{ info.name }}</h3>
                  <p class="text-gray-600 text-sm">{{ info.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="messages.length === 0" class="text-center text-gray-500 mt-20">
          <div class="text-4xl mb-4">🎓</div>
          <p class="mb-4">Ready to teach Algorithm Buddy about {{ getSelectedAlgorithmName() }}?</p>
          <p class="text-sm">Start teaching when you're ready! 👇</p>
        </div>
        
        <div
          v-for="message in messages"
          :key="message.id"
          :class="[
            'flex flex-col',
            message.type === 'user' ? 'items-end' : message.type === 'warning' ? 'items-center' : 'items-start'
          ]"
        >
          <div
            :class="[
              'max-w-xs lg:max-w-md px-4 py-2 rounded-lg',
              message.type === 'user'
                ? 'bg-blue-500 text-white'
                : message.type === 'warning'
                ? 'bg-red-100 text-red-800 border-2 border-red-300'
                : getAIMessageStyle(message.evaluation)
            ]"
          >
            <p class="text-sm" :class="message.type === 'warning' ? 'font-medium' : ''">
              <span v-if="message.type === 'warning'" class="text-red-600">⚠️ </span>{{ message.content }}
            </p>
            <p class="text-xs mt-1 opacity-70">
              {{ formatTime(message.timestamp) }}
            </p>
          </div>
          
          <!-- 🔋 能量获取提示 -->
          <div
            v-if="message.type === 'user' && message.energy_gain !== undefined && message.energy_gain >= 0"
            class="mt-1 px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1 shadow-sm transition-all duration-500 animate-pulse"
            :class="message.energy_gain > 0 ? 'bg-green-100 text-green-700 border border-green-300' : 'bg-gray-100 text-gray-600 border border-gray-300'"
          >
            <span v-if="message.energy_gain > 0">+{{ message.energy_gain }}⚡</span>
            <span v-else>+0⚡</span>
            <span class="text-[10px] opacity-80">{{ message.energy_reason || 'Evaluated' }}</span>
          </div>
        </div>
        
        <!-- ✅ AI正在思考指示器 -->
        <div v-if="isTyping" class="flex justify-start animate-fadeIn">
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 text-gray-800 border-2 border-blue-300 px-5 py-3 rounded-lg shadow-md">
            <div class="flex items-center space-x-3">
              <div class="flex space-x-1">
                <div class="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce"></div>
                <div class="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.15s"></div>
                <div class="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.3s"></div>
              </div>
              <span class="text-sm font-medium text-blue-700">AI Buddy is thinking...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="border-t p-4 transition-all duration-1000" :class="getInputAreaClass()">
        <form @submit.prevent="sendMessage" class="flex space-x-4">
          <input
            v-model="newMessage"
            type="text"
            :placeholder="getInputPlaceholder()"
            class="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 transition-all duration-500"
            :class="getInputClass()"
            :disabled="isConnecting || dashboardStats.current_phase === 'algorithm_selection'"
            @paste="handlePaste"
          />
          <button
            type="submit"
            :disabled="!newMessage.trim() || isConnecting || dashboardStats.current_phase === 'algorithm_selection'"
            class="text-white px-6 py-2 rounded-lg transition-all duration-500 transform hover:scale-105"
            :class="getButtonClass()"
          >
            Send
          </button>
        </form>
      </div>
    </div>

    <!-- 右侧仪表板 -->
    <div class="w-96 transition-all duration-1000" :class="getDashboardClass()">
      <Dashboard ref="dashboardRef" :stats="dashboardStats" :messages="messages" :current-phase="dashboardStats.current_phase" />
    </div>

    <!-- 🎓 教师证书弹窗 -->
    <Certificate 
      :show="showCertificate"
      :total-energy="certificateData.totalEnergy"
      :algorithm-name="certificateData.algorithmName"
      :stats="certificateData.stats"
      @close="showCertificate = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import Dashboard from '@/components/Dashboard.vue'
import Certificate from '@/components/Certificate.vue'

interface Message {
  id: number
  type: 'user' | 'bot' | 'warning'
  content: string
  timestamp: string
  sender: string
  evaluation?: string  // 添加评估结果字段
  energy_gain?: number  // 🔋 能量增益
  energy_reason?: string  // 🔋 能量增益原因
}

interface EnergyStats {
  student_id: string
  current_energy: number
  last_energy_change: number
  total_explanations: number
  total_corrected_errors: number
  current_knowledge_point_energy: number
  recent_events: Array<{
    timestamp: string
    event_type: string
    energy_change: number
    reason: string
    knowledge_point: string
  }>
}

// ✅ 二级小点接口
interface SubItem {
  id: string
  title: string
  status: 'locked' | 'manuallyViewed' | 'revealedByLLM'
  completed: boolean
}

// ✅ 一级 Topic 接口
interface Topic {
  id: string
  title: string
  unlocked: boolean
  sub_items: SubItem[]
  all_completed: boolean
}

interface DashboardStats {
  total_messages: number
  total_knowledge_points: number
  completed_knowledge_points: number
  current_knowledge_point: string
  progress_percentage: number
  current_phase: string
  selected_algorithm?: string
  knowledge_points_detail: Array<{
    id: string
    title: string
    status: string
    ai_taught: boolean
    student_taught: boolean
  }>
  energy_stats?: EnergyStats  // 🔋 能量统计数据
  topics?: Topic[]  // ✅ 两级 Topic 结构
  current_topic_index?: number  // ✅ 当前 Topic 索引
}

const messages = ref<Message[]>([])
const newMessage = ref('')
const isConnecting = ref(true)
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement>()
const isPhaseTransitioning = ref(false)
const previousPhase = ref('')
const availableAlgorithms = ref({})
const pasteAllowed = ref(true)  // 粘贴控制状态
const dashboardRef = ref<any>(null)  // Dashboard组件引用
const dashboardStats = ref<DashboardStats>({
  total_messages: 0,
  total_knowledge_points: 0,
  completed_knowledge_points: 0,
  current_knowledge_point: '',
  progress_percentage: 0,
  current_phase: 'algorithm_selection',
  selected_algorithm: undefined,
  knowledge_points_detail: []
})

// 🎓 教师证书相关状态
const showCertificate = ref(false)
const certificateData = ref({
  totalEnergy: 0,
  algorithmName: '',
  stats: {
    topicsCompleted: 0,
    totalTopics: 0,
    explanations: 0,
    corrections: 0,
    discoveries: 0
  }
})

let ws: WebSocket | null = null

const connectWebSocket = () => {
  // 每次连接前清除本地状态，确保全新开始
  messages.value = []
  isPhaseTransitioning.value = false
  previousPhase.value = ''
  dashboardStats.value = {
    total_messages: 0,
    total_knowledge_points: 0,
    completed_knowledge_points: 0,
    current_knowledge_point: '',
    progress_percentage: 0,
    current_phase: 'algorithm_selection',
    selected_algorithm: undefined,
    knowledge_points_detail: []
  }
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/chat`
  
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket connection established - Starting fresh learning session')
    isConnecting.value = false
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'system' && data.content === 'algorithm_selection') {
      // 处理算法选择消息
      availableAlgorithms.value = data.algorithms
      console.log('Received algorithm options:', data.algorithms)
    } else if (data.type === 'history') {
      // 忽略历史消息，因为每次都是新会话
      console.log('Ignoring history - starting fresh session')
    } else {
      messages.value.push(data)
      if (data.type === 'user') {
        isTyping.value = true
      } else if (data.type === 'bot') {
        isTyping.value = false
        // 🕐 AI发送消息后，启动回复计时器
        if (dashboardRef.value && dashboardStats.value.current_phase === 'student_teaching') {
          nextTick(() => {
            dashboardRef.value.startResponseTimer()
          })
        }
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

const selectAlgorithm = async (algorithmKey: string) => {
  try {
    const response = await fetch('/api/select-algorithm', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ algorithm: algorithmKey })
    })
    
    const result = await response.json()
    if (result.success) {
      console.log('Algorithm selected successfully:', algorithmKey)
      updateDashboardStats()
    } else {
      console.error('Failed to select algorithm:', result.message)
    }
  } catch (error) {
    console.error('Error selecting algorithm:', error)
  }
}

// 粘贴控制功能
const togglePasteAllowed = () => {
  pasteAllowed.value = !pasteAllowed.value
}

const handlePaste = (event: ClipboardEvent) => {
  if (!pasteAllowed.value) {
    event.preventDefault()
    // 显示提示信息
    messages.value.push({
      id: Date.now(),
      type: 'warning',
      content: '⚠️ Paste is currently disabled. Please type your response manually.',
      timestamp: new Date().toISOString(),
      sender: 'System'
    })
    scrollToBottom()
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim() || !ws || ws.readyState !== WebSocket.OPEN) {
    return
  }
  
  // 🕐 获取当前分数倍数
  let scoreMultiplier = 1.0
  if (dashboardRef.value) {
    const multiplier = dashboardRef.value.getScoreMultiplier()
    scoreMultiplier = multiplier / 100  // 转换为小数（100% -> 1.0, 75% -> 0.75, 50% -> 0.5）
    // 停止计时器
    dashboardRef.value.stopResponseTimer()
  }
  
  ws.send(JSON.stringify({
    content: newMessage.value,
    score_multiplier: scoreMultiplier  // 发送分数倍数到后端
  }))
  
  newMessage.value = ''
  
  // ✅ 显示"AI正在思考"动画
  isTyping.value = true
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getAIMessageStyle = (evaluation?: string) => {
  switch (evaluation) {
    case 'completely_wrong':
      return 'bg-red-100 text-red-800 border border-red-200'
    case 'partially_right':
      return 'bg-yellow-100 text-yellow-800 border border-yellow-200'
    case 'completely_right':
      return 'bg-green-100 text-green-800 border border-green-200'
    default:
      return 'bg-white text-gray-800 border border-gray-200'
  }
}

const updateDashboardStats = async () => {
  try {
    const response = await fetch('/api/dashboard/stats')
    const stats = await response.json()
    
    // 检测阶段转换
    if (dashboardStats.value.current_phase !== stats.current_phase) {
      previousPhase.value = dashboardStats.value.current_phase
      isPhaseTransitioning.value = true
      
      // 转换动画持续时间
      setTimeout(() => {
        isPhaseTransitioning.value = false
      }, 2000)

      // 🎓 检测学习完成，显示证书
      if (stats.current_phase === 'all_completed') {
        showCertificateModal(stats)
      }
    }
    
    dashboardStats.value = stats
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error)
  }
}

// 🎓 显示教师证书
const showCertificateModal = (stats: DashboardStats) => {
  const energyStats = stats.energy_stats
  const topics = stats.topics || []
  
  certificateData.value = {
    totalEnergy: energyStats?.current_energy || 0,
    algorithmName: stats.selected_algorithm 
      ? (availableAlgorithms.value[stats.selected_algorithm]?.name || stats.selected_algorithm)
      : '算法',
    stats: {
      topicsCompleted: topics.filter(t => t.all_completed).length,
      totalTopics: topics.length,
      explanations: energyStats?.total_explanations || 0,
      corrections: energyStats?.total_corrected_errors || 0,
      discoveries: energyStats?.recent_events?.filter(e => e.event_type === 'exploration_bonus').length || 0
    }
  }
  
  // 延迟显示证书，给用户一点时间看完成消息
  setTimeout(() => {
    showCertificate.value = true
  }, 2000)
}

const getPageTitle = () => {
  if (dashboardStats.value.current_phase === 'algorithm_selection') {
    return 'Algorithm Learning Platform'
  } else if (dashboardStats.value.selected_algorithm && availableAlgorithms.value[dashboardStats.value.selected_algorithm]) {
    return `Teaching Session: ${availableAlgorithms.value[dashboardStats.value.selected_algorithm].name}`
  } else {
    return 'Teaching Session'
  }
}

const getSelectedAlgorithmName = () => {
  if (dashboardStats.value.selected_algorithm && availableAlgorithms.value[dashboardStats.value.selected_algorithm]) {
    return availableAlgorithms.value[dashboardStats.value.selected_algorithm].name
  }
  return 'the selected algorithm'
}

const getPhaseText = (phase: string) => {
  switch (phase) {
    case 'algorithm_selection': return 'Choose Algorithm'
    case 'opening': return 'Getting Started'
    case 'student_teaching': return 'You Teaching'
    case 'knowledge_point_completed': return 'Topic Complete'
    case 'all_completed': return 'Session Complete'
    default: return 'Teaching'
  }
}

const getPhaseIndicatorClass = (phase: string) => {
  switch (phase) {
    case 'algorithm_selection': return 'bg-indigo-100 text-indigo-600 border-indigo-200'
    case 'opening': return 'bg-blue-100 text-blue-600 border-blue-200'
    case 'student_teaching': return 'bg-green-100 text-green-600 border-green-200'
    case 'knowledge_point_completed': return 'bg-yellow-100 text-yellow-600 border-yellow-200'
    case 'all_completed': return 'bg-emerald-100 text-emerald-600 border-emerald-200'
    default: return 'bg-gray-100 text-gray-600 border-gray-200'
  }
}

// 新增的UI样式方法
const getBackgroundClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'algorithm_selection': return 'bg-gradient-to-br from-indigo-50 to-purple-50'
    case 'student_teaching': return 'bg-gradient-to-br from-green-50 to-emerald-50'
    case 'all_completed': return 'bg-gradient-to-br from-emerald-50 to-teal-50'
    default: return 'bg-gradient-to-br from-blue-50 to-cyan-50'
  }
}

const getHeaderClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'bg-white/80 backdrop-blur-sm border-green-200'
    case 'all_completed': return 'bg-white/80 backdrop-blur-sm border-emerald-200'
    default: return 'bg-white/80 backdrop-blur-sm border-blue-200'
  }
}

const getTitleClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'text-green-800'
    case 'all_completed': return 'text-emerald-800'
    default: return 'text-blue-800'
  }
}

const getSubtitleClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'text-green-600'
    case 'all_completed': return 'text-emerald-600'
    default: return 'text-blue-600'
  }
}

const getTopicClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'text-green-500'
    case 'all_completed': return 'text-emerald-500'
    default: return 'text-blue-500'
  }
}

const getStatusClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'text-green-500'
    case 'all_completed': return 'text-emerald-500'
    default: return 'text-blue-500'
  }
}

const getCurrentSharerClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'bg-green-50 border border-green-200 text-green-700'
    case 'all_completed': return 'bg-emerald-50 border border-emerald-200 text-emerald-700'
    default: return 'bg-blue-50 border border-blue-200 text-blue-700'
  }
}

const getSharerDotClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'bg-green-500 animate-pulse'
    case 'all_completed': return 'bg-emerald-500'
    default: return 'bg-blue-500'
  }
}

const getCurrentSharerText = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'You Teaching'
    case 'all_completed': return 'Complete!'
    default: return 'Ready'
  }
}

const getPulseClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'bg-green-200'
    case 'all_completed': return 'bg-emerald-200'
    default: return 'bg-blue-200'
  }
}

const getPhaseAnimationStyle = () => {
  if (isPhaseTransitioning.value) {
    return {
      transform: 'scale(1.1)',
      boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)'
    }
  }
  return {}
}

const getInputAreaClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'bg-white/80 backdrop-blur-sm border-green-200'
    case 'all_completed': return 'bg-white/80 backdrop-blur-sm border-emerald-200'
    default: return 'bg-white/80 backdrop-blur-sm border-blue-200'
  }
}

const getInputClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'border-green-300 focus:ring-green-500 focus:border-green-500'
    case 'all_completed': return 'border-emerald-300 focus:ring-emerald-500 focus:border-emerald-500'
    default: return 'border-blue-300 focus:ring-blue-500 focus:border-blue-500'
  }
}

const getButtonClass = () => {
  const baseClass = 'disabled:bg-gray-400 disabled:cursor-not-allowed'
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return `bg-green-500 hover:bg-green-600 ${baseClass}`
    case 'all_completed': return `bg-emerald-500 hover:bg-emerald-600 ${baseClass}`
    default: return `bg-blue-500 hover:bg-blue-600 ${baseClass}`
  }
}

const getInputPlaceholder = () => {
  switch (dashboardStats.value.current_phase) {
    case 'algorithm_selection': return 'Please select an algorithm above to start learning...'
    case 'student_teaching': return 'Teach AI Buddy about this topic...'
    case 'all_completed': return 'Great job! You\'ve completed the learning session!'
    default: return 'Teach AI Buddy what you know...'
  }
}

const getDashboardClass = () => {
  switch (dashboardStats.value.current_phase) {
    case 'student_teaching': return 'bg-white/90 backdrop-blur-sm border-l border-green-200'
    case 'all_completed': return 'bg-white/90 backdrop-blur-sm border-l border-emerald-200'
    default: return 'bg-white/90 backdrop-blur-sm border-l border-blue-200'
  }
}

const getTransitionMessage = () => {
  const currentPhase = dashboardStats.value.current_phase
  const previous = previousPhase.value
  
  if (currentPhase === 'all_completed') {
    return '🎉 Learning session completed!'
  } else if (currentPhase === 'student_teaching') {
    return '📚 Continue teaching the next topic...'
  } else {
    return '🔄 Moving forward...'
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

<style scoped>
/* ✅ 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.4s ease-out;
}
</style>
