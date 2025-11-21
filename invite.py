#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT Team 邀请工具
简单易用的命令行工具，用于通过API发送Team邀请
"""

import requests
import json
import re
import os
import sys

# 跨平台彩色输出
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # 如果没有colorama，定义空的颜色代码
    class Fore:
        GREEN = RED = YELLOW = CYAN = BLUE = MAGENTA = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

# ========== 配置 ==========

# 默认API地址（可以修改为你的服务器地址）
DEFAULT_API_URL = "https://team.8888822.xyz/api/invite"

# ========== 工具函数 ==========

def print_header(text):
    """打印标题"""
    if HAS_COLOR:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{Fore.CYAN}{Style.BRIGHT}  {text}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
    else:
        print(f"\n{'=' * 60}")
        print(f"  {text}")
        print(f"{'=' * 60}")

def print_success(text):
    """打印成功信息"""
    if HAS_COLOR:
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    else:
        print(f"✓ {text}")

def print_error(text):
    """打印错误信息"""
    if HAS_COLOR:
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")
    else:
        print(f"✗ {text}")

def print_warning(text):
    """打印警告信息"""
    if HAS_COLOR:
        print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")
    else:
        print(f"⚠ {text}")

def print_info(text):
    """打印信息"""
    if HAS_COLOR:
        print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")
    else:
        print(f"ℹ {text}")

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_card_key(card_key):
    """格式化卡密，自动添加-"""
    # 移除所有非字母数字字符
    cleaned = re.sub(r'[^A-Za-z0-9]', '', card_key).upper()

    # 如果长度是12，格式化为 XXXX-XXXX-XXXX
    if len(cleaned) == 12:
        return f"{cleaned[:4]}-{cleaned[4:8]}-{cleaned[8:]}"

    # 否则返回原样
    return cleaned

def send_invite(api_url, card_key, email):
    """发送邀请请求"""
    try:
        print_info("正在连接服务器...")

        response = requests.post(
            api_url,
            json={
                "card_key": card_key,
                "email": email
            },
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )

        print_info(f"HTTP 状态码: {response.status_code}")

        # 尝试解析JSON响应
        try:
            data = response.json()
        except:
            data = {"message": response.text}

        # 根据状态码处理
        if response.status_code == 200:
            print_success("邀请发送成功！")
            if isinstance(data, dict):
                if data.get('success'):
                    print_info(data.get('message', '请查收邮箱中的 ChatGPT Team 邀请邮件'))
                else:
                    print_error(data.get('message', '未知错误'))
            return True

        elif response.status_code == 400:
            print_error("请求参数错误！")
            if isinstance(data, dict):
                msg = data.get('message') or data.get('detail', {}).get('message', '未知错误')
                print_error(f"错误信息: {msg}")
            print_warning("\n可能的原因:")
            print("  • 卡密格式不正确")
            print("  • 卡密已被使用")
            print("  • 邮箱格式不正确")
            print("  • 没有可用的 Team")
            return False

        elif response.status_code == 404:
            print_error("API 接口不存在！")
            print_warning(f"请检查 API 地址是否正确: {api_url}")
            return False

        elif response.status_code == 500:
            print_error("服务器内部错误！")
            print_warning("请联系管理员检查服务器状态")
            return False

        else:
            print_error(f"未知错误 (HTTP {response.status_code})")
            if isinstance(data, dict):
                print_error(f"错误信息: {data.get('message', '无详细信息')}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("无法连接到服务器！")
        print_warning("\n可能的原因:")
        print("  • API 地址错误")
        print("  • 服务器未运行")
        print("  • 网络连接问题")
        print(f"\n当前API地址: {api_url}")
        return False

    except requests.exceptions.Timeout:
        print_error("请求超时！")
        print_warning("服务器响应时间过长 (超过 30 秒)")
        return False

    except Exception as e:
        print_error(f"发生异常: {str(e)}")
        return False

# ========== 主程序 ==========

def main():
    """主函数"""
    print_header("ChatGPT Team 邀请工具")

    # 检查是否安装了colorama
    if not HAS_COLOR:
        print_warning("提示: 安装 colorama 可以获得彩色输出体验")
        print_warning("安装命令: pip install colorama")

    print(f"\n{Fore.MAGENTA if HAS_COLOR else ''}欢迎使用 ChatGPT Team 邀请工具！{Style.RESET_ALL if HAS_COLOR else ''}\n")

    # 1. 输入API地址
    print(f"{Fore.CYAN if HAS_COLOR else ''}请输入API地址{Style.RESET_ALL if HAS_COLOR else ''}")
    print(f"直接回车使用默认地址: {DEFAULT_API_URL}")
    api_url = input(f"{Fore.WHITE if HAS_COLOR else ''}API地址 > {Style.RESET_ALL if HAS_COLOR else ''}").strip()

    if not api_url:
        api_url = DEFAULT_API_URL
        print_info(f"使用默认地址: {api_url}")

    print()  # 空行

    # 2. 输入卡密
    while True:
        print(f"{Fore.CYAN if HAS_COLOR else ''}请输入卡密{Style.RESET_ALL if HAS_COLOR else ''}")
        print("格式: XXXX-XXXX-XXXX 或 XXXXXXXXXXXX")
        card_key = input(f"{Fore.WHITE if HAS_COLOR else ''}卡密 > {Style.RESET_ALL if HAS_COLOR else ''}").strip()

        if not card_key:
            print_error("卡密不能为空！")
            continue

        # 格式化卡密
        formatted_key = format_card_key(card_key)
        print_info(f"卡密格式化为: {formatted_key}")
        break

    print()  # 空行

    # 3. 输入邮箱
    while True:
        print(f"{Fore.CYAN if HAS_COLOR else ''}请输入接收邀请的邮箱地址{Style.RESET_ALL if HAS_COLOR else ''}")
        email = input(f"{Fore.WHITE if HAS_COLOR else ''}邮箱 > {Style.RESET_ALL if HAS_COLOR else ''}").strip()

        if not email:
            print_error("邮箱不能为空！")
            continue

        if not validate_email(email):
            print_error("邮箱格式不正确！")
            print_warning("请输入有效的邮箱地址，例如: user@example.com")
            continue

        print_success(f"邮箱格式正确: {email}")
        break

    print()  # 空行

    # 4. 确认信息
    print_header("请确认信息")
    print(f"API 地址: {Fore.YELLOW if HAS_COLOR else ''}{api_url}{Style.RESET_ALL if HAS_COLOR else ''}")
    print(f"卡密:     {Fore.YELLOW if HAS_COLOR else ''}{formatted_key}{Style.RESET_ALL if HAS_COLOR else ''}")
    print(f"邮箱:     {Fore.YELLOW if HAS_COLOR else ''}{email}{Style.RESET_ALL if HAS_COLOR else ''}")
    print()

    confirm = input(f"{Fore.WHITE if HAS_COLOR else ''}确认发送邀请？ (y/n) > {Style.RESET_ALL if HAS_COLOR else ''}").strip().lower()

    if confirm not in ['y', 'yes', '是']:
        print_warning("已取消操作")
        return

    print()  # 空行

    # 5. 发送请求
    print_header("正在发送邀请")
    success = send_invite(api_url, card_key, email)

    print()  # 空行

    # 6. 显示结果
    if success:
        print_header("操作成功")
        print_success("邀请已成功发送！")
        print_info("请查收邮箱中的 ChatGPT Team 邀请邮件")
    else:
        print_header("操作失败")
        print_error("邀请发送失败，请检查上面的错误信息")

    print()  # 空行

    # 7. 询问是否继续
    if input(f"{Fore.WHITE if HAS_COLOR else ''}是否继续发送其他邀请？ (y/n) > {Style.RESET_ALL if HAS_COLOR else ''}").strip().lower() in ['y', 'yes', '是']:
        print("\n" * 2)
        main()  # 递归调用
    else:
        print_info("感谢使用，再见！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW if HAS_COLOR else ''}操作已取消{Style.RESET_ALL if HAS_COLOR else ''}")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n程序异常: {str(e)}")
        sys.exit(1)
