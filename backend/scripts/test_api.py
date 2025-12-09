"""
API 测试脚本 - 用于验证系统功能
"""
import os
import sys
import django
import requests
from decimal import Decimal

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdlabel_backend.settings')
django.setup()

BASE_URL = 'http://localhost:8000/api'

def test_login(username, password):
    """测试登录"""
    response = requests.post(
        f'{BASE_URL}/auth/login/',
        json={'username': username, 'password': password},
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful: {data['username']} (role: {data['role']})")
        return response.cookies
    else:
        print(f"✗ Login failed: {response.status_code} - {response.text}")
        return None

def test_get_task(cookies):
    """测试获取任务"""
    response = requests.get(f'{BASE_URL}/tasks/next/', cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"✓ Task retrieved: Image #{data['id']} (${data['bounty']})")
            return data
        else:
            print("  No tasks available")
            return None
    else:
        print(f"✗ Failed to get task: {response.status_code}")
        return None

def test_get_stats(cookies):
    """测试获取统计信息"""
    response = requests.get(f'{BASE_URL}/stats/', cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Stats: Accuracy {data['accuracy']*100:.1f}%, Pending ${data['pendingBalance']:.2f}")
        return data
    else:
        print(f"✗ Failed to get stats: {response.status_code}")
        return None

def main():
    """主测试函数"""
    print("=" * 60)
    print("CrowdLabel System - API Test")
    print("=" * 60)
    
    # 测试标注员登录
    print("\n1. Testing annotator login...")
    cookies = test_login('annotator1', '123')
    
    if cookies:
        # 测试获取任务
        print("\n2. Testing get available task...")
        task = test_get_task(cookies)
        
        # 测试获取统计
        print("\n3. Testing get stats...")
        test_get_stats(cookies)
        
        # 测试管理员功能（需要管理员账号）
        print("\n4. Testing admin login...")
        admin_cookies = test_login('admin', 'admin123')
        
        if admin_cookies:
            print("\n5. Testing admin endpoints...")
            response = requests.get(f'{BASE_URL}/admin/reviews/', cookies=admin_cookies)
            if response.status_code == 200:
                print(f"✓ Admin reviews endpoint accessible")
            
            response = requests.get(f'{BASE_URL}/admin/unpaid/', cookies=admin_cookies)
            if response.status_code == 200:
                unpaid = response.json()
                print(f"✓ Unpaid users: {len(unpaid)}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to server. Make sure the backend is running on http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

