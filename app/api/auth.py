"""Authentication routes supporting Google OAuth 2.0 and Mock mode."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
import requests

from app.core.config import settings
from app.models.schemas import AuthStatusResponse, UserInfo

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory session simulation for demonstration and single-user administrator
_CURRENT_SESSION: dict[str, Optional[UserInfo]] = {
    "user": UserInfo(
        email="kyumun_hwang@liskorea.org",
        name="Vice Principal Kyumun Hwang",
        picture="",
        role="Vice Principal (Administrator)",
        auth_mode="mock",
        is_authenticated=True,
    )
}
_ACCESS_TOKEN: dict[str, Optional[str]] = {"token": "mock_token_lis_admin"}


@router.get("/status", response_model=AuthStatusResponse)
def get_auth_status() -> AuthStatusResponse:
    """Retrieve current authentication status and active user info.

    Returns:
        AuthStatusResponse with user information and configuration status.
    """
    user = _CURRENT_SESSION.get("user")
    is_configured = bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)
    return AuthStatusResponse(
        is_authenticated=user is not None and user.is_authenticated,
        auth_mode=user.auth_mode if user else "mock",
        is_configured=is_configured,
        user=user,
    )


@router.get("/google/login")
def google_login() -> RedirectResponse:
    """Initiate Google OAuth 2.0 authorization code flow.

    Returns:
        RedirectResponse to Google Accounts authentication or back to app with notice.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        # Gracefully redirect back with notice instead of raw 400 error page
        return RedirectResponse(url="/?oauth_error=not_configured")

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=settings.GOOGLE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
def google_callback(code: str = Query(...)) -> RedirectResponse:
    """Handle Google OAuth 2.0 authorization code callback.

    Args:
        code: Authorization code returned by Google.

    Returns:
        RedirectResponse to main dashboard.
    """
    try:
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=settings.GOOGLE_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Fetch profile
        user_info_resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"},
            timeout=10,
        )
        profile = user_info_resp.json()

        user = UserInfo(
            email=profile.get("email", "kyumun_hwang@liskorea.org"),
            name=profile.get("name", "Vice Principal Kyumun Hwang"),
            picture=profile.get("picture", ""),
            role="Vice Principal (Administrator)",
            auth_mode="google",
            is_authenticated=True,
        )
        _CURRENT_SESSION["user"] = user
        _ACCESS_TOKEN["token"] = credentials.token

        return RedirectResponse(url="/?auth_status=success")
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
        email="kyumun_hwang@liskorea.org",
        name="Vice Principal Kyumun Hwang",
        picture="",
        role="Vice Principal (Administrator)",
        auth_mode="mock",
        is_authenticated=True,
    )
    _CURRENT_SESSION["user"] = user
    _ACCESS_TOKEN["token"] = "mock_token_lis_admin"
    return AuthStatusResponse(
        is_authenticated=True,
        auth_mode="mock",
        is_configured=bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        user=user,
    )


@router.post("/logout")
def logout() -> AuthStatusResponse:
    """Sign out the current user session.

    Returns:
        AuthStatusResponse with unauthenticated state.
    """
    _CURRENT_SESSION["user"] = None
    _ACCESS_TOKEN["token"] = None
    return AuthStatusResponse(
        is_authenticated=False,
        auth_mode="none",
        is_configured=bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        user=None,
    )


def get_current_access_token() -> Optional[str]:
    """Helper to retrieve current access token."""
    return _ACCESS_TOKEN.get("token")
