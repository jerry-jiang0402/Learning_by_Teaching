#!/usr/bin/env python3
"""
调试环境变量问题
"""
import os
import sys
from dotenv import load_dotenv

print("=== 环境变量调试 ===")

# 1. 检查当前工作目录
print(f"📁 当前工作目录: {os.getcwd()}")

# 2. 检查.env文件是否存在
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ .env文件存在")
    
    # 读取文件内容
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 .env文件大小: {len(content)} 字符")
    print("📄 .env文件内容:")
    print("=" * 50)
    print(repr(content))  # 显示所有隐藏字符
    print("=" * 50)
    
    # 逐行分析
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'OPENAI_API_KEY' in line:
            print(f"🔍 第{i}行 (OPENAI_API_KEY): {repr(line)}")
            if '=' in line:
                key, value = line.split('=', 1)
                print(f"   键: {repr(key)}")
                print(f"   值: {repr(value)}")
                print(f"   值长度: {len(value)}")
else:
    print(f"❌ .env文件不存在")

print("\n=== 环境变量读取测试 ===")

# 3. 测试不同的加载方式
print("🧪 测试1: 直接从系统环境变量读取")
sys_api_key = os.environ.get('OPENAI_API_KEY')
print(f"   系统环境变量: {repr(sys_api_key)}")
print(f"   长度: {len(sys_api_key) if sys_api_key else 0}")

print("\n🧪 测试2: 使用dotenv加载后读取")
load_dotenv()
dotenv_api_key = os.getenv('OPENAI_API_KEY')
print(f"   dotenv加载后: {repr(dotenv_api_key)}")
print(f"   长度: {len(dotenv_api_key) if dotenv_api_key else 0}")

print("\n🧪 测试3: 强制重新加载dotenv")
load_dotenv(override=True)
reload_api_key = os.getenv('OPENAI_API_KEY')
print(f"   重新加载后: {repr(reload_api_key)}")
print(f"   长度: {len(reload_api_key) if reload_api_key else 0}")

print("\n🧪 测试4: 指定.env文件路径")
if os.path.exists('.env'):
    load_dotenv('.env', override=True)
    specific_api_key = os.getenv('OPENAI_API_KEY')
    print(f"   指定文件加载: {repr(specific_api_key)}")
    print(f"   长度: {len(specific_api_key) if specific_api_key else 0}")

# 4. 检查所有环境变量中包含OPENAI的
print("\n=== 所有相关环境变量 ===")
for key, value in os.environ.items():
    if 'OPENAI' in key.upper():
        print(f"🔑 {key}: {repr(value)} (长度: {len(value)})")

print("\n=== 调试完成 ===")
