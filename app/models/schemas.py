"""Data transfer objects and Pydantic schemas for Inspection paper."""

from typing import Optional
from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    """Google Workspace user profile information."""

    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User display name")
    picture: Optional[str] = Field(None, description="Profile picture URL")
    role: str = Field("Vice Principal (Administrator)", description="User role in LIS")
    auth_mode: str = Field("mock", description="Authentication mode: 'mock' or 'google'")
    is_authenticated: bool = Field(True, description="Authentication flag")


class DriveFile(BaseModel):
    """Exam file entry parsed from Google Drive folder."""

    id: str = Field(..., description="Google Drive file ID")
    name: str = Field(..., description="File name including extension")
    mime_type: str = Field(..., description="Google Drive MIME type")
    web_view_link: str = Field("#", description="Direct view/edit URL in Google Drive")
    subject: str = Field("Unknown Subject", description="Course / subject title")
    teacher: str = Field("Unknown Teacher", description="Responsible teacher name")
    exam_date: str = Field("-", description="Scheduled exam date")
    is_uploaded: bool = Field(True, description="File presence flag")
    pdf_exists: bool = Field(False, description="Whether matching PDF inspection copy exists")
    quality_summary: str = Field("Pending analysis", description="AI evaluation summary or ratio check")
    quality_status: str = Field("normal", description="Status code: 'normal', 'warning', 'error'")
    memo: str = Field("-", description="Administrative memo or notes")
    file_size_formatted: str = Field("0 KB", description="Human-readable file size")


class DriveFolderSyncRequest(BaseModel):
    """Request payload to synchronize Google Drive folder."""

    folder_id: str = Field(..., description="Target Google Drive Folder ID")


class DriveFolderSyncResponse(BaseModel):
    """Response payload containing synced folder metadata and file list."""

    folder_id: str = Field(..., description="Target folder ID")
    folder_name: str = Field(..., description="Target folder display name")
    folder_path: str = Field(..., description="Breadcrumb path of folder")
    synced_at: str = Field(..., description="ISO timestamp of last sync")
    total_subjects: int = Field(0, description="Total subject count")
    uploaded_count: int = Field(0, description="Total uploaded exam files")
    approved_count: int = Field(0, description="Total approved / inspected exams")
    files: list[DriveFile] = Field(default_factory=list, description="List of exam files in folder")


class AuthStatusResponse(BaseModel):
    """Current authentication state response."""

    is_authenticated: bool = Field(..., description="Whether user is currently signed in")
    auth_mode: str = Field("mock", description="Active auth mode: 'mock' or 'google'")
    is_configured: bool = Field(False, description="Whether Google OAuth credentials are configured")
    user: Optional[UserInfo] = Field(None, description="Current authenticated user details")
