# System Rules & Prompt Guidelines (Updated)

## 1. Exam Quality Evaluation Rule (Deep Analysis Prompt)
AI가 시험지 데이터를 읽고 `시험 Quality`를 평가할 때, 다음 7가지 심층 점검 항목을 반드시 수행하고 결과를 리포트한다.

- **Check 1: Header Information (기본 정보 표기)**
  - 첫 페이지 상단 표나 머리말에 [교과명, 담당 교사명, 시험 날짜, 학기명(Mid-term/Final 등)] 4가지 필수 요소가 모두 정확히 기재되어 있는지 확인.
- **Check 2: Grammar & Typos (문법 및 오타)**
  - 각 문제의 지문과 질문을 분석하여 맞춤법, 오타, 어색한 문법(특히 영어 지문)이 있는지 검수.
- **Check 3: Logical Errors (문제 오류)**
  - 문제 자체에 논리적 모순이 있거나, 정답을 도출할 수 없는 치명적인 출제 오류가 있는지 점검.
- **Check 4: Question Pagination (문제 분할 출제)**
  - 하나의 문제(지문+질문)가 페이지 중간에 잘려서 다음 페이지로 넘어가는지 문서 구조 메타데이터를 통해 확인.
- **Check 5: Options Pagination (선택지 분할 출제)**
  - 다지선다형 문제의 예문(A, B, C, D)이 같은 페이지에 있지 않고 다음 페이지로 분리되어 있는지 확인.
- **Check 6: Formatting Consistency (줄 간격 유지)**
  - 각 문제와 문제 사이, 지문과 선택지 사이의 줄 간격(Line spacing)이 시험지 전체에 걸쳐 일정하게 유지되고 있는지 검토.
- **Check 7: Time vs. Workload Balance (시간 대비 문항 수)**
  - 교과목을 인식하여 제한 시간 매핑: [영어, 수학, 과학 = 90분 / 기타 모든 교과 = 60분].
  - 각 과목별 제한 시간 대비 총 문항 수(객관식+주관식)를 계산하여, 시험 시간이 부족하거나 너무 남을 가능성이 있는 문제 수인지 분석 및 조언.

## 2. Deep Folder Search Rule
- 사용자가 '상위 폴더(예: Mid-term Folder)'의 URL이나 ID를 입력하면, 시스템은 그 안의 하위 폴더(과목 폴더)들만 보여주는 것이 아니라, 하위 폴더를 모두 뚫고 들어가 **최종 시험지 파일(Docs, Word 등) 단위로 데이터를 평면화(Flatten)**하여 테이블에 직접 출력해야 한다.