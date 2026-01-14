#!/usr/bin/env python3
"""
验证API是否可用
"""
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def test_api():
    # 强制加载.env文件
    load_dotenv(override=True)
    
    # 获取配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    print("=== API配置 ===")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'None'}")
    print(f"🔑 长度: {len(api_key) if api_key else 0}")
    print(f"🌐 Base URL: {base_url}")
    print(f"🤖 Model: {model}")
    print()
    
    if not api_key or not base_url:
        print("❌ 配置不完整")
        return
    
    # 测试API
    print("=== 测试API连接 ===")
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 准备测试消息
        test_message = "你好，请回复'测试成功'"
        messages = [{"role": "user", "content": test_message}]
        
        print("📡 发送测试请求...")
        print(f"📤 发送内容: {test_message}")
        print("⏳ 等待AI回复...")
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=50,
            temperature=0.1
        )
        
        reply = response.choices[0].message.content
        print(f"✅ API连接成功！")
        print(f"📥 AI回复: {reply}")
        print(f"🎯 使用模型: {response.model}")
        print(f"🔢 消耗tokens: {response.usage.total_tokens if hasattr(response, 'usage') and response.usage else '未知'}")
        
        # 再测试一个更复杂的请求
        print("\n=== 第二次测试（数学计算） ===")
        math_message = "请计算 2+3 等于多少，只回答数字"
        math_messages = [{"role": "user", "content": math_message}]
        
        print(f"📤 发送内容: {math_message}")
        print("⏳ 等待AI回复...")
        
        math_response = await client.chat.completions.create(
            model=model,
            messages=math_messages,
            max_tokens=10,
            temperature=0
        )
        
        math_reply = math_response.choices[0].message.content
        print(f"📥 AI回复: {math_reply}")
        print("✅ 第二次测试也成功！")
        
    except Exception as e:
        print(f"❌ API连接失败")
        print(f"🔍 错误: {e}")
        
        # 错误分析
        error_str = str(e)
        if "401" in error_str:
            print("💡 401错误 = API密钥无效")
        elif "404" in error_str:
            print("💡 404错误 = 模型不存在或URL错误")
        elif "429" in error_str:
            print("💡 429错误 = 请求频率过高")
        elif "500" in error_str:
            print("💡 500错误 = 服务器内部错误")

if __name__ == "__main__":
    print("🚀 开始验证API...")
    asyncio.run(test_api())
    print("🏁 验证完成")
