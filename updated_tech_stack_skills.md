# Required Skills & Tech Stack (Updated)

## 1. Core Framework
*   **Frontend:** React (또는 Next.js), Tailwind CSS.
*   **Backend / API:** Node.js 기반 Serverless Functions.

## 2. API Integrations
*   **Google Drive API (v3):**
    *   `Recursive Folder Search`: 상위 폴더 ID를 받으면 쿼리(`mimeType = 'application/vnd.google-apps.folder'`)를 통해 하위 폴더들을 재귀적으로 탐색하고, 최종적으로 실제 문서 파일(Docs/PDF)들만 추출하여 테이블에 매핑하는 로직.
*   **Google Docs API / PDF Parsing:**
    *   텍스트뿐만 아니라 **문서 구조(Structural Elements)** 파싱 기능 추가.
    *   페이지 나누기(Page Breaks), 문단 간격(Line Spacing), 표(Tables) 데이터를 인식하여 서식 및 레이아웃 오류를 분석할 수 있도록 데이터 전처리.
*   **Google Sheets API (또는 CSV Export):**
    *   대시보드 테이블의 분석 결과를 Google Sheet 파일로 직접 생성하거나, 브라우저에서 `.csv` / `.xlsx` 형태로 즉시 다운로드(Export)하는 라이브러리(예: `SheetJS` 등) 활용.

## 3. Authentication
*   Google OAuth 2.0 (Drive Read-only 및 Sheets Write 권한 필요).

## 4. AI & Prompt Engineering
*   **LLM API (OpenAI / Gemini 등)**
*   **Advanced Document Analysis:** 단순 텍스트 이해를 넘어, 문항의 페이지 배치 및 시각적 구성(줄 간격 등)을 추론하고 검증하는 복합 프롬프트 구성.