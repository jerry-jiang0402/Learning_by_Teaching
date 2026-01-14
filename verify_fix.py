#!/usr/bin/env python3
"""
验证修复是否有效
"""
import os
from dotenv import load_dotenv

print("=== 验证修复 ===")

# 模拟后端代码的加载方式
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL")

print(f"🔑 API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'None'}")
print(f"🔑 API Key长度: {len(api_key) if api_key else 0}")
print(f"🌐 Base URL: {base_url}")
print(f"🤖 Model: {model}")

if api_key and len(api_key) == 51:
    print("✅ 修复成功！现在使用的是.env文件中的API Key")
else:
    print("❌ 修复失败，仍在使用系统环境变量")

print("\n=== 验证完成 ===")
