# Product Requirements Document (PRD)
## Project: LIS Exam Paper Monitoring System

### 1. Overview
등대글로벌스쿨(LIS) 교감 선생님의 중간/기말고사 시험지 점검 업무를 자동화하고 효율화하는 모니터링 대시보드 웹 애플리케이션.

### 2. Core Features
- **[F1] 학기별 Google Drive 폴더 연동:** 매 학기 변경되는 시험지 최상위 폴더 ID를 입력하고 저장하는 환경설정 기능.
- **[F2] 대시보드 테이블 뷰:** 폴더 내 모든 교사의 시험지를 한눈에 볼 수 있는 그리드 테이블 제공.
  - 컬럼 항목: `교과목`, `담당교사`, `시험지명`, `시험날짜`, `시험지 링크(View URL)`, `업로드 유무`, `시험 Quality`, `점검완료 유무(PDF 존재 여부)`, `메모`
- **[F3] 메타데이터 자동 추출:** 업로드된 Google Docs/Word 시험지의 첫 장(Cover Page)을 파싱하여 교과목, 교사명, 시험지명, 시험날짜 자동 채움.
- **[F4] 시험지 링크 직접 접근:** 테이블의 링크 클릭 시 해당 시험지를 즉시 열어볼 수 있는 프리뷰/새창 열기 기능.
- **[F5] 점검 완료 유무 자동 확인:** 원본 파일(Docs/Docx)과 동일한 파일명의 PDF 파일이 해당 폴더에 존재하는지 확인하여 '완료' 처리.
- **[F6] AI 기반 시험지 Quality 검수 (핵심):**
  - LIS 가이드라인(Closed 10-30%, Open 40-50%, Essay 20-50%) 배점 비율 계산.
  - 4지 선다(MCQ) 옵션 규칙 및 오타/문법 오류 검수.
  - 교감 선생님을 대신하여 AI가 문항을 분석하고 예상 난이도(Cognitive Load)를 리뷰.

### 3. Design Principles
- **Simple & Minimal:** 복잡한 UI를 배제하고 데이터 테이블 중심의 직관적인 뷰 제공.
- **Permission-driven:** 교감 선생님의 구글 계정(OAuth)으로만 접근 가능한 안전한 환경.