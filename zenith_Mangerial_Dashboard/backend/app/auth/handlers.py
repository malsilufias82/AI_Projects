from jose import JWTError

from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import TokenResponse


def generate_token_pair(user_id: str) -> TokenResponse:
    access_token = create_access_token(subject=user_id)
    refresh_token = create_refresh_token(subject=user_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


def refresh_access_token(refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise UnauthorizedException("Invalid refresh token.")

        return generate_token_pair(user_id)

    except JWTError:
        raise UnauthorizedException("Invalid or expired refresh token.")
