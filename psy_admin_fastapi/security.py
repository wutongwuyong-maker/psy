# psy_admin_fastapi/security.py

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Optional
import hashlib

from config import settings # 导入你的配置

# 强制使用简单的哈希方法，避免bcrypt问题
bcrypt_available = False
print("Using simple SHA-256 hash for passwords")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否与哈希密码匹配"""
    # 简单的哈希验证
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    """生成密码的哈希值"""
    # 简单的哈希
    return hashlib.sha256(password.encode()).hexdigest()

# 注意：create_access_token 函数通常放在 main.py 中，因为 JWT 的生成更靠近认证逻辑。
# 但如果你希望把它完全封装到 security.py 中，也可以。
# 目前你已经在 main.py 中有了这个函数，所以 security.py 暂时不需要包含它。
# 如果未来你想将 JWT 相关的逻辑也集中管理，可以考虑将 main.py 中的 create_access_token 移到这里。
