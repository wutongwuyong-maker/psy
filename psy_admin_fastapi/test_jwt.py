#!/usr/bin/env python3
"""
测试JWT验证的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jose import JWTError, jwt
from config import settings

def test_jwt_decode():
    """测试JWT解码"""
    print("正在测试JWT解码...")
    
    # 使用之前获取的token
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NjA0MjJjMn0.EZCHzatAmtmj5Y-0kWWw9Js8t5M-jGzCNIoVCCkHjQE"
    
    try:
        # 解码token
        payload = jwt.decode(test_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"Token解码成功: {payload}")
        
        # 提取用户名
        username = payload.get("sub")
        print(f"用户名: {username}")
        
    except JWTError as e:
        print(f"JWT解码失败: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

if __name__ == "__main__":
    test_jwt_decode()
