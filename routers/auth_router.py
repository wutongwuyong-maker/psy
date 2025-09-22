from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError

from ..config import settings
from ..crud import authenticate_admin_user
from ..database import get_db_session
from ..schemas import Token
from ..utils.logging_utils import operation_logger, audit_logger

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token, summary="获取JWT令牌")
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
):
    admin_user = authenticate_admin_user(db, form_data.username, form_data.password)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": admin_user.username}, access_token_expires)

    try:
        login_ip = request.client.host if request.client else "unknown_ip"
        audit_logger.info(f"用户 '{admin_user.username}' 从 IP '{login_ip}' 登录成功")
        operation_logger.info(
            f"登录详情: 用户 '{admin_user.username}', IP '{login_ip}', 时间 {datetime.utcnow().isoformat()}"
        )
    except Exception:
        pass

    return {"access_token": access_token, "token_type": "bearer"}

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY 未配置，无法生成 Token")
    algorithm = settings.ALGORITHM or "HS256"

    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {**data, "exp": expire}

    try:
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=algorithm)
    except JWTError as e:
        raise RuntimeError(f"JWT 生成失败: {e}") from e
