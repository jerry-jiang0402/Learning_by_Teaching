#!/usr/bin/env python3
"""
测试OpenAI API连接
"""
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def test_api():
    # 加载环境变量
    load_dotenv()
    
    # 获取配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    print("=== API配置检查 ===")
    print(f"🔑 API Key存在: {'是' if api_key else '否'}")
    print(f"🔑 API Key长度: {len(api_key) if api_key else 0}")
    print(f"🔑 API Key前缀: {api_key[:10] if api_key else 'None'}")
    print(f"🔑 API Key后缀: {api_key[-10:] if api_key else 'None'}")
    print(f"🔑 API Key原始内容: '{repr(api_key)}'")  # 显示隐藏字符
    print(f"🌐 Base URL: {base_url}")
    print(f"🤖 模型: {model}")
    print()
    
    # 检查API Key格式
    if api_key:
        if not api_key.startswith('sk-'):
            print("⚠️  警告：API Key应该以'sk-'开头")
        if len(api_key) != 51:
            print(f"⚠️  警告：API Key长度异常，应该是51个字符，实际是{len(api_key)}个字符")
            print("💡 建议：检查.env文件是否有多余的空格或换行符")
    
    if not api_key:
        print("❌ 错误：未找到API密钥，请检查.env文件")
        return
    
    if not base_url:
        print("❌ 错误：未找到Base URL，请检查.env文件")
        return
    
    # 测试API连接
    print("=== 测试API连接 ===")
    
    # 测试不同的模型名称
    models_to_test = [model, "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
    
    for test_model in models_to_test:
        print(f"\n🧪 测试模型: {test_model}")
        try:
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            response = await client.chat.completions.create(
                model=test_model,
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10
            )
            
            print(f"✅ 模型 {test_model} 连接成功！")
            print(f"📝 响应: {response.choices[0].message.content}")
            break  # 找到可用模型就停止
            
        except Exception as e:
            print(f"❌ 模型 {test_model} 失败: {e}")
            
            # 详细错误分析
            if "401" in str(e):
                print("💡 可能原因：API密钥无效或模型不支持")
            elif "404" in str(e):
                print("💡 可能原因：模型不存在或Base URL错误")
            elif "400" in str(e):
                print("💡 可能原因：请求参数错误")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_api())

