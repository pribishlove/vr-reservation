import jwt
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, Response, Request, HTTPException, Depends
from config.config import SECRET_JWT, JWT_ALGORITHM, COOKIE_LIFETIME, JWT_TOKEN_LIFETIME
from src.schemas.user_schema import UserSchema
from src.models.users import user
from config.database import get_async_session


class JWTManager():
    def __init__(self, status: status = status.HTTP_204_NO_CONTENT) -> None:
        self.response = Response(status_code=status)
        self.cookie_name = 'vr_headset_booking'
        self.max_age = COOKIE_LIFETIME,
        self.secure = True,
        self.httponly = True,
        self.samesite = "none"

    def get_login_response_with_cookie(self, user_id: str) -> Response:
        self.response.set_cookie(
            self.cookie_name,
            self._create_token(user_id),
            max_age=self.max_age,
            secure=self.secure,
            httponly=self.httponly,
            samesite=self.samesite
        )
        return self.response
    
    def get_logout_response_with_cookie(self) -> Response:
        self.response.set_cookie(
            self.cookie_name,
            '',
            max_age=0,
            secure=self.secure,
            httponly=self.httponly,
            samesite=self.samesite
        )
        return self.response

    def _create_token(self, user_id: str) -> str:
        data = {"sub": user_id}
        payload = data.copy()

        if JWT_TOKEN_LIFETIME:
            expire = datetime.now(timezone.utc) + timedelta(seconds=JWT_TOKEN_LIFETIME)
            payload["exp"] = expire

        token = jwt.encode(payload, SECRET_JWT, algorithm=JWT_ALGORITHM)

        return token
    
    async def get_token_from_cookie(self, request: Request) -> str:
        token = request.cookies.get(self.cookie_name)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
        return token
    
    def get_user_id_by_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, SECRET_JWT, algorithms=[JWT_ALGORITHM])
            user_id = payload.get('sub')
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
        return user_id
    

jwt_manager = JWTManager()
async def get_current_user(
    token: str = Depends(jwt_manager.get_token_from_cookie),
    session: AsyncSession = Depends(get_async_session)
) -> UserSchema:
    user_id = jwt_manager.get_user_id_by_token(token)
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid token')
    
    query = select(user).where(user.c.id == user_uuid)
    current_user = (await session.execute(query)).fetchone()

    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not exists')
    
    return UserSchema.from_orm(current_user)


async def get_current_superuser(
    user_schema: UserSchema = Depends(get_current_user)
) -> UserSchema:
    if not user_schema.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not have permissions to access this resource')
    return user_schema
