# Required Skills & Tech Stack (Updated)

## 1. Core Framework
*   **Frontend:** HTML5, CSS3, Tailwind CSS, Vanilla JavaScript (Fast & Lightweight SPA architecture).
*   **Backend / API:** Python FastAPI (Modularized Services, Clean Architecture).

## 2. API Integrations
*   **Google Drive API (v3):**
    *   `Recursive Folder Search`: 상위 폴더 ID를 받으면 쿼리(`mimeType = 'application/vnd.google-apps.folder'`)를 통해 하위 폴더들을 재귀적으로 탐색하고, 최종적으로 실제 문서 파일(Docs/Word/PDF)들만 추출하여 테이블에 평면화(Flatten) 매핑하는 로직.
*   **Google Docs API / PDF Parsing:**
    *   텍스트뿐만 아니라 **문서 구조(Structural Elements)** 파싱 기능 추가.
    *   페이지 나누기(Page Breaks), 문단 간격(Line Spacing), 표(Tables) 데이터를 인식하여 서식 및 레이아웃 오류를 분석할 수 있도록 데이터 전처리.
*   **Google Sheets API (또는 Spreadsheet/CSV Export):**
    *   대시보드 테이블의 분석 결과를 Google Sheets 호환 스프레드시트 파일(`.xlsx` / `.csv`)로 즉시 다운로드(Export)하는 라이브러리(`SheetJS` / XLSX) 활용.

## 3. Authentication
*   Google OAuth 2.0 (Drive Read-only 및 사용자 프로필 권한 연동).

## 4. AI & Prompt Engineering
*   **LLM API (Gemini Pro / rules.md 엔진):**
    *   **Advanced Document Analysis (7 Checks):** 단순 텍스트 이해를 넘어, 표지 필수요소, 문법/오타, 논리적 모순, 문항 페이지 분할, 선택지 페이지 분할, 줄 간격 일관성, 교과목별 시험 시간(영어/수학/과학 90분, 기타 60분) 대비 문항 수 밸런스를 종합 검증하는 7단계 복합 프롬프트 구성.