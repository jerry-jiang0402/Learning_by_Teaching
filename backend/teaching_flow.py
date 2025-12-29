# Teaching Flow Manager with LLM Integration
from typing import Optional, Dict, List
from enum import Enum
from knowledge_points import (
    KnowledgePointManager, KnowledgePoint, KnowledgePointStatus, 
    ALGORITHM_INFO, ALGORITHM_KNOWLEDGE_POINTS,
    Topic, SubItem, SubItemStatus, ALGORITHM_TOPICS  # ✅ 导入两级结构
)
from llm_service import llm_service
from knowledge_energy import KnowledgeEnergy  # 导入能量系统

class TeachingPhase(Enum):
    ALGORITHM_SELECTION = "algorithm_selection"  # Algorithm selection phase
    OPENING = "opening"  # Opening phase
    STUDENT_TEACHING = "student_teaching"  # Student teaching phase (only mode)
    KNOWLEDGE_POINT_COMPLETED = "knowledge_point_completed"  # Knowledge point completed
    ALL_COMPLETED = "all_completed"  # All knowledge points completed

class TeachingFlowManager:
    def __init__(self):
        self.knowledge_manager = None  # Will be initialized after algorithm selection
        self.current_phase = TeachingPhase.ALGORITHM_SELECTION
        self.session_started = False
        self.algorithm_selected = None
        self.teaching_rounds = 0  # Track teaching rounds for current knowledge point
        self.conversation_history = []  # Store conversation for LLM context
        self.teaching_evaluations = []  # Store Teaching Helper evaluations
        self.energy_manager = KnowledgeEnergy()  # 初始化能量管理器
        self.last_quality_was_red = False  # 追踪上一次是否是红色质量（用于检测纠错）
        
        # ✅ 两级结构状态管理
        self.topics: List[Topic] = []  # 所有 Topics
        self.current_topic_index: int = 0  # 当前允许讲解的 Topic 索引
        
    def select_algorithm(self, algorithm_type: str) -> bool:
        """Select algorithm and initialize knowledge manager"""
        if algorithm_type in ALGORITHM_INFO:
            self.algorithm_selected = algorithm_type
            # 创建特定算法的知识点管理器
            if algorithm_type in ALGORITHM_KNOWLEDGE_POINTS:
                self.knowledge_manager = KnowledgePointManager()
                self.knowledge_manager.knowledge_points = ALGORITHM_KNOWLEDGE_POINTS[algorithm_type].copy()
            else:
                # 默认使用Dijkstra算法
                self.knowledge_manager = KnowledgePointManager()
            
            # ✅ 初始化两级 Topic 结构
            if algorithm_type in ALGORITHM_TOPICS:
                # Deep copy Topics to avoid modifying original definitions
                import copy
                self.topics = copy.deepcopy(ALGORITHM_TOPICS[algorithm_type])
                # 解锁第一个 Topic
                if self.topics:
                    self.topics[0].unlocked = True
                self.current_topic_index = 0
            
            self.current_phase = TeachingPhase.OPENING
            return True
        return False
    
    async def start_session(self) -> str:
        """Start learning session, return opening message"""
        if not self.algorithm_selected or not self.knowledge_manager:
            return "请先选择一个算法！"
            
        self.session_started = True
        
        # Student always teaches in this mode
        self.current_phase = TeachingPhase.STUDENT_TEACHING
        
        # Set first knowledge point status
        current_kp = self.knowledge_manager.get_current_knowledge_point()
        if current_kp:
            current_kp.status = KnowledgePointStatus.STUDENT_TEACHING
        
        # ✅ 使用 Topic 标题生成开场
        algorithm_info = ALGORITHM_INFO[self.algorithm_selected]
        current_topic = self.get_current_topic()
        first_topic_title = current_topic.title if current_topic else "the basics"
        
        # 获取所有 Topic 标题列表
        topic_titles = [topic.title for topic in self.topics] if self.topics else []
        
        opening_prompt = f"""你是算法小伙伴（Algorithm Buddy），正在开始一个关于{algorithm_info['name']}的学习会话。

你的角色定位：你是一个困惑的学生，需要学习，对{algorithm_info['name']}了解很少，经常会有误解。你不是专家，你是来学习的。

学习方式：
- 我们将探索{algorithm_info['name']}的{len(topic_titles)}个主要话题：{', '.join(topic_titles)}
- 在这个学习会话中，你是学生，人类用户是老师，会教你这些话题
- 第一个话题：{first_topic_title}
- 你对这个算法了解很少，甚至可能有一些错误的理解

请生成开场白（2-3句话）：
1. 介绍自己，提到你对{algorithm_info['name']}不太了解，想要学习
2. 表达你听说过{algorithm_info['name']}但不太理解（可以展示一些模糊或错误的印象）
3. 请求老师从第一个话题"{first_topic_title}"开始教你

重要要求：
- 你是一个困惑的学生角色，不要表现得太专业
- 保持谦虚、好奇、有点困惑的语气
- 可以透露你对算法有一些误解或模糊的印象
- 简短，只要2-3句话
- 用中文回复"""

        return await llm_service.generate_response([
            {"role": "system", "content": opening_prompt}
        ])

    def reset_rounds_for_new_knowledge_point(self):
        """Reset round counters for new knowledge point"""
        self.teaching_rounds = 0
    
    def add_to_conversation_history(self, message_type: str, content: str):
        """Add message to conversation history for LLM context"""
        self.conversation_history.append({
            "type": message_type,
            "content": content
        })
    
    async def check_teaching_quality(self, user_message: str, score_multiplier: float = 1.0) -> Dict:
        """Teaching Helper: Check if message is relevant and evaluate quality"""
        # ✅ 使用 Topic 而不是 knowledge_point
        current_topic = self.get_current_topic()
        
        if not current_topic:
            # No current topic, allow message
            return {
                "is_relevant": True,
                "warning_message": "",
                "quality_level": "yellow",
                "feedback": ""
            }
        
        # ✅ Call Teaching Helper evaluation（基于 Topic 标题）
        evaluation = await llm_service.evaluate_topic_teaching_quality(
            current_topic.title,
            user_message,
            self.conversation_history,
            self.algorithm_selected
        )
        
        quality_level = evaluation.get("quality_level", "yellow")
        
        # 🔋 能量系统：检测学生是否纠正了AI的错误
        # 如果上一次质量是红色（学生犯错），这次是绿色或黄色（改正了），给予纠错奖励
        if self.last_quality_was_red and quality_level in ["green", "yellow"]:
            # 🕐 应用时间倍数
            energy_gain = self.energy_manager.add_error_correction_energy(
                current_topic.title,
                "Student corrected their previous error",
                multiplier=score_multiplier
            )
            evaluation["energy_gain"] = energy_gain
            multiplier_text = f" (×{int(score_multiplier*100)}%)" if score_multiplier < 1.0 else ""
            evaluation["energy_reason"] = f"Corrected error{multiplier_text}"
        else:
            # 🔋 能量系统：根据教学质量增加能量
            # 🕐 应用时间倍数
            energy_gain = self.energy_manager.add_quality_energy(
                quality_level,
                current_topic.title,
                evaluation.get("feedback", ""),
                multiplier=score_multiplier
            )
            evaluation["energy_gain"] = energy_gain
            multiplier_text = f" (×{int(score_multiplier*100)}%)" if score_multiplier < 1.0 else ""
            evaluation["energy_reason"] = f"Quality: {quality_level}{multiplier_text}"
        
        # 追踪当前质量是否为红色
        self.last_quality_was_red = (quality_level == "red")
        
        # Store evaluation
        self.teaching_evaluations.append({
            "knowledge_point": current_topic.title,  # 使用 topic 标题
            "quality_level": quality_level,
            "feedback": evaluation.get("feedback", ""),
            "is_relevant": evaluation.get("is_relevant", True),
            "energy_gain": evaluation.get("energy_gain", 0)  # 存储能量增益
        })
        
        return evaluation
    
    def _is_simple_acknowledgment(self, message: str) -> bool:
        """Check if user message is just a simple acknowledgment without substance"""
        if not message or len(message.strip()) == 0:
            return True
        
        # 清理消息，移除标点符号并转为小写
        cleaned = message.strip().lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "")
        
        # 简单确认词列表
        simple_responses = {
            "ok", "okay", "yes", "yeah", "yep", "sure", "right", "correct", 
            "good", "great", "nice", "cool", "awesome", "perfect", "exactly",
            "i see", "got it", "understood", "makes sense", "agree", "true",
            "thanks", "thank you", "alright", "fine", "sounds good"
        }
        
        # 检查是否是简单回复
        if cleaned in simple_responses:
            return True
        
        # 检查是否是非常短的回复（少于10个字符且没有技术词汇）
        if len(cleaned) < 10:
            technical_words = ["algorithm", "dijkstra", "graph", "vertex", "edge", "weight", "path", "queue", "complexity"]
            has_technical_content = any(word in cleaned for word in technical_words)
            if not has_technical_content:
                return True
        
        return False
    
    async def get_next_ai_response(self, user_message: str) -> str:
        """Generate AI response based on current phase and conversation state"""
        # Handle algorithm selection phase
        if self.current_phase == TeachingPhase.ALGORITHM_SELECTION:
            return "请从可用选项中选择一个算法开始学习！"
        
        if not self.session_started:
            return await self.start_session()
        
        # Add user message to conversation history
        self.add_to_conversation_history("user", user_message)
        
        # ✅ 使用 Topic 而不是 knowledge_point
        current_topic = self.get_current_topic()
        
        if self.current_phase == TeachingPhase.ALL_COMPLETED:
            algorithm_info = ALGORITHM_INFO[self.algorithm_selected]
            return await llm_service.generate_response([
                {"role": "system", "content": f"生成一条祝贺消息，庆祝我们一起完成了{algorithm_info['name']}的所有话题。用中文回复，表现得热情洋溢，展示成就感。"}
            ])
        
        if not current_topic:
            # 所有 Topics 都完成了
            self.current_phase = TeachingPhase.ALL_COMPLETED
            algorithm_info = ALGORITHM_INFO[self.algorithm_selected]
            return await llm_service.generate_response([
                {"role": "system", "content": f"生成一条祝贺消息，庆祝我们一起完成了{algorithm_info['name']}的所有话题。用中文回复，表现得非常热情，展示强烈的成就感。"}
            ])
        
        self.teaching_rounds += 1
        
        # ✅ 检查当前 Topic 是否所有小点都完成
        if current_topic.is_all_completed():
            return await self._handle_topic_completion(current_topic)
        
        # Student always teaches, AI always learns
        # Get last teaching evaluation to check if student made an error
        last_evaluation = self.teaching_evaluations[-1] if self.teaching_evaluations else None
        
        # ✅ AI Buddy 基于 Topic 标题学习（不知道具体的 sub_items）
        response = await llm_service.generate_ai_topic_learning_response(
            current_topic.title,
            user_message,
            self.conversation_history,
            self.teaching_rounds,
            last_evaluation,
            self.algorithm_selected
        )
        
        # Add AI response to conversation history
        self.add_to_conversation_history("bot", response)
        return response
    
    async def _handle_topic_completion(self, current_topic: Topic) -> str:
        """✅ Handle transition to next topic"""
        # Topic 已经在 check_and_unlock_sub_items 中给过 +10 能量了
        # 这里只处理过渡消息
        
        print(f"✅ Topic completed: {current_topic.title}")
        
        # 检查是否所有 Topics 都完成
        if self.current_topic_index >= len(self.topics) - 1:
            # 最后一个 Topic 也完成了
            self.current_phase = TeachingPhase.ALL_COMPLETED
            algorithm_info = ALGORITHM_INFO[self.algorithm_selected]
            return await llm_service.generate_response([
                {"role": "system", "content": f"生成一条热情洋溢的祝贺消息，庆祝我们一起完成了{algorithm_info['name']}的所有话题。用中文回复，表现得非常热情，展示强烈的成就感。"}
            ])
        
        # Move to next topic (已经在 advance_to_next_topic 中推进了)
        self.reset_rounds_for_new_knowledge_point()
        next_topic = self.get_current_topic()
        
        # Debug info
        print(f"🔄 Topic switching: current index={self.current_topic_index}")
        if next_topic:
            print(f"📚 Next topic: {next_topic.title}")
        
        if next_topic:
            # Generate transition message with memory continuity
            print(f"🎭 Generating transition message: from '{current_topic.title}' to '{next_topic.title}'")
            transition_message = await llm_service.generate_topic_transition_message(
                current_topic.title,
                next_topic.title,
                self.conversation_history,
                self.algorithm_selected
            )
            print(f"📝 Generated transition message: {transition_message}")
            
            self.add_to_conversation_history("bot", transition_message)
            return transition_message
        
        return "出了点问题，让我们继续学习吧！"
    
    
    def get_current_status(self) -> Dict:
        """Get current teaching status"""
        current_kp = self.knowledge_manager.get_current_knowledge_point()
        progress = self.knowledge_manager.get_progress_stats()
        
        return {
            "phase": self.current_phase.value,
            "session_started": self.session_started,
            "current_knowledge_point": {
                "id": current_kp.id if current_kp else None,
                "title": current_kp.title if current_kp else None,
                "description": current_kp.description if current_kp else None,
                "status": current_kp.status.value if current_kp else None
            } if current_kp else None,
            "progress": progress
        }
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        progress = self.knowledge_manager.get_progress_stats()
        current_kp = self.knowledge_manager.get_current_knowledge_point()
        
        return {
            "total_knowledge_points": progress["total_points"],
            "completed_knowledge_points": progress["completed_points"], 
            "current_knowledge_point": current_kp.title if current_kp else "Completed",
            "progress_percentage": progress["progress_percentage"],
            "current_phase": self.current_phase.value,
            "knowledge_points_detail": progress["knowledge_points_status"],
            "teaching_evaluations": self.teaching_evaluations,  # Teaching Helper evaluations
            "energy_stats": self.energy_manager.get_stats(),  # 🔋 能量统计数据
            # ✅ 两级 Topic 结构数据
            "topics": [topic.to_dict() for topic in self.topics],
            "current_topic_index": self.current_topic_index
        }
    
    # ✅ ========== 两级 Topic 管理方法 ==========
    
    def manually_view_sub_item(self, topic_id: str, sub_item_id: str) -> Dict:
        """
        学生主动查看二级小点
        
        ⚠️ 主动查看 ≠ 自动通过
        - 立即解除模糊
        - 标记为 manuallyViewed
        - 但不算完成，不给探索奖励
        - 仍需后续讲清才能完成
        """
        # 查找对应的 Topic 和 SubItem
        for topic in self.topics:
            if topic.id == topic_id:
                # 检查该 Topic 是否已解锁
                if not topic.unlocked:
                    return {
                        "success": False,
                        "message": "This topic is not unlocked yet"
                    }
                
                for sub_item in topic.sub_items:
                    if sub_item.id == sub_item_id:
                        if sub_item.status == SubItemStatus.LOCKED:
                            # 从 locked 变为 manuallyViewed
                            sub_item.status = SubItemStatus.MANUALLY_VIEWED
                            return {
                                "success": True,
                                "message": f"Viewed: {sub_item.title}",
                                "sub_item": sub_item.to_dict()
                            }
                        else:
                            return {
                                "success": True,
                                "message": "Already viewed or unlocked",
                                "sub_item": sub_item.to_dict()
                            }
        
        return {
            "success": False,
            "message": "Topic or sub-item not found"
        }
    
    async def check_and_unlock_sub_items(self, user_message: str, score_multiplier: float = 1.0) -> List[Dict]:
        """
        检测用户讲解是否涉及并讲清了某个二级小点
        
        两阶段逻辑：
        1. 涉及阶段：LLM检测到用户提到了某个小点
           - locked → revealedByLLM + 探索bonus（+3，不受时间影响）
        2. 讲清阶段：LLM判定用户讲清楚了
           - completed = True + 完成奖励（+5，不受时间影响）
        
        返回被解锁的二级小点列表（用于能量奖励）
        """
        if not self.topics or self.current_topic_index >= len(self.topics):
            return []
        
        current_topic = self.topics[self.current_topic_index]
        unlocked_items = []
        
        # 记录Topic完成前的状态
        topic_was_incomplete = not current_topic.is_all_completed()
        
        # 遍历当前 Topic 的所有 sub_items
        for sub_item in current_topic.sub_items:
            # 调用 LLM 检测涉及程度
            coverage_level = await llm_service.check_sub_item_coverage(
                sub_item.title,
                sub_item.keywords,
                user_message,
                self.conversation_history
            )
            
            total_energy = 0
            event_info = {
                "sub_item_id": sub_item.id,
                "sub_item_title": sub_item.title,
                "topic_title": current_topic.title,
                "energy_gain": 0,
                "events": []
            }
            
            # 阶段1：涉及（mentioned 或 explained）
            if coverage_level in ["mentioned", "explained"]:
                if sub_item.status == SubItemStatus.LOCKED:
                    # ✅ 探索解锁：locked → revealedByLLM
                    sub_item.status = SubItemStatus.REVEALED_BY_LLM
                    
                    # ⚡ 探索bonus：+3（固定，不受时间影响）
                    exploration_bonus = self.energy_manager.add_exploration_bonus(
                        sub_item.title,
                        current_topic.title
                    )
                    total_energy += exploration_bonus
                    event_info["events"].append(f"🔍 Exploration bonus +{exploration_bonus}")
            
            # 阶段2：讲清（explained）
            if coverage_level == "explained" and not sub_item.completed:
                # 标记为完成
                sub_item.completed = True
                
                # ⚡ 小点完成：+5（固定，不受时间影响）
                complete_energy = self.energy_manager.add_sub_item_complete_energy(
                    sub_item.title,
                    current_topic.title
                )
                total_energy += complete_energy
                event_info["events"].append(f"✅ Completed +{complete_energy}")
            
            # 如果有能量变化，添加到结果
            if total_energy > 0:
                event_info["energy_gain"] = total_energy
                unlocked_items.append(event_info)
        
        # 检查 Topic 是否刚刚完成
        if topic_was_incomplete and current_topic.is_all_completed():
            # ⚡ Topic 完成：+10（固定，不受时间影响）
            topic_energy = self.energy_manager.add_topic_complete_energy(current_topic.title)
            
            # 将Topic完成奖励添加到返回结果
            unlocked_items.append({
                "type": "topic_complete",
                "topic_title": current_topic.title,
                "energy_gain": topic_energy,
                "events": [f"🎉 Topic completed +{topic_energy}"]
            })
            
            # 推进到下一个 Topic
            await self.advance_to_next_topic()
        
        return unlocked_items
    
    async def advance_to_next_topic(self):
        """推进到下一个 Topic"""
        if self.current_topic_index < len(self.topics) - 1:
            self.current_topic_index += 1
            next_topic = self.topics[self.current_topic_index]
            next_topic.unlocked = True
            print(f"🔓 Topic advanced: {next_topic.title} is now unlocked")
    
    def get_current_topic(self) -> Optional[Topic]:
        """获取当前 Topic"""
        if self.topics and 0 <= self.current_topic_index < len(self.topics):
            return self.topics[self.current_topic_index]
        return None
