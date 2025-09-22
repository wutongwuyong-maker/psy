# psy_admin_fastapi/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import BaseModel

from psy_admin_fastapi import crud, models
from psy_admin_fastapi.database import get_db_session # 导入数据库会话
from psy_admin_fastapi.config import settings # 导入你的配置

# OAuth2PasswordBearer 用于处理 OAuth2 的密码流认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # 与实际登录路由保持一致

class TokenData(BaseModel):
    username: str | None = None

async def get_current_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)):
    """
    根据JWT令牌获取当前认证的管理员用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    admin_user = crud.get_admin_user_by_username(db, username=token_data.username)
    if admin_user is None:
        raise credentials_exception

    # 可选：进一步检查用户状态，例如是否被禁用 (根据你的 AdminUser 模型和业务需求)
    # if not admin_user.is_active:
    #      raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="您的账户已被禁用，请联系管理员。",
    #     )

    return admin_user
