"""Authentication routes supporting Google OAuth 2.0 and Mock mode."""

import json
import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
import requests

from app.core.config import settings
from app.models.schemas import AuthStatusResponse, UserInfo

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Persistent session storage path (support Cloud Run /tmp and local)
_SESSION_FILE = Path("/tmp/lis_auth_session.json") if os.path.isdir("/tmp") else Path("data/auth_session.json")

# In-memory session holder
_CURRENT_SESSION: dict[str, Optional[UserInfo]] = {"user": None}
_ACCESS_TOKEN: dict[str, Optional[str]] = {"token": None}


def _save_session(user: Optional[UserInfo], token: Optional[str]) -> None:
    try:
        _SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "user": user.model_dump() if user else None,
                "token": token,
            }, f)
    except Exception as exc:
        print(f"[Auth] Warning: failed to save session file: {exc}")


def _clear_session() -> None:
    _CURRENT_SESSION["user"] = None
    _ACCESS_TOKEN["token"] = None
    try:
        if _SESSION_FILE.exists():
            _SESSION_FILE.unlink()
    except Exception as exc:
        print(f"[Auth] Warning: failed to clear session file: {exc}")


def _ensure_loaded_session(request: Optional[Request] = None) -> None:
    """Ensure in-memory session is populated from file or cookie."""
    if _CURRENT_SESSION["user"] is not None and _ACCESS_TOKEN["token"] is not None:
        return

    # 1. Try loading from persistent file
    try:
        if _SESSION_FILE.exists():
            with open(_SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                u_data = data.get("user")
                token = data.get("token")
                if u_data and token:
                    _CURRENT_SESSION["user"] = UserInfo(**u_data)
                    _ACCESS_TOKEN["token"] = token
                    return
    except Exception as exc:
        print(f"[Auth] Notice: persistent session read error: {exc}")

    # 2. Try loading from cookie
    if request:
        c_token = request.cookies.get("lis_token")
        c_email = request.cookies.get("lis_email")
        if c_token and c_email:
            user = UserInfo(
                email=c_email,
                name="Vice Principal Kyumun Hwang",
                picture="",
                role="Vice Principal (Administrator)",
                auth_mode="google",
                is_authenticated=True,
            )
            _CURRENT_SESSION["user"] = user
            _ACCESS_TOKEN["token"] = c_token
            return


@router.get("/status", response_model=AuthStatusResponse)
def get_auth_status(request: Request) -> AuthStatusResponse:
    """Retrieve current authentication status and active user info.

    Returns:
        AuthStatusResponse with user information and configuration status.
    """
    _ensure_loaded_session(request)
    user = _CURRENT_SESSION.get("user")
    is_configured = bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    # If no session and not configured, provide mock by default for quick evaluation
    # If configured and no session, return unauthenticated so user can sign in with real Google
    if user is None:
        if not is_configured:
            # Fallback to mock demo if Google credentials not configured
            mock_user = UserInfo(
                email="kyumun.hwang@gmail.com",
                name="Vice Principal Kyumun Hwang",
                picture="",
                role="Vice Principal (Administrator)",
                auth_mode="mock",
                is_authenticated=True,
            )
            return AuthStatusResponse(
                is_authenticated=True,
                auth_mode="mock",
                is_configured=False,
                user=mock_user,
            )
        else:
            return AuthStatusResponse(
                is_authenticated=False,
                auth_mode="none",
                is_configured=True,
                user=None,
            )

    return AuthStatusResponse(
        is_authenticated=user.is_authenticated,
        auth_mode=user.auth_mode,
        is_configured=is_configured,
        user=user,
    )


def _get_redirect_uri(request: Request) -> str:
    """Resolve redirect URI dynamically from request to ensure exact matching."""
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    proto = request.headers.get("x-forwarded-proto", "https")
    if host and ("run.app" in host or "localhost" in host or "127.0.0.1" in host):
        return f"{proto}://{host}/api/auth/google/callback"
    return settings.GOOGLE_REDIRECT_URI


@router.get("/google/login")
def google_login(request: Request) -> RedirectResponse:
    """Initiate Google OAuth 2.0 authorization code flow.

    Returns:
        RedirectResponse to Google Accounts authentication or back to app with notice.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        return RedirectResponse(url="/?oauth_error=not_configured")

    redirect_uri = _get_redirect_uri(request)
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=settings.GOOGLE_SCOPES,
        redirect_uri=redirect_uri,
    )
    flow.autogenerate_code_verifier = False
    flow.code_verifier = None

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account consent",
    )

    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
def google_callback(request: Request, code: str = Query(...)) -> RedirectResponse:
    """Handle Google OAuth 2.0 authorization code callback.

    Args:
        request: Incoming HTTP request.
        code: Authorization code returned by Google.

    Returns:
        RedirectResponse to main dashboard.
    """
    try:
        redirect_uri = _get_redirect_uri(request)
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=settings.GOOGLE_SCOPES,
            redirect_uri=redirect_uri,
        )
        flow.autogenerate_code_verifier = False
        flow.code_verifier = None

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Fetch user profile
        user_info_resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"},
            timeout=10,
        )
        profile = user_info_resp.json()

        user = UserInfo(
            email=profile.get("email", "kyumun.hwang@gmail.com"),
            name=profile.get("name", "Vice Principal Kyumun Hwang"),
            picture=profile.get("picture", ""),
            role="Vice Principal (Administrator)",
            auth_mode="google",
            is_authenticated=True,
        )
        _CURRENT_SESSION["user"] = user
        _ACCESS_TOKEN["token"] = credentials.token
        _save_session(user, credentials.token)

        response = RedirectResponse(url="/?auth_status=success")
        response.set_cookie(key="lis_token", value=credentials.token, max_age=86400, httponly=True, samesite="lax")
        response.set_cookie(key="lis_email", value=user.email, max_age=86400, httponly=False, samesite="lax")
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to authenticate with Google: {str(exc)}"
        )


@router.post("/mock/login")
def mock_login() -> AuthStatusResponse:
    """Switch or sign in with Mock Vice Principal credentials.

    Returns:
        AuthStatusResponse with mock session.
    """
    user = UserInfo(
        email="kyumun.hwang@gmail.com",
        name="Vice Principal Kyumun Hwang",
        picture="",
        role="Vice Principal (Administrator)",
        auth_mode="mock",
        is_authenticated=True,
    )
    _CURRENT_SESSION["user"] = user
    _ACCESS_TOKEN["token"] = "mock_token_lis_admin"
    _save_session(user, "mock_token_lis_admin")
    return AuthStatusResponse(
        is_authenticated=True,
        auth_mode="mock",
        is_configured=bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        user=user,
    )


@router.post("/logout")
def logout(response: Response) -> AuthStatusResponse:
    """Sign out the current user session.

    Returns:
        AuthStatusResponse with unauthenticated state.
    """
    _clear_session()
    response.delete_cookie(key="lis_token")
    response.delete_cookie(key="lis_email")
    return AuthStatusResponse(
        is_authenticated=False,
        auth_mode="none",
        is_configured=bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        user=None,
    )


def get_current_access_token(request: Optional[Request] = None) -> Optional[str]:
    """Helper to retrieve current access token."""
    if request:
        _ensure_loaded_session(request)
    return _ACCESS_TOKEN.get("token")
