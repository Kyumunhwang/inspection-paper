# Tech Stack & API Skills

## 1. Frontend
- HTML5, CSS3, Vanilla JavaScript (최대한 가볍고 Simple한 아키텍처)
- DataTables.js (또는 유사한 가벼운 테이블 라이브러리)를 활용한 정렬 및 필터링.

## 2. Backend & Integration
- **Google Drive API (v3):**
  - `files.list`: 특정 폴더 ID를 `parents`로 지정하여 하위 파일(Docs, PDF) 검색.
  - `files.get`: 파일 메타데이터(WebViewLink 등) 가져오기.
- **Google Docs API (또는 Drive Export):**
  - 텍스트 추출용. Docs 파일을 `text/plain`으로 Export하여 AI 엔진에 전달.
- **AI Integration (Gemini API / LLM):**
  - 추출된 시험지 텍스트를 `rules.md`의 프롬프트와 결합하여 Quality Review 생성.

## 3. Authentication
- Google OAuth 2.0 (Drive Read-only 권한 필요)