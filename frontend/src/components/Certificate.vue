<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
    <!-- 证书容器 -->
    <div class="relative animate-certificate-appear">
      <!-- 关闭按钮 -->
      <button 
        @click="$emit('close')"
        class="absolute -top-4 -right-4 w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-100 transition-colors z-10"
      >
        <span class="text-gray-600 text-xl">×</span>
      </button>

      <!-- 证书主体 -->
      <div 
        ref="certificateRef"
        class="certificate-card w-[600px] bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 rounded-2xl shadow-2xl overflow-hidden"
      >
        <!-- 顶部装饰条 -->
        <div class="h-3 bg-gradient-to-r" :class="getGradeGradient()"></div>
        
        <!-- 证书内容 -->
        <div class="p-8">
          <!-- 顶部装饰 -->
          <div class="flex justify-center mb-4">
            <div class="flex items-center space-x-2">
              <span class="text-3xl">🏆</span>
              <div class="h-px w-16 bg-gradient-to-r from-transparent via-amber-400 to-transparent"></div>
              <span class="text-3xl">{{ getGradeEmoji() }}</span>
              <div class="h-px w-16 bg-gradient-to-r from-transparent via-amber-400 to-transparent"></div>
              <span class="text-3xl">🏆</span>
            </div>
          </div>

          <!-- Title -->
          <div class="text-center mb-6">
            <h1 class="text-3xl font-bold bg-gradient-to-r bg-clip-text text-transparent" :class="getGradeTitleGradient()">
              Teaching Certificate
            </h1>
            <p class="text-sm text-gray-500 mt-1 font-serif italic">Certificate of Teaching Excellence</p>
          </div>

          <!-- 分隔线 -->
          <div class="flex items-center justify-center mb-6">
            <div class="h-px w-20 bg-gradient-to-r from-transparent to-amber-300"></div>
            <span class="mx-4 text-amber-500">✦</span>
            <div class="h-px w-20 bg-gradient-to-l from-transparent to-amber-300"></div>
          </div>

          <!-- Certificate Body -->
          <div class="text-center mb-6">
            <p class="text-gray-600 mb-2">This certifies that</p>
            <p class="text-2xl font-bold text-gray-800 mb-2">Outstanding Learner</p>
            <p class="text-gray-600 mb-4">has successfully completed the</p>
            <p class="text-xl font-semibold text-amber-700">{{ algorithmName }}</p>
            <p class="text-gray-600 mt-2">Teaching & Learning Course</p>
          </div>

          <!-- 成就等级 -->
          <div class="flex justify-center mb-6">
            <div 
              class="px-6 py-3 rounded-full text-white font-bold text-lg shadow-lg"
              :class="getGradeBadgeClass()"
            >
              {{ getGradeTitle() }}
            </div>
          </div>

          <!-- 分数展示 -->
          <div class="bg-white/60 rounded-xl p-4 mb-6">
            <div class="flex justify-center items-center space-x-2 mb-3">
              <span class="text-4xl font-bold" :class="getGradeTextColor()">{{ totalEnergy }}</span>
              <span class="text-2xl">⚡</span>
            </div>
            
            <!-- Statistics -->
            <div class="grid grid-cols-4 gap-2 text-center">
              <div class="bg-white/80 rounded-lg p-2">
                <p class="text-xs text-gray-500">Topics Done</p>
                <p class="text-lg font-bold text-gray-700">{{ stats.topicsCompleted }}/{{ stats.totalTopics }}</p>
              </div>
              <div class="bg-white/80 rounded-lg p-2">
                <p class="text-xs text-gray-500">Explanations</p>
                <p class="text-lg font-bold text-gray-700">{{ stats.explanations }}</p>
              </div>
              <div class="bg-white/80 rounded-lg p-2">
                <p class="text-xs text-gray-500">Corrections</p>
                <p class="text-lg font-bold text-gray-700">{{ stats.corrections }}</p>
              </div>
              <div class="bg-white/80 rounded-lg p-2">
                <p class="text-xs text-gray-500">Discoveries</p>
                <p class="text-lg font-bold text-gray-700">{{ stats.discoveries }}</p>
              </div>
            </div>
          </div>

          <!-- 评语 -->
          <div class="text-center mb-6">
            <p class="text-gray-600 italic text-sm px-8">
              "{{ getGradeComment() }}"
            </p>
          </div>

          <!-- 底部信息 -->
          <div class="flex items-center justify-between text-xs text-gray-400">
            <div class="flex items-center space-x-1">
              <span>🤖</span>
              <span>Algorithm Buddy</span>
            </div>
            <div>{{ currentDate }}</div>
            <div class="flex items-center space-x-1">
              <span>📚</span>
              <span>AI Learning Platform</span>
            </div>
          </div>
        </div>

        <!-- 底部装饰条 -->
        <div class="h-3 bg-gradient-to-r" :class="getGradeGradient()"></div>
      </div>

      <!-- Save Button -->
      <div class="flex justify-center mt-6 space-x-4">
        <button 
          @click="saveCertificate"
          class="px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white font-semibold rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 flex items-center space-x-2"
        >
          <span>💾</span>
          <span>Save Certificate</span>
        </button>
        <button 
          @click="$emit('close')"
          class="px-6 py-3 bg-white text-gray-700 font-semibold rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import html2canvas from 'html2canvas'

interface Props {
  show: boolean
  totalEnergy: number
  algorithmName: string
  stats: {
    topicsCompleted: number
    totalTopics: number
    explanations: number
    corrections: number
    discoveries: number
  }
}

const props = defineProps<Props>()
const emit = defineEmits(['close'])

const certificateRef = ref<HTMLElement | null>(null)

const currentDate = computed(() => {
  const date = new Date()
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' }
  return date.toLocaleDateString('en-US', options)
})

// Get grade
const getGrade = () => {
  if (props.totalEnergy >= 250) return 'master'
  if (props.totalEnergy >= 200) return 'proficient'
  if (props.totalEnergy >= 150) return 'competent'
  return 'growing'
}

// Grade title
const getGradeTitle = () => {
  const grade = getGrade()
  switch (grade) {
    case 'master': return '🏆 Master Teacher'
    case 'proficient': return '🥇 Proficient Educator'
    case 'competent': return '🥈 Competent Learner'
    default: return '🌱 Growing Teacher'
  }
}

// 等级表情
const getGradeEmoji = () => {
  const grade = getGrade()
  switch (grade) {
    case 'master': return '👑'
    case 'proficient': return '🌟'
    case 'competent': return '📖'
    default: return '🌱'
  }
}

// Grade comment
const getGradeComment = () => {
  const grade = getGrade()
  switch (grade) {
    case 'master': 
      return 'You demonstrated exceptional teaching ability with deep understanding and clear expression. You are a true master!'
    case 'proficient': 
      return 'Your teaching performance was outstanding, showing solid knowledge and excellent communication skills. Keep it up!'
    case 'competent': 
      return 'You successfully completed the learning tasks with a great attitude. Keep going, you will get even better!'
    default: 
      return 'You took the first step in learning, and that\'s wonderful! Keep practicing, your teaching skills will definitely improve!'
  }
}

// 等级渐变色
const getGradeGradient = () => {
  const grade = getGrade()
  switch (grade) {
    case 'master': return 'from-yellow-400 via-amber-500 to-orange-500'
    case 'proficient': return 'from-blue-400 via-indigo-500 to-purple-500'
    case 'competent': return 'from-green-400 via-emerald-500 to-teal-500'
    default: return 'from-gray-400 via-slate-500 to-gray-600'
  }
}

// 标题渐变色
const getGradeTitleGradient = () => {
  const grade = getGrade()
  switch (grade) {
    case 'master': return 'from-yellow-600 via-amber-600 to-orange-600'
    case 'proficient': return 'from-blue-600 via-indigo-600 to-purple-600'
    case 'competent': return 'from-green-600 via-emerald-600 to-teal-600'
    default: return 'from-gray-600 via-slate-600 to-gray-700'
  }
}

// 徽章样式
const getGradeBadgeClass = () => {
  const grade = getGrade()
  switch (grade) {
    case 'master': return 'bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500'
    case 'proficient': return 'bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500'
    case 'competent': return 'bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500'
    default: return 'bg-gradient-to-r from-gray-500 via-slate-500 to-gray-600'
  }
}

// 分数颜色
const getGradeTextColor = () => {
  const grade = getGrade()
  switch (grade) {
    case 'master': return 'text-amber-600'
    case 'proficient': return 'text-indigo-600'
    case 'competent': return 'text-emerald-600'
    default: return 'text-gray-600'
  }
}

// Save certificate
const saveCertificate = async () => {
  if (!certificateRef.value) return
  
  try {
    const canvas = await html2canvas(certificateRef.value, {
      scale: 2,
      backgroundColor: null,
      useCORS: true
    })
    
    const link = document.createElement('a')
    link.download = `Teaching_Certificate_${props.algorithmName}_${new Date().toISOString().split('T')[0]}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (error) {
    console.error('Failed to save certificate:', error)
    alert('Failed to save certificate, please try again')
  }
}
</script>

<style scoped>
@keyframes certificate-appear {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.animate-certificate-appear {
  animation: certificate-appear 0.5s ease-out forwards;
}

.certificate-card {
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 215, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}
</style>





