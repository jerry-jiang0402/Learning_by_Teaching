<template>
  <div class="h-full flex flex-col">
    <!-- 仪表板标题 -->
    <div class="p-6 border-b transition-all duration-1000" :class="getHeaderBorderClass()">
      <h2 class="text-lg font-semibold transition-colors duration-500" :class="getHeaderTextClass()">
        Teaching Dashboard
      </h2>
      <!-- 阶段转换提示 -->
      <div v-if="props.currentPhase" class="mt-2 flex items-center space-x-2">
        <div class="w-3 h-3 rounded-full transition-colors duration-500" :class="getPhaseIndicatorDotClass()"></div>
        <span class="text-sm font-medium transition-colors duration-500" :class="getPhaseTextClass()">
          {{ getPhaseDisplayText() }}
        </span>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- 🔋 Knowledge Energy 能量显示模块 - 移到第一位 -->
      <div v-if="stats.energy_stats" class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl shadow-md p-5 border border-amber-200">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg flex items-center justify-center shadow-lg">
              <span class="text-2xl">⚡</span>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-800">Knowledge Energy</h3>
              <p class="text-xs text-gray-600">Learning Achievement</p>
            </div>
          </div>
        </div>
        
        <!-- 主能量显示 -->
        <div class="bg-white rounded-lg p-4 shadow-sm mb-3">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">Total Energy</p>
              <div class="flex items-baseline space-x-2">
                <span class="text-4xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                  {{ stats.energy_stats.current_energy }}
                </span>
                <span class="text-2xl">⚡</span>
              </div>
              <p v-if="stats.energy_stats.last_energy_change > 0" 
                 class="text-sm font-semibold text-green-600 mt-1 animate-pulse">
                +{{ stats.energy_stats.last_energy_change }} from last action
              </p>
            </div>
            <div class="text-right">
              <p class="text-xs text-gray-500">Current Topic</p>
              <p class="text-lg font-bold text-amber-600">
                +{{ stats.energy_stats.current_knowledge_point_energy }}⚡
              </p>
            </div>
          </div>
          
          <!-- 🕐 回复计时器 - 始终显示 -->
          <div class="mt-3 pt-3 border-t border-amber-100">
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-xs font-medium text-gray-700">Response Timer</span>
              <div class="flex items-center space-x-1.5">
                <span class="text-xs font-bold" :class="getTimerTextClass()">
                  {{ responseTimer.timeLeft }}s
                </span>
                <span class="text-xs font-medium" :class="getMultiplierClass()">
                  {{ getScoreMultiplier() }}%
                </span>
              </div>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                class="h-2 rounded-full transition-all duration-1000 ease-linear"
                :class="getTimerBarClass()"
                :style="`width: ${responseTimer.percentage}%`"
              ></div>
            </div>
          </div>
        </div>
        
        <!-- 统计信息 -->
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-white rounded-lg p-3 shadow-sm">
            <p class="text-xs text-gray-600 mb-1">Explanations</p>
            <p class="text-2xl font-bold text-amber-600">{{ stats.energy_stats.total_explanations }}</p>
          </div>
          <div class="bg-white rounded-lg p-3 shadow-sm">
            <p class="text-xs text-gray-600 mb-1">Errors Corrected</p>
            <p class="text-2xl font-bold text-orange-600">{{ stats.energy_stats.total_corrected_errors }}</p>
          </div>
        </div>
      </div>

      <!-- Teaching Helper + Energy Activity - 合并版 -->
      <div v-if="stats.teaching_evaluations && stats.teaching_evaluations.length > 0" class="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl shadow-md p-5">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
              <Activity class="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-800">Teaching Activity</h3>
              <p class="text-xs text-gray-600">Quality & Energy</p>
            </div>
          </div>
          <span class="text-xs font-medium text-indigo-600 bg-indigo-100 px-3 py-1 rounded-full">
            {{ stats.teaching_evaluations.length }} activities
          </span>
        </div>
        
        <div class="space-y-2 max-h-80 overflow-y-auto pr-2">
          <div
            v-for="(evaluation, index) in stats.teaching_evaluations.slice().reverse().slice(0, 15)"
            :key="index"
            class="bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2 mb-1">
                  <span 
                    class="w-4 h-4 rounded-full flex-shrink-0 shadow-sm" 
                    :class="getQualityDotClass(evaluation.quality_level)"
                    :title="getQualityTitle(evaluation.quality_level)"
                  ></span>
                  <span class="text-sm font-semibold text-gray-700 truncate">{{ evaluation.knowledge_point }}</span>
                </div>
                <p class="text-xs text-gray-600 leading-relaxed ml-6 break-words">{{ evaluation.feedback }}</p>
              </div>
              <span v-if="evaluation.energy_gain > 0" 
                    class="text-sm font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded-full flex-shrink-0 whitespace-nowrap">
                +{{ evaluation.energy_gain }}⚡
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- ✅ Current Topic Board - 渐进式探索解锁系统 -->
      <div 
        v-if="stats.topics && stats.topics.length > 0"
        class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl shadow-md border border-indigo-200 overflow-hidden"
      >
        <!-- 标题栏 -->
        <div class="p-4 border-b border-indigo-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="text-lg">🗺️</span>
              <p class="text-sm font-medium text-indigo-700">Knowledge Path</p>
            </div>
            <span class="text-xs text-indigo-500">
              {{ stats.current_topic_index !== undefined ? `Topic ${stats.current_topic_index + 1}/${stats.topics.length}` : '' }}
            </span>
          </div>
        </div>

        <!-- Topic Board 内容 -->
        <div class="px-4 pb-4 pt-3 space-y-3 max-h-96 overflow-y-auto">
          <!-- 每个一级 Topic -->
          <div
            v-for="(topic, topicIndex) in stats.topics"
            :key="topic.id"
            class="bg-white rounded-lg p-3 border transition-all duration-300"
            :class="getTopicBorderClass(topic, topicIndex)"
          >
            <!-- 一级 Topic 标题 -->
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                <span class="text-sm font-semibold" :class="getTopicTitleClass(topic)">
                  {{ topicIndex + 1 }}. {{ topic.title }}
                </span>
                <span v-if="topic.all_completed" class="text-xs">✅</span>
                <span v-else-if="!topic.unlocked" class="text-xs">🔒</span>
              </div>
            </div>

            <!-- 二级小点列表 -->
            <div v-if="topic.unlocked" class="space-y-1.5 ml-4">
              <div
                v-for="subItem in topic.sub_items"
                :key="subItem.id"
                class="flex items-center justify-between p-2 rounded transition-all duration-300"
                :class="getSubItemClass(subItem)"
              >
                <div class="flex items-center space-x-2 flex-1 min-w-0">
                  <span class="text-xs" :class="getSubItemBlurClass(subItem)">
                    {{ subItem.title }}
                  </span>
                  <!-- ✅ 区分状态图标 -->
                  <span v-if="subItem.completed" class="text-xs">✅</span>
                  <span v-else-if="subItem.status === 'revealedByLLM'" class="text-xs">🔍</span>
                  <span v-else-if="subItem.status === 'manuallyViewed'" class="text-xs">👁️</span>
                  <span v-else class="text-xs text-gray-400">🔒</span>
                </div>

                <!-- 查看按钮（仅对当前 Topic 且 locked 状态可用） -->
                <button
                  v-if="topicIndex === stats.current_topic_index && subItem.status === 'locked' && !subItem.completed"
                  @click.stop="viewSubItem(topic.id, subItem.id)"
                  class="text-xs px-2 py-0.5 rounded bg-indigo-100 hover:bg-indigo-200 text-indigo-700 transition-all duration-200 flex-shrink-0"
                >
                  View
                </button>
              </div>
            </div>

            <!-- 未解锁提示 -->
            <div v-else class="text-xs text-gray-400 ml-4 italic">
              Complete previous topics to unlock
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { MessageSquare, Users, Activity, Trash2, Download } from 'lucide-vue-next'

interface Message {
  id: number
  type: 'user' | 'bot'
  content: string
  timestamp: string
  sender: string
}

interface TeachingEvaluation {
  knowledge_point: string
  quality_level: string
  feedback: string
  is_relevant: boolean
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
  teaching_evaluations?: TeachingEvaluation[]
  energy_stats?: EnergyStats  // 🔋 能量统计数据
  topics?: Topic[]  // ✅ 两级 Topic 结构
  current_topic_index?: number  // ✅ 当前 Topic 索引
}

interface Props {
  stats: DashboardStats
  messages: Message[]
  currentPhase?: string
}

const props = defineProps<Props>()

// 🕐 响应计时器状态
const responseTimer = reactive({
  isActive: false,
  timeLeft: 90,
  percentage: 100,
  intervalId: null as number | null
})

// 开始计时器
const startResponseTimer = () => {
  stopResponseTimer() // 清除之前的计时器
  responseTimer.isActive = true
  responseTimer.timeLeft = 90
  responseTimer.percentage = 100
  
  responseTimer.intervalId = window.setInterval(() => {
    if (responseTimer.timeLeft > 0) {
      responseTimer.timeLeft--
      responseTimer.percentage = (responseTimer.timeLeft / 90) * 100
    } else {
      // 🕐 归零后停止计时，但保持在0，不重置
      if (responseTimer.intervalId) {
        clearInterval(responseTimer.intervalId)
        responseTimer.intervalId = null
      }
      // 保持 isActive = true，timeLeft = 0，percentage = 0
      // 这样用户发消息时会得到最低50%的分数
    }
  }, 1000)
}

// 停止计时器并重置为满格
const stopResponseTimer = () => {
  if (responseTimer.intervalId) {
    clearInterval(responseTimer.intervalId)
    responseTimer.intervalId = null
  }
  responseTimer.isActive = false
  responseTimer.timeLeft = 90
  responseTimer.percentage = 100
}

// 获取分数倍数
const getScoreMultiplier = () => {
  const time = responseTimer.timeLeft
  // 倒计时90秒：剩余时间越少，分数越低
  if (time >= 60) return 100  // 剩余60-90s (已用0-30s): 100%
  if (time >= 40) return 75   // 剩余40-60s (已用30-50s): 75%
  if (time >= 20) return 63   // 剩余20-40s (已用50-70s): 63%
  return 50                   // 剩余0-20s (已用70-90s+): 50%
}

// 计时器文字颜色
const getTimerTextClass = () => {
  const time = responseTimer.timeLeft
  if (time >= 60) return 'text-green-600'   // 100%: 绿色
  if (time >= 40) return 'text-yellow-600'  // 75%: 黄色
  if (time >= 20) return 'text-orange-600'  // 63%: 橙色
  return 'text-red-600'                     // 50%: 红色
}

// 倍数文字颜色
const getMultiplierClass = () => {
  const time = responseTimer.timeLeft
  if (time >= 60) return 'text-green-600'
  if (time >= 40) return 'text-yellow-600'
  if (time >= 20) return 'text-orange-600'
  return 'text-red-600'
}

// 计时器进度条颜色
const getTimerBarClass = () => {
  const time = responseTimer.timeLeft
  if (time >= 60) return 'bg-gradient-to-r from-green-500 to-emerald-500'
  if (time >= 40) return 'bg-gradient-to-r from-yellow-500 to-orange-400'
  if (time >= 20) return 'bg-gradient-to-r from-orange-500 to-orange-600'
  return 'bg-gradient-to-r from-red-500 to-rose-500'
}

// 暴露方法给父组件
defineExpose({
  startResponseTimer,
  stopResponseTimer,
  getScoreMultiplier
})

const recentMessages = computed(() => {
  return props.messages.slice(-5).reverse()
})

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('en-US', {
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

const getStatusText = (status: string) => {
  switch (status) {
    case 'not_started': return 'Not Started'
    case 'student_teaching': return 'You Teaching'
    case 'completed': return 'Completed'
    default: return 'Unknown'
  }
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'not_started': return 'bg-gray-100 text-gray-600'
    case 'student_teaching': return 'bg-green-100 text-green-600'
    case 'completed': return 'bg-emerald-100 text-emerald-600'
    default: return 'bg-gray-100 text-gray-600'
  }
}

// 新增的动态样式方法
const getHeaderBorderClass = () => {
  switch (props.currentPhase) {
    case 'student_teaching': return 'border-green-200'
    case 'all_completed': return 'border-emerald-200'
    default: return 'border-blue-200'
  }
}

const getHeaderTextClass = () => {
  switch (props.currentPhase) {
    case 'student_teaching': return 'text-green-800'
    case 'all_completed': return 'text-emerald-800'
    default: return 'text-blue-800'
  }
}

const getPhaseIndicatorDotClass = () => {
  switch (props.currentPhase) {
    case 'student_teaching': return 'bg-green-500 animate-pulse'
    case 'all_completed': return 'bg-emerald-500'
    default: return 'bg-blue-500'
  }
}

const getPhaseTextClass = () => {
  switch (props.currentPhase) {
    case 'student_teaching': return 'text-green-700'
    case 'all_completed': return 'text-emerald-700'
    default: return 'text-blue-700'
  }
}

const getPhaseDisplayText = () => {
  switch (props.currentPhase) {
    case 'algorithm_selection': return 'Choose an algorithm to start learning'
    case 'student_teaching': return 'You are teaching AI Buddy'
    case 'all_completed': return 'Teaching session completed! 🎉'
    default: return 'Ready to start teaching'
  }
}

const getQualityDotClass = (quality: string) => {
  switch (quality) {
    case 'green': return 'bg-green-500 ring-2 ring-green-200'
    case 'yellow': return 'bg-yellow-500 ring-2 ring-yellow-200'
    case 'red': return 'bg-red-500 ring-2 ring-red-200'
    default: return 'bg-gray-400'
  }
}

const getQualityTitle = (quality: string) => {
  switch (quality) {
    case 'green': return 'Excellent: Content accurate, explanation comprehensive'
    case 'yellow': return 'Average: Basically correct but not comprehensive enough'
    case 'red': return 'Needs improvement: Obvious errors or unclear explanation'
    default: return 'Evaluating'
  }
}

// ✅ ========== Topic Board 样式方法 ==========

const getTopicBorderClass = (topic: Topic, topicIndex: number) => {
  if (topicIndex === props.stats.current_topic_index) {
    return 'border-indigo-400 bg-indigo-50 shadow-md'
  } else if (topic.unlocked) {
    return 'border-green-300 bg-green-50'
  } else {
    return 'border-gray-200 bg-gray-50 opacity-60'
  }
}

const getTopicTitleClass = (topic: Topic) => {
  if (topic.all_completed) {
    return 'text-green-700'
  } else if (topic.unlocked) {
    return 'text-indigo-700'
  } else {
    return 'text-gray-400'
  }
}

const getSubItemClass = (subItem: SubItem) => {
  // ✅ 优先判断是否完成
  if (subItem.completed) {
    return 'bg-emerald-200 border-2 border-emerald-500 shadow-sm'
  } else if (subItem.status === 'revealedByLLM') {
    // 🔍 探索发现，但未完成
    return 'bg-green-100 border border-green-300'
  } else if (subItem.status === 'manuallyViewed') {
    // 👁️ 主动查看，但未完成
    return 'bg-blue-50 border border-blue-200'
  } else {
    // 🔒 未发现
    return 'bg-gray-50 border border-gray-200'
  }
}

const getSubItemBlurClass = (subItem: SubItem) => {
  // ✅ 优先判断是否完成
  if (subItem.completed) {
    return 'text-emerald-800 font-bold'
  } else if (subItem.status === 'locked') {
    // 🔒 未发现：模糊
    return 'blur-sm text-gray-400 select-none'
  } else if (subItem.status === 'manuallyViewed') {
    // 👁️ 主动查看，但未完成
    return 'text-blue-700 font-medium'
  } else if (subItem.status === 'revealedByLLM') {
    // 🔍 探索发现，但未完成
    return 'text-green-700 font-semibold'
  } else {
    return 'text-gray-600'
  }
}

// ✅ 主动查看二级小点
const viewSubItem = async (topicId: string, subItemId: string) => {
  try {
    const response = await fetch('http://localhost:8000/api/view_sub_item', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic_id: topicId,
        sub_item_id: subItemId
      })
    })
    
    const result = await response.json()
    if (result.success) {
      console.log('✅ Sub-item viewed:', result.message)
      // 触发 Dashboard 刷新（通过父组件）
      window.dispatchEvent(new CustomEvent('refresh-dashboard'))
    }
  } catch (error) {
    console.error('Error viewing sub-item:', error)
  }
}
</script>

<style scoped>
/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* ✅ Topic Board 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
</style>

