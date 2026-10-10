"""Google Drive folder synchronization and file listing endpoints."""

from typing import Optional
from fastapi import APIRouter, Query

from app.api.auth import get_current_access_token
from app.core.config import settings
from app.models.schemas import DriveFolderSyncRequest, DriveFolderSyncResponse
from app.services.drive_service import drive_service

router = APIRouter(prefix="/api/drive", tags=["Google Drive"])


@router.get("/files", response_model=DriveFolderSyncResponse)
def list_folder_files(
    folder_id: Optional[str] = Query(None, description="Google Drive Folder ID to inspect")
) -> DriveFolderSyncResponse:
    """Fetch list of examination files within the specified Google Drive folder.

    Args:
        folder_id: Optional folder ID, defaults to configured semester folder.

    Returns:
        DriveFolderSyncResponse containing parsed examination entries.
    """
    target_folder = folder_id.strip() if folder_id and folder_id.strip() else settings.DEFAULT_FOLDER_ID
    token = get_current_access_token()
    return drive_service.get_folder_files(target_folder, access_token=token)


@router.post("/sync", response_model=DriveFolderSyncResponse)
def sync_folder(request: DriveFolderSyncRequest) -> DriveFolderSyncResponse:
    """Trigger synchronization for a specific Google Drive folder ID.

    Args:
        request: DriveFolderSyncRequest containing folder_id.

    Returns:
        DriveFolderSyncResponse containing refreshed list of exam files.
    """
    target_folder = request.folder_id.strip() or settings.DEFAULT_FOLDER_ID
    token = get_current_access_token()
    return drive_service.get_folder_files(target_folder, access_token=token)
