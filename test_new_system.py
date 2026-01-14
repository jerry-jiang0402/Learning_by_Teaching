#!/usr/bin/env python3
"""
测试新的学习伙伴系统
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from knowledge_points import KnowledgePointManager
from teaching_flow import TeachingFlowManager

def test_knowledge_points():
    """测试知识点管理器"""
    print("=== 测试知识点管理器 ===")
    manager = KnowledgePointManager()
    
    print(f"总知识点数: {len(manager.get_all_knowledge_points())}")
    
    current = manager.get_current_knowledge_point()
    if current:
        print(f"当前知识点: {current.title}")
        print(f"描述: {current.description}")
    
    stats = manager.get_progress_stats()
    print(f"进度统计: {stats}")
    print()

async def test_teaching_flow():
    """测试教学流程管理器"""
    print("=== Testing Teaching Flow Manager ===")
    flow = TeachingFlowManager()
    
    # 开始会话
    opening = await flow.start_session()
    print("Opening message:")
    print(opening)
    print()
    
    # 模拟第一个知识点（AI教学或学生教学）
    print("=== First Knowledge Point ===")
    current_teacher = flow.knowledge_manager.get_current_teacher()
    print(f"Current teacher: {current_teacher}")
    
    if current_teacher == "ai":
        # AI教学阶段
        ai_response1 = await flow.get_next_ai_response("Hello, I'm ready to learn!")
        print("AI Teaching Response:")
        print(ai_response1)
        print()
        
        # 学生回应
        student_response = "A shortest path problem is about finding the path with minimum weight between vertices in a graph"
        ai_response2 = await flow.get_next_ai_response(student_response)
        print("AI Follow-up Response:")
        print(ai_response2)
        print()
    else:
        # 学生教学阶段
        student_teaching = "Let me explain shortest path problem. It's about finding the minimum cost path from source to all other vertices using weighted edges in a graph."
        ai_response = await flow.get_next_ai_response(student_teaching)
        print("AI Learning Response:")
        print(ai_response)
        print()
    
    # 获取状态
    status = flow.get_current_status()
    print("Current Status:")
    print(f"Phase: {status['phase']}")
    print(f"Current KP: {status['current_knowledge_point']['title'] if status['current_knowledge_point'] else 'None'}")
    print(f"Current Teacher: {flow.knowledge_manager.get_current_teacher()}")
    print()

def test_dashboard_stats():
    """测试仪表板统计"""
    print("=== 测试仪表板统计 ===")
    flow = TeachingFlowManager()
    flow.start_session()
    
    stats = flow.get_dashboard_stats()
    print("仪表板统计:")
    for key, value in stats.items():
        if key != 'knowledge_points_detail':
            print(f"  {key}: {value}")
    
    print("知识点详情:")
    for i, kp in enumerate(stats['knowledge_points_detail']):
        print(f"  {i+1}. {kp['title']} - {kp['status']}")
    print()

async def main():
    print("Testing New Learning Partner System")
    print("=" * 50)
    
    try:
        test_knowledge_points()
        await test_teaching_flow()
        test_dashboard_stats()
        
        print("All tests passed!")
        print("\nSystem is ready! You can start the server for testing")
        print("Run command: python backend/main.py")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
