"""Google Drive Service with hybrid real API and realistic Mock simulation."""

from datetime import datetime
import os
from typing import Any, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from app.models.schemas import DriveFile, DriveFolderSyncResponse
from app.core.config import settings


class DriveService:
    """Service to interact with Google Drive API v3 with Mock fallback."""

    def __init__(self) -> None:
        """Initialize DriveService."""
        self._mock_data_cache: dict[str, list[DriveFile]] = {}
        self._initialize_mock_dataset()

    def _initialize_mock_dataset(self) -> None:
        """Seed initial realistic mock examination files based on PRD requirements."""
        self._mock_data_cache["default"] = [
            DriveFile(
                id="gdoc_001_eng",
                name="2025_G10_Eng_Midterm.gdoc",
                mime_type="application/vnd.google-apps.document",
                web_view_link="https://docs.google.com/document/d/mock-g10-eng/edit",
                subject="Grade 10 English Literature",
                teacher="Teacher Kim",
                exam_date="2025-04-22",
                is_uploaded=True,
                pdf_exists=True,
                folder_path="LIS_Drive / 2025_Spring / English_Dept",
                quality_summary="Closed 25%, Open 50%, Essay 25% (Pass)",
                quality_status="normal",
                memo="PDF Final Approved",
                file_size_formatted="4.2 KB",
            ),
            DriveFile(
                id="gdoc_002_math",
                name="2025_G11_Math_Midterm.gdoc",
                mime_type="application/vnd.google-apps.document",
                web_view_link="https://docs.google.com/document/d/mock-g11-math/edit",
                subject="Grade 11 Pre-Calculus",
                teacher="Teacher Park",
                exam_date="2025-04-23",
                is_uploaded=True,
                pdf_exists=False,
                folder_path="LIS_Drive / 2025_Spring / Math_Dept",
                quality_summary="Essay 45% (Exceeds 20-40% standard)",
                quality_status="error",
                memo="Essay weight adjustment required",
                file_size_formatted="5.1 KB",
            ),
            DriveFile(
                id="docx_003_hist",
                name="2025_G9_Hist_Midterm.docx",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                web_view_link="https://drive.google.com/file/d/mock-g9-hist/view",
                subject="Grade 9 World History",
                teacher="Teacher Lee",
                exam_date="2025-04-24",
                is_uploaded=True,
                pdf_exists=False,
                folder_path="LIS_Drive / 2025_Spring / Social_Studies",
                quality_summary="Closed 20%, Open 50%, Essay 30% (Pass)",
                quality_status="normal",
                memo="AI cognitive load rating: Moderate",
                file_size_formatted="3.8 KB",
            ),
            DriveFile(
                id="gdoc_004_kor",
                name="2025_G10_Kor_Midterm.gdoc",
                mime_type="application/vnd.google-apps.document",
                web_view_link="https://docs.google.com/document/d/mock-g10-kor/edit",
                subject="Grade 10 Korean Literature",
                teacher="Teacher Jung",
                exam_date="2025-04-25",
                is_uploaded=True,
                pdf_exists=True,
                folder_path="LIS_Drive / 2025_Spring / Korean_Dept",
                quality_summary="MCQ item #3 has fewer than 4 choices",
                quality_status="warning",
                memo="Check option revision on item #3",
                file_size_formatted="4.5 KB",
            ),
            DriveFile(
                id="empty_005_bio",
                name="-",
                mime_type="application/octet-stream",
                web_view_link="#",
                subject="Grade 12 Biology",
                teacher="Teacher Choi",
                exam_date="-",
                is_uploaded=False,
                pdf_exists=False,
                folder_path="LIS_Drive / 2025_Spring / Science_Dept",
                quality_summary="Not submitted (Analysis unavailable)",
                quality_status="error",
                memo="Reminder notification sent (Due: 04/18)",
                file_size_formatted="-",
            ),
        ]

    @staticmethod
    def clean_folder_id(raw_id: str) -> str:
        """Sanitize folder ID by stripping URLs and query params."""
        if not raw_id:
            return ""
        import re
        raw_id = raw_id.strip()
        match = re.search(r"folders/([a-zA-Z0-9_-]+)", raw_id)
        if match:
            return match.group(1)
        return raw_id.split("?")[0].split("&")[0].strip()

    def get_folder_files(
        self, folder_id: str, access_token: Optional[str] = None
    ) -> DriveFolderSyncResponse:
        """Fetch exam papers from Google Drive folder or return simulation data.

        Args:
            folder_id: Target folder identifier.
            access_token: Google OAuth access token if available.

        Returns:
            DriveFolderSyncResponse with files and metrics.
        """
        clean_id = self.clean_folder_id(folder_id)

        # If valid access token is provided and not a placeholder, query Google Drive API
        if access_token and not access_token.startswith("mock_"):
            try:
                return self._fetch_from_google_api(clean_id, access_token)
            except Exception as exc:
                err_msg = str(exc)
                print(f"[DriveService] Error querying Google Drive API: {err_msg}")
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail=f"Google Drive API Error: {err_msg}. (Make sure 'Google Drive API' is enabled in GCP Console and folder '{clean_id}' is shared with your account)."
                )

        # Simulation Mode
        files = self._mock_data_cache.get(clean_id, self._mock_data_cache["default"])
        uploaded_count = sum(1 for f in files if f.is_uploaded)
        approved_count = sum(1 for f in files if f.pdf_exists)

        return DriveFolderSyncResponse(
            folder_id=folder_id,
            folder_name="2025_Spring_Midterm_Exams",
            folder_path="LIS_Drive / 2025_Spring / Midterm_Official",
            synced_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            total_subjects=len(files),
            uploaded_count=uploaded_count,
            approved_count=approved_count,
            files=files,
        )

    def _fetch_from_google_api(self, folder_id: str, access_token: str) -> DriveFolderSyncResponse:
        """Execute recursive Google Drive API v3 calls to traverse all subfolders and flatten exam files.

        Args:
            folder_id: Root Google Drive folder ID.
            access_token: Active OAuth 2.0 access token.

        Returns:
            DriveFolderSyncResponse with parsed and flattened Google Drive files.
        """
        creds = Credentials(token=access_token)
        service = build("drive", "v3", credentials=creds)

        # 1. Retrieve root folder metadata
        folder_metadata = service.files().get(
            fileId=folder_id,
            fields="id, name"
        ).execute()
        root_folder_name = folder_metadata.get("name", "Exam Folder")

        # 2. Recursive BFS Queue: [(folder_id, current_path, depth)]
        folder_queue: list[tuple[str, str, int]] = [(folder_id, root_folder_name, 0)]
        MAX_DEPTH = 6
        MAX_TOTAL_FILES = 300

        all_doc_files: list[dict[str, Any]] = []
        pdf_basenames: set[str] = set()

        while folder_queue and len(all_doc_files) < MAX_TOTAL_FILES:
            curr_id, curr_path, depth = folder_queue.pop(0)
            if depth > MAX_DEPTH:
                continue

            page_token = None
            while True:
                query = f"'{curr_id}' in parents and trashed = false"
                results = service.files().list(
                    q=query,
                    pageSize=100,
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, mimeType, webViewLink, size, modifiedTime)"
                ).execute()

                items = results.get("files", [])
                for item in items:
                    mime = item.get("mimeType", "")
                    name = item.get("name", "Untitled")

                    # If item is a subfolder, enqueue for recursive deep inspection
                    if mime == "application/vnd.google-apps.folder":
                        folder_queue.append((item["id"], f"{curr_path} / {name}", depth + 1))
                    elif name.lower().endswith(".pdf"):
                        # Record PDF base name as verification marker
                        base_name = os.path.splitext(name)[0].strip().lower()
                        pdf_basenames.add(base_name)
                    else:
                        # Document file (Google Docs, Word, etc.)
                        item["folder_path"] = curr_path
                        all_doc_files.append(item)

                page_token = results.get("nextPageToken")
                if not page_token:
                    break

        parsed_files: list[DriveFile] = []
        for file_item in all_doc_files:
            file_name = file_item.get("name", "Untitled")
            base_name, ext = os.path.splitext(file_name)
            pdf_matched = base_name.strip().lower() in pdf_basenames

            size_bytes = int(file_item.get("size", 0))
            size_kb = f"{size_bytes / 1024:.1f} KB" if size_bytes > 0 else "-"
            folder_loc = file_item.get("folder_path", root_folder_name)

            parsed_files.append(
                DriveFile(
                    id=file_item.get("id", ""),
                    name=file_name,
                    mime_type=file_item.get("mimeType", ""),
                    web_view_link=file_item.get("webViewLink", "#"),
                    subject=base_name.replace("_", " "),
                    teacher="LIS Instructor",
                    exam_date=datetime.utcnow().strftime("%Y-%m-%d"),
                    is_uploaded=True,
                    pdf_exists=pdf_matched,
                    folder_path=folder_loc,
                    quality_summary="Ready for 7-Step Deep AI Quality Audit",
                    quality_status="normal" if pdf_matched else "warning",
                    memo="PDF Completed" if pdf_matched else "Pending PDF Inspection",
                    file_size_formatted=size_kb,
                )
            )

        uploaded_count = len(parsed_files)
        approved_count = sum(1 for f in parsed_files if f.pdf_exists)

        return DriveFolderSyncResponse(
            folder_id=folder_id,
            folder_name=root_folder_name,
            folder_path=f"LIS_Drive / {root_folder_name} (Recursive Deep Traversal)",
            synced_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            total_subjects=uploaded_count,
            uploaded_count=uploaded_count,
            approved_count=approved_count,
            files=parsed_files,
        )


drive_service = DriveService()
