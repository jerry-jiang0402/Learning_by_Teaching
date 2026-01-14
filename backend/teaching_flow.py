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
        self.energy_manager = KnowledgeEnergy()  # Initialize energy manager
        self.last_quality_was_red = False  # Track if last quality was red (for error correction detection)
        
        # Two-level structure state management
        self.topics: List[Topic] = []  # All Topics
        self.current_topic_index: int = 0  # Current allowed Topic index
        
    def select_algorithm(self, algorithm_type: str) -> bool:
        """Select algorithm and initialize knowledge manager"""
        if algorithm_type in ALGORITHM_INFO:
            self.algorithm_selected = algorithm_type
            # Create algorithm-specific knowledge point manager
            if algorithm_type in ALGORITHM_KNOWLEDGE_POINTS:
                self.knowledge_manager = KnowledgePointManager()
                self.knowledge_manager.knowledge_points = ALGORITHM_KNOWLEDGE_POINTS[algorithm_type].copy()
            else:
                # Default to Dijkstra algorithm
                self.knowledge_manager = KnowledgePointManager()
            
            # Initialize two-level Topic structure
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
            return "Please select an algorithm first!"
            
        self.session_started = True
        
        # Student always teaches in this mode
        self.current_phase = TeachingPhase.STUDENT_TEACHING
        
        # Set first knowledge point status
        current_kp = self.knowledge_manager.get_current_knowledge_point()
        if current_kp:
            current_kp.status = KnowledgePointStatus.STUDENT_TEACHING
        
        # Use Topic title to generate opening
        algorithm_info = ALGORITHM_INFO[self.algorithm_selected]
        current_topic = self.get_current_topic()
        first_topic_title = current_topic.title if current_topic else "the basics"
        
        # Get all Topic titles list
        topic_titles = [topic.title for topic in self.topics] if self.topics else []
        
        opening_prompt = f"""You are Algorithm Buddy, starting a learning session about {algorithm_info['name']}.

Your role: You are a confused student who needs to learn, knows very little about {algorithm_info['name']}, and often has misconceptions. You are not an expert, you are here to learn.

Learning approach:
- We will explore {len(topic_titles)} main topics of {algorithm_info['name']}: {', '.join(topic_titles)}
- In this learning session, you are the student, the human user is the teacher who will teach you these topics
- First topic: {first_topic_title}
- You know very little about this algorithm, and may even have some wrong understandings

Please generate an opening (2-3 sentences):
1. Introduce yourself, mention that you don't know much about {algorithm_info['name']} and want to learn
2. Express that you've heard of {algorithm_info['name']} but don't quite understand it (can show some vague or wrong impressions)
3. Ask the teacher to start teaching you from the first topic "{first_topic_title}"

Important requirements:
- You are a confused student role, don't act too professional
- Keep a humble, curious, slightly confused tone
- Can reveal that you have some misconceptions or vague impressions about the algorithm
- Keep it short, just 2-3 sentences
- Reply in English"""

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
        
        # Energy system: Detect if student corrected AI's error
        # If last quality was red (student made error), and this time is green or yellow (corrected), give correction bonus
        if self.last_quality_was_red and quality_level in ["green", "yellow"]:
            # Apply time multiplier
            energy_gain = self.energy_manager.add_error_correction_energy(
                current_topic.title,
                "Student corrected their previous error",
                multiplier=score_multiplier
            )
            evaluation["energy_gain"] = energy_gain
            multiplier_text = f" (×{int(score_multiplier*100)}%)" if score_multiplier < 1.0 else ""
            evaluation["energy_reason"] = f"Corrected error{multiplier_text}"
        else:
            # Energy system: Add energy based on teaching quality
            # Apply time multiplier
            energy_gain = self.energy_manager.add_quality_energy(
                quality_level,
                current_topic.title,
                evaluation.get("feedback", ""),
                multiplier=score_multiplier
            )
            evaluation["energy_gain"] = energy_gain
            multiplier_text = f" (×{int(score_multiplier*100)}%)" if score_multiplier < 1.0 else ""
            evaluation["energy_reason"] = f"Quality: {quality_level}{multiplier_text}"
        
        # Track if current quality is red
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
            return "Please select an algorithm from the available options to start learning!"
        
        if not self.session_started:
            return await self.start_session()
        
        # Add user message to conversation history
        self.add_to_conversation_history("user", user_message)
        
        # Use Topic instead of knowledge_point
        current_topic = self.get_current_topic()
        
        if self.current_phase == TeachingPhase.ALL_COMPLETED:
            algorithm_info = ALGORITHM_INFO[self.algorithm_selected]
            return await llm_service.generate_response([
                {"role": "system", "content": f"Generate a congratulatory message celebrating that we have completed all topics of {algorithm_info['name']} together. Reply in English, be enthusiastic and show a sense of achievement."}
            ])
        
        if not current_topic:
            # All Topics completed
            self.current_phase = TeachingPhase.ALL_COMPLETED
            algorithm_info = ALGORITHM_INFO[self.algorithm_selected]
            return await llm_service.generate_response([
                {"role": "system", "content": f"Generate a congratulatory message celebrating that we have completed all topics of {algorithm_info['name']} together. Reply in English, be very enthusiastic and show a strong sense of achievement."}
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
        """Handle transition to next topic"""
        # Topic already got +10 energy in check_and_unlock_sub_items
        # Here we only handle the transition message
        
        print(f"✅ Topic completed: {current_topic.title}")
        
        # Check if all Topics are completed
        if self.current_topic_index >= len(self.topics) - 1:
            # Last Topic also completed
            self.current_phase = TeachingPhase.ALL_COMPLETED
            algorithm_info = ALGORITHM_INFO[self.algorithm_selected]
            return await llm_service.generate_response([
                {"role": "system", "content": f"Generate an enthusiastic congratulatory message celebrating that we have completed all topics of {algorithm_info['name']} together. Reply in English, be very enthusiastic and show a strong sense of achievement."}
            ])
        
        # Move to next topic (already advanced in advance_to_next_topic)
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
        
        return "Something went wrong, let's continue learning!"
    
    
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
    
    # ========== Two-level Topic Management Methods ==========
    
    def manually_view_sub_item(self, topic_id: str, sub_item_id: str) -> Dict:
        """
        Student manually views a sub-item
        
        ⚠️ Manual viewing ≠ Auto completion
        - Immediately removes blur
        - Marks as manuallyViewed
        - But doesn't count as completed, no exploration bonus
        - Still needs to be explained clearly to complete
        """
        # Find the corresponding Topic and SubItem
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
        Detect if user's explanation covers and explains a sub-item clearly
        
        Two-stage logic:
        1. Mention stage: LLM detects user mentioned a sub-item
           - locked → revealedByLLM + exploration bonus (+3, not affected by time)
        2. Explain stage: LLM determines user explained it clearly
           - completed = True + completion reward (+5, not affected by time)
        
        Returns list of unlocked sub-items (for energy rewards)
        """
        if not self.topics or self.current_topic_index >= len(self.topics):
            return []
        
        current_topic = self.topics[self.current_topic_index]
        unlocked_items = []
        
            # Record Topic state before completion
            topic_was_incomplete = not current_topic.is_all_completed()
            
            # Iterate through all sub_items of current Topic
            for sub_item in current_topic.sub_items:
                # Call LLM to detect coverage level
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
            
            # Stage 1: Mentioned (mentioned or explained)
            if coverage_level in ["mentioned", "explained"]:
                if sub_item.status == SubItemStatus.LOCKED:
                    # Exploration unlock: locked → revealedByLLM
                    sub_item.status = SubItemStatus.REVEALED_BY_LLM
                    
                    # Exploration bonus: +3 (fixed, not affected by time)
                    exploration_bonus = self.energy_manager.add_exploration_bonus(
                        sub_item.title,
                        current_topic.title
                    )
                    total_energy += exploration_bonus
                    event_info["events"].append(f"🔍 Exploration bonus +{exploration_bonus}")
            
            # Stage 2: Explained clearly
            if coverage_level == "explained" and not sub_item.completed:
                # Mark as completed
                sub_item.completed = True
                
                # Sub-item complete: +5 (fixed, not affected by time)
                complete_energy = self.energy_manager.add_sub_item_complete_energy(
                    sub_item.title,
                    current_topic.title
                )
                total_energy += complete_energy
                event_info["events"].append(f"✅ Completed +{complete_energy}")
            
            # If there's energy change, add to result
            if total_energy > 0:
                event_info["energy_gain"] = total_energy
                unlocked_items.append(event_info)
        
        # Check if Topic just completed
        if topic_was_incomplete and current_topic.is_all_completed():
            # Topic complete: +10 (fixed, not affected by time)
            topic_energy = self.energy_manager.add_topic_complete_energy(current_topic.title)
            
            # Add Topic completion reward to return result
            unlocked_items.append({
                "type": "topic_complete",
                "topic_title": current_topic.title,
                "energy_gain": topic_energy,
                "events": [f"🎉 Topic completed +{topic_energy}"]
            })
            
            # Advance to next Topic
            await self.advance_to_next_topic()
        
        return unlocked_items
    
    async def advance_to_next_topic(self):
        """Advance to next Topic"""
        if self.current_topic_index < len(self.topics) - 1:
            self.current_topic_index += 1
            next_topic = self.topics[self.current_topic_index]
            next_topic.unlocked = True
            print(f"🔓 Topic advanced: {next_topic.title} is now unlocked")
    
    def get_current_topic(self) -> Optional[Topic]:
        """Get current Topic"""
        if self.topics and 0 <= self.current_topic_index < len(self.topics):
            return self.topics[self.current_topic_index]
        return None
