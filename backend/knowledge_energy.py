"""
Knowledge Energy System - 知识能量系统
追踪学生的教学质量和学习进度，通过能量值提供即时反馈
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class EnergyEvent(BaseModel):
    """能量变化事件记录"""
    timestamp: str
    event_type: str  # "quality_evaluation", "error_correction", "knowledge_point_complete"
    energy_change: int
    reason: str
    knowledge_point: str


class KnowledgeEnergy:
    """知识能量管理器"""
    
    def __init__(self, student_id: str = "default_student"):
        self.student_id = student_id
        self.current_energy: int = 0
        self.total_explanations: int = 0
        self.total_corrected_errors: int = 0
        self.last_explanation_score: int = 0
        self.energy_history: List[EnergyEvent] = []
        self.current_knowledge_point_energy: int = 0  # 当前知识点累积能量
        
    def add_quality_energy(self, quality_level: str, knowledge_point: str, feedback: str = "", multiplier: float = 1.0) -> int:
        """
        根据教学质量增加能量
        
        Args:
            quality_level: "green", "yellow", "red"
            knowledge_point: 当前知识点名称
            feedback: 评估反馈
            multiplier: 🕐 时间倍数（0.5-1.0），根据回复速度调整分数
            
        Returns:
            本次增加的能量值
        """
        energy_map = {
            "green": 10,   # 🟢 质量高：+10
            "yellow": 5,   # 🟡 质量一般：+5
            "red": 0       # 🔴 质量差：+0
        }
        
        base_energy = energy_map.get(quality_level, 0)
        energy_gain = int(base_energy * multiplier)  # 🕐 应用时间倍数
        
        if energy_gain > 0:
            self.current_energy += energy_gain
            self.current_knowledge_point_energy += energy_gain
            self.total_explanations += 1
            self.last_explanation_score = energy_gain
            
            # 记录事件
            multiplier_text = f" (×{int(multiplier*100)}%)" if multiplier < 1.0 else ""
            event = EnergyEvent(
                timestamp=datetime.now().isoformat(),
                event_type="quality_evaluation",
                energy_change=energy_gain,
                reason=f"Quality: {quality_level.upper()}{multiplier_text} - {feedback[:50]}",
                knowledge_point=knowledge_point
            )
            self.energy_history.append(event)
            
        return energy_gain
    
    def add_error_correction_energy(self, knowledge_point: str, error_description: str = "", multiplier: float = 1.0) -> int:
        """
        学生纠正AI错误时增加能量
        
        Args:
            knowledge_point: 当前知识点名称
            error_description: 错误描述
            multiplier: 🕐 时间倍数（0.5-1.0），根据回复速度调整分数
            
        Returns:
            本次增加的能量值
        """
        base_energy = 15  # 纠正AI错误基础值：+15
        energy_gain = int(base_energy * multiplier)  # 🕐 应用时间倍数
        
        self.current_energy += energy_gain
        self.current_knowledge_point_energy += energy_gain
        self.total_corrected_errors += 1
        self.last_explanation_score = energy_gain
        
        # 记录事件
        multiplier_text = f" (×{int(multiplier*100)}%)" if multiplier < 1.0 else ""
        event = EnergyEvent(
            timestamp=datetime.now().isoformat(),
            event_type="error_correction",
            energy_change=energy_gain,
            reason=f"Corrected AI error{multiplier_text}: {error_description[:50]}",
            knowledge_point=knowledge_point
        )
        self.energy_history.append(event)
        
        return energy_gain
    
    def add_exploration_bonus(self, sub_item_title: str, topic_title: str) -> int:
        """
        ✅ 探索bonus：从locked状态自动解锁（LLM检测到涉及）
        
        Args:
            sub_item_title: 解锁的二级小点名称
            topic_title: 所属的一级 Topic 名称
            
        Returns:
            本次增加的能量值（固定+3，不受时间影响）
        """
        energy_gain = 3  # 探索bonus：+3（固定）
        
        self.current_energy += energy_gain
        self.current_knowledge_point_energy += energy_gain
        self.last_explanation_score = energy_gain
        
        # 记录事件
        event = EnergyEvent(
            timestamp=datetime.now().isoformat(),
            event_type="exploration_bonus",
            energy_change=energy_gain,
            reason=f"🔍 Exploration bonus: {sub_item_title}",
            knowledge_point=topic_title
        )
        self.energy_history.append(event)
        
        return energy_gain
    
    def add_sub_item_complete_energy(self, sub_item_title: str, topic_title: str) -> int:
        """
        ✅ 讲清一个二级小点
        
        Args:
            sub_item_title: 完成的二级小点名称
            topic_title: 所属的一级 Topic 名称
            
        Returns:
            本次增加的能量值（固定+5，不受时间影响）
        """
        energy_gain = 5  # 讲清一个小点：+5（固定）
        
        self.current_energy += energy_gain
        self.current_knowledge_point_energy += energy_gain
        self.last_explanation_score = energy_gain
        
        # 记录事件
        event = EnergyEvent(
            timestamp=datetime.now().isoformat(),
            event_type="sub_item_complete",
            energy_change=energy_gain,
            reason=f"✅ Completed: {sub_item_title}",
            knowledge_point=topic_title
        )
        self.energy_history.append(event)
        
        return energy_gain
    
    def add_topic_complete_energy(self, topic_title: str) -> int:
        """
        ✅ 完成一个大Topic
        
        Args:
            topic_title: 完成的 Topic 名称
            
        Returns:
            本次增加的能量值（固定+10，不受时间影响）
        """
        energy_gain = 10  # 完成一个Topic：+10（固定）
        
        self.current_energy += energy_gain
        self.current_knowledge_point_energy += energy_gain
        self.last_explanation_score = energy_gain
        
        # 记录事件
        event = EnergyEvent(
            timestamp=datetime.now().isoformat(),
            event_type="topic_complete",
            energy_change=energy_gain,
            reason=f"🎉 Topic completed: {topic_title}",
            knowledge_point=topic_title
        )
        self.energy_history.append(event)
        
        return energy_gain
    
    def add_knowledge_point_complete_energy(self, knowledge_point: str) -> int:
        """
        完成知识点时增加能量
        
        Args:
            knowledge_point: 完成的知识点名称
            
        Returns:
            本次增加的能量值（固定30）
        """
        energy_gain = 30  # 完成知识点：+30
        
        self.current_energy += energy_gain
        self.current_knowledge_point_energy += energy_gain
        self.last_explanation_score = energy_gain
        
        # 记录事件
        event = EnergyEvent(
            timestamp=datetime.now().isoformat(),
            event_type="knowledge_point_complete",
            energy_change=energy_gain,
            reason=f"Completed knowledge point: {knowledge_point}",
            knowledge_point=knowledge_point
        )
        self.energy_history.append(event)
        
        # 完成知识点后，重置当前知识点能量
        current_kp_energy = self.current_knowledge_point_energy
        self.current_knowledge_point_energy = 0
        
        return energy_gain
    
    def reset_current_knowledge_point_energy(self):
        """开始新知识点时重置当前知识点能量"""
        self.current_knowledge_point_energy = 0
    
    def get_stats(self) -> Dict:
        """
        获取能量统计数据
        
        Returns:
            包含所有能量相关数据的字典
        """
        return {
            "student_id": self.student_id,
            "current_energy": self.current_energy,
            "last_energy_change": self.last_explanation_score,
            "total_explanations": self.total_explanations,
            "total_corrected_errors": self.total_corrected_errors,
            "current_knowledge_point_energy": self.current_knowledge_point_energy,
            "recent_events": [
                {
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "energy_change": event.energy_change,
                    "reason": event.reason,
                    "knowledge_point": event.knowledge_point
                }
                for event in self.energy_history[-10:]  # 最近10条事件
            ]
        }
    
    def reset(self):
        """重置能量系统（新会话开始时）"""
        self.current_energy = 0
        self.total_explanations = 0
        self.total_corrected_errors = 0
        self.last_explanation_score = 0
        self.energy_history.clear()
        self.current_knowledge_point_energy = 0

