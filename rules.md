# System Rules & Prompt Guidelines

## 1. Exam Quality Evaluation Rule (AI Prompting)
AI가 시험지 텍스트를 읽고 `시험 Quality` 컬럼에 출력할 내용을 생성할 때 다음 3단계를 엄격히 준수한다.

- **Step 1: Format & Header Check**
  - "Teacher, Date, Subject, Grade, Student Name, Score"가 포함된 표(Cover Page)가 존재하는지 확인.
- **Step 2: Balance of Questions (배점 비율 검증)**
  - 문서 내의 점수(points)를 합산하여 카테고리화.
  - **Midterm:** Closed (10-30%), Open (50%), Essay (20-40%)
  - **Final:** Closed (10-30%), Open (40-50%), Essay (20-50%)
  - 계산된 비율이 가이드라인을 초과하거나 미달하면 붉은색 경고 텍스트로 표시.
- **Step 3: Content & Difficulty Check**
  - 문항 내 오타나 명백한 출제 오류 확인.
  - MCQ(다지선다)가 4개 이상의 선택지를 가졌는지 확인.
  - AI가 판단한 전반적인 난이도(쉬움/적절/어려움)와 그 이유를 2~3문장으로 요약.

## 2. Status Determination Rules
- **업로드 유무:** 폴더 내 파일 존재 여부 (O/X)
- **점검완료 유무:** 확장자가 `.pdf`이고 원본과 이름이 일치하는 파일이 존재하면 '점검완료(완료)', 없으면 '미완료'.

## 3. Interaction Rule
- 시스템 구조나 기능 추가 등 중요한 변경이 발생할 수 있는 코딩 작업 전에는 반드시 사용자(교감 선생님)에게 의견을 묻고 승인(Approval)을 받은 후 개발을 진행한다.