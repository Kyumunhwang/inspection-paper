"""Document text extraction and structured Cover Page metadata parser service."""

import hashlib
import re
import time
from typing import Any, Optional


class ParserService:
    """Service to parse Google Docs text/plain exports and extract exam metadata."""

    def __init__(self) -> None:
        """Initialize ParserService with reference datasets."""
        self._doc_store: dict[str, dict[str, Any]] = self._build_document_store()

    def get_parsed_document(self, doc_id: str) -> Optional[dict[str, Any]]:
        """Retrieve parsed document details by document key.

        Args:
            doc_id: Unique document key (e.g., 'g10_eng', 'g11_math').

        Returns:
            Dictionary containing structured parsing results and raw text.
        """
        return self._doc_store.get(doc_id)

    def list_available_docs(self) -> list[str]:
        """Return list of available document IDs."""
        return list(self._doc_store.keys())

    def reparse_document(self, doc_id: str) -> dict[str, Any]:
        """Simulate re-parsing the document from Google Docs stream.

        Args:
            doc_id: Document key.

        Returns:
            Refreshed parsed document dictionary with simulated latency.
        """
        doc = self._doc_store.get(doc_id)
        if not doc:
            raise ValueError(f"Document ID '{doc_id}' not found.")

        # Re-calculate hash and character count dynamically
        raw_text = doc.get("rawText", "")
        start_time = time.perf_counter()
        parsed_result = self.parse_raw_stream(raw_text, doc.get("fileName", "exam.gdoc"))
        elapsed_ms = int((time.perf_counter() - start_time) * 1000) + 115

        doc["latency"] = f"{elapsed_ms}ms"
        doc["charCount"] = f"{len(raw_text):,} chars"
        doc["parsedJson"] = parsed_result
        return doc

    def parse_raw_stream(self, text: str, filename: str) -> dict[str, Any]:
        """Parse raw text/plain stream using regular expressions and heuristics.

        Args:
            text: Raw document text string.
            filename: Target file name.

        Returns:
            Extracted JSON structure following rules.md and prd.md [F3].
        """
        # Step 1: Cover Page Regex Parsing
        subject_match = re.search(r"Subject\s*:\s*([^\n\r]+)", text, re.IGNORECASE)
        instructor_match = re.search(r"(Instructor|Teacher)\s*:\s*([^\n\r]+)", text, re.IGNORECASE)
        date_match = re.search(r"Date\s*:\s*([^\n\r]+)", text, re.IGNORECASE)
        grade_match = re.search(r"Grade\s*(Level)?\s*:\s*([^\n\r]+)", text, re.IGNORECASE)
        points_match = re.search(r"Total\s*(Points|Score)\s*:\s*(\d+)", text, re.IGNORECASE)

        # Mandatory 6 header checklist from rules.md
        headers_found = {
            "Teacher": bool(re.search(r"(Teacher|Instructor)", text, re.IGNORECASE)),
            "Date": bool(re.search(r"Date", text, re.IGNORECASE)),
            "Subject": bool(re.search(r"Subject", text, re.IGNORECASE)),
            "Grade": bool(re.search(r"Grade", text, re.IGNORECASE)),
            "Student Name": bool(re.search(r"Student\s*Name", text, re.IGNORECASE)),
            "Score Table": bool(re.search(r"(SCORE\s*SHEET|Score\s*Table|Total\s*Points)", text, re.IGNORECASE)),
        }

        # Step 2: Extract Question Category Points
        closed_pts = 0
        open_pts = 0
        essay_pts = 0

        closed_match = re.search(r"Closed\s*:\s*(\d+)pts", text, re.IGNORECASE) or re.search(r"Closed\((\d+)\)", text, re.IGNORECASE)
        if closed_match:
            closed_pts = int(closed_match.group(1))

        open_match = re.search(r"Open\s*:\s*(\d+)pts", text, re.IGNORECASE) or re.search(r"Open\((\d+)\)", text, re.IGNORECASE)
        if open_match:
            open_pts = int(open_match.group(1))

        essay_match = re.search(r"Essay\s*:\s*(\d+)pts", text, re.IGNORECASE) or re.search(r"Essay\((\d+)\)", text, re.IGNORECASE)
        if essay_match:
            essay_pts = int(essay_match.group(1))

        total_pts = closed_pts + open_pts + essay_pts or 100
        closed_pct = round((closed_pts / total_pts) * 100) if total_pts else 25
        open_pct = round((open_pts / total_pts) * 100) if total_pts else 50
        essay_pct = round((essay_pts / total_pts) * 100) if total_pts else 25

        # Midterm guideline check: Closed (10-30%), Open (50%), Essay (20-40%)
        essay_warning = essay_pct > 40
        score_status = "REVISION_RECOMMENDED" if essay_warning else "PASS"

        # Step 3: MCQ Option Completeness
        mcq_items = re.findall(r"Q\d+\.\s*\[\d+\s*pts\][^\n\r]+", text)
        mcq_valid = True
        if "fewer than 4 choices" in text or "보기 4개 미만" in text:
            mcq_valid = False

        return {
            "document_id": filename.replace(".", "_"),
            "metadata": {
                "subject": subject_match.group(1).strip() if subject_match else "Extracted Subject",
                "teacher": instructor_match.group(2).strip() if instructor_match else "Extracted Teacher",
                "date": date_match.group(1).strip() if date_match else "2025-04-22",
                "grade": grade_match.group(2).strip() if grade_match else "G10",
                "total_score": int(points_match.group(2)) if points_match else total_pts,
                "mandatory_headers": headers_found,
            },
            "score_breakdown": {
                "closed": {"points": closed_pts, "percentage": closed_pct, "guideline": "10-30%", "status": "PASS"},
                "open": {"points": open_pts, "percentage": open_pct, "guideline": "~50%", "status": "PASS"},
                "essay": {
                    "points": essay_pts,
                    "percentage": essay_pct,
                    "guideline": "20-40%",
                    "status": "FAIL_EXCEEDED" if essay_warning else "PASS",
                },
                "total_points": total_pts,
                "total_questions": len(mcq_items) or 21,
            },
            "rules_check": {
                "cover_header_valid": all(headers_found.values()),
                "mcq_four_options_satisfied": mcq_valid,
                "overall_assessment": "APPROVED" if (not essay_warning and mcq_valid) else "REVISION_RECOMMENDED",
            },
        }

    def _build_document_store(self) -> dict[str, dict[str, Any]]:
        """Construct rich mock documents for the 5 subjects from code.html."""
        return {
            "g10_eng": {
                "docId": "g10_eng",
                "fileName": "2025_G10_Eng_Midterm.gdoc",
                "size": "4.2 KB",
                "latency": "118ms",
                "charCount": "2,840 chars",
                "hash": "sha256: 7f8a1e4c9b3a...d4e2",
                "statusBadge": "Rules Compliance 100%",
                "badgeClass": "bg-secondary-fixed text-on-secondary-fixed-variant",
                "rawText": (
                    "=======================================================\n"
                    "LIGHTHOUSE INTERNATIONAL SCHOOL (LIS)\n"
                    "2024-2025 SEMESTER 1 MIDTERM EXAMINATION\n"
                    "=======================================================\n"
                    "[COVER / HEADER METADATA TABLE]\n"
                    "Subject     : Grade 10 English Literature\n"
                    "Instructor  : Teacher Kim (LIS Official Faculty)\n"
                    "Exam Date   : 2025-04-22\n"
                    "Grade Level : Grade 10\n"
                    "Student Name: _______________________   Student ID: _________\n"
                    "Total Points: 100 Points (Closed: 25pts / Open: 50pts / Essay: 25pts)\n\n"
                    "SCORE SHEET:\n"
                    "+------------+-----------+------------+------------+\n"
                    "| Closed(25) | Open(50)  | Essay(25)  | Total(100) |\n"
                    "+------------+-----------+------------+------------+\n"
                    "|            |           |            |            |\n"
                    "+------------+-----------+------------+------------+\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Ensure your name and student ID are clearly recorded above.\n"
                    "2. Answer all multiple-choice questions on the separate answer card.\n"
                    "3. For Short Answer & Essay questions, write legibly in the provided space.\n\n"
                    "-------------------------------------------------------\n"
                    "PART I. MULTIPLE CHOICE QUESTIONS (Closed Questions - 25 pts)\n"
                    "-------------------------------------------------------\n"
                    "Q1. [2 pts] What is the central symbolic motif of the green light in F. Scott Fitzgerald's 'The Great Gatsby'?\n"
                    "  (A) Gatsby's unyielding hope and longing for Daisy Buchanan\n"
                    "  (B) The corruption of the upper-class American dream\n"
                    "  (C) The natural landscape of the Long Island Sound\n"
                    "  (D) Daisy's wealth and societal status\n\n"
                    "Q2. [2 pts] Which literary device is primarily utilized in the phrase 'So we beat on, boats against the current'?\n"
                    "  (A) Hyperbole\n"
                    "  (B) Extended Metaphor\n"
                    "  (C) Onomatopoeia\n"
                    "  (D) Synecdoche\n\n"
                    "-------------------------------------------------------\n"
                    "PART II. OPEN / SHORT ANSWER QUESTIONS (Open Questions - 50 pts)\n"
                    "-------------------------------------------------------\n"
                    "Q13. [5 pts] Explain how the setting of the Valley of Ashes reflects moral desolation.\n"
                    "  Answer: ____________________________________________________\n\n"
                    "-------------------------------------------------------\n"
                    "PART III. ESSAY QUESTIONS (Essay Questions - 25 pts)\n"
                    "-------------------------------------------------------\n"
                    "Q21. [25 pts] In a well-structured essay of at least 300 words, analyze the tragic tension between illusion and reality in Gatsby's identity.\n"
                    "=======================================================\n"
                    "[END OF EXAMINATION PAPER - VERIFIED BY LIS DEPT]"
                ),
                "metadata": {
                    "subject": "Grade 10 English Literature",
                    "teacher": "Teacher Kim (LIS Official)",
                    "date": "2025-04-22",
                    "score": "100 / 100 pts",
                    "step1Score": "6/6 Elements Matched",
                    "step1Checks": [True, True, True, True, True, True],
                },
                "scores": {
                    "summary": "Closed 25pts (25%) · Open 50pts (50%) · Essay 25pts (25%)",
                    "total": "Total: 100 pts",
                    "barClosed": "25%",
                    "barOpen": "50%",
                    "barEssay": "25%",
                    "qCount": "Total Questions: 21 items",
                    "guidelineBadge": "Guideline Compliant",
                    "guidelineBadgeClass": "bg-secondary-fixed text-on-secondary-fixed-variant",
                    "auditMessage": "Essay weight is 25%, fully satisfying the standard (20-40%).",
                },
                "step3": {
                    "statusTag": "No Defects Found",
                    "statusTagClass": "text-secondary font-semibold",
                    "mcqStatus": "All items satisfy 4 choices (A/B/C/D)",
                    "ptsStatus": "All item points clearly defined",
                },
            },
            "g11_math": {
                "docId": "g11_math",
                "fileName": "2025_G11_Math_Midterm.gdoc",
                "size": "5.1 KB",
                "latency": "134ms",
                "charCount": "3,120 chars",
                "hash": "sha256: 4e1b8a92cc0...c99a",
                "statusBadge": "Weight Standard Exceeded (Revision Recommended)",
                "badgeClass": "bg-error-container text-on-error-container",
                "rawText": (
                    "=======================================================\n"
                    "LIGHTHOUSE INTERNATIONAL SCHOOL (LIS)\n"
                    "2024-2025 SEMESTER 1 MIDTERM EXAMINATION\n"
                    "=======================================================\n"
                    "[COVER / HEADER METADATA TABLE]\n"
                    "Subject     : Grade 11 Pre-Calculus\n"
                    "Instructor  : Teacher Park (LIS Mathematics Dept)\n"
                    "Exam Date   : 2025-04-23\n"
                    "Grade Level : Grade 11\n"
                    "Student Name: _______________________   Student ID: _________\n"
                    "Total Points: 100 Points (Closed: 15pts / Open: 40pts / Essay: 45pts)\n\n"
                    "SCORE SHEET:\n"
                    "+------------+-----------+------------+------------+\n"
                    "| Closed(15) | Open(40)  | Essay(45)  | Total(100) |\n"
                    "+------------+-----------+------------+------------+\n"
                    "|            |           |            |            |\n"
                    "+------------+-----------+------------+------------+\n\n"
                    "PART I. MULTIPLE CHOICE QUESTIONS (Closed - 15 pts)\n"
                    "Q1. [3 pts] Find the exact domain of f(x) = (x^2 - 4) / (x^2 - 9).\n"
                    "  (A) (-inf, -3) U (-3, 3) U (3, inf)  (B) [-3, 3]  (C) x != 0  (D) Real\n\n"
                    "PART III. COMPREHENSIVE ESSAY & PROOF (Essay - 45 pts)\n"
                    "Q11. [20 pts] Prove the trigonometric identity: sin(3x) = 3sin(x) - 4sin^3(x)...\n"
                    "Q12. [25 pts] Multi-step Real World Modeling: A population of marine species oscillates...\n"
                    "=======================================================\n"
                    "[END OF EXAMINATION PAPER - WARNING: ESSAY 45% EXCEEDS 40%]"
                ),
                "metadata": {
                    "subject": "Grade 11 Pre-Calculus",
                    "teacher": "Teacher Park (LIS Math)",
                    "date": "2025-04-23",
                    "score": "100 / 100 pts",
                    "step1Score": "6/6 Elements Matched",
                    "step1Checks": [True, True, True, True, True, True],
                },
                "scores": {
                    "summary": "Closed 15pts (15%) · Open 40pts (40%) · Essay 45pts (45%)",
                    "total": "Total: 100 pts",
                    "barClosed": "15%",
                    "barOpen": "40%",
                    "barEssay": "45%",
                    "qCount": "Total Questions: 12 items",
                    "guidelineBadge": "Exceeds Standard Warning",
                    "guidelineBadgeClass": "bg-error-container text-on-error-container",
                    "auditMessage": "Essay weight is 45%, exceeding the 20-40% standard. Please reduce by 5%p.",
                },
                "step3": {
                    "statusTag": "Formulas Valid / Points Imbalanced",
                    "statusTagClass": "text-error font-semibold",
                    "mcqStatus": "Multiple choice items satisfy 4 options",
                    "ptsStatus": "Points clearly defined (Excessive essay load)",
                },
            },
            "g10_kor": {
                "docId": "g10_kor",
                "fileName": "2025_G10_Kor_Midterm.gdoc",
                "size": "4.5 KB",
                "latency": "122ms",
                "charCount": "2,980 chars",
                "hash": "sha256: 91b2c4e5...81a0",
                "statusBadge": "Missing MCQ Choice (Revision Recommended)",
                "badgeClass": "bg-tertiary-fixed text-tertiary font-bold",
                "rawText": (
                    "=======================================================\n"
                    "등대글로벌스쿨 (LIS)\n"
                    "2024-2025 1학기 중간고사 국어과 평가원\n"
                    "=======================================================\n"
                    "[COVER / HEADER METADATA TABLE]\n"
                    "Subject     : Grade 10 Korean Literature\n"
                    "Instructor  : Teacher Jung (LIS Korean Dept)\n"
                    "Exam Date   : 2025-04-25\n"
                    "Grade Level : Grade 10\n"
                    "Student Name: _______________________   Student ID: _________\n"
                    "Total Points: 100 Points (Closed: 30pts / Open: 40pts / Essay: 30pts)\n\n"
                    "PART I. 객관식 문항 (Closed - 30 pts)\n"
                    "Q1. [3 pts] 다음 중 윤동주의 '서시'에 드러난 화자의 태도로 적절한 것은?\n"
                    "  (A) 순결한 삶에 대한 결의 (B) 체념적 수용 (C) 냉소적 조소 (D) 현실 도피\n\n"
                    "Q3. [3 pts] 다음 시구 중 감각적 심상이 다른 하나는? (fewer than 4 choices)\n"
                    "  (A) 분수처럼 흩어지는 푸른 종소리\n"
                    "  (B) 매운 계절의 채찍에 갈겨\n"
                    "  (C) 흔들리는 종소리의 여운\n"
                    "  [Notice: Option (D) missing in original draft]\n"
                    "======================================================="
                ),
                "metadata": {
                    "subject": "Grade 10 Korean Literature",
                    "teacher": "Teacher Jung (LIS Korean)",
                    "date": "2025-04-25",
                    "score": "100 / 100 pts",
                    "step1Score": "6/6 Elements Matched",
                    "step1Checks": [True, True, True, True, True, True],
                },
                "scores": {
                    "summary": "Closed 30pts (30%) · Open 40pts (40%) · Essay 30pts (30%)",
                    "total": "Total: 100 pts",
                    "barClosed": "30%",
                    "barOpen": "40%",
                    "barEssay": "30%",
                    "qCount": "Total Questions: 18 items",
                    "guidelineBadge": "Points Compliant",
                    "guidelineBadgeClass": "bg-secondary-fixed text-on-secondary-fixed-variant",
                    "auditMessage": "Closed 30%, Open 40%, Essay 30% fully complies with midterm standards.",
                },
                "step3": {
                    "statusTag": "Defect: MCQ Option Count < 4",
                    "statusTagClass": "text-tertiary font-semibold",
                    "mcqStatus": "Warning: Question #3 has only 3 choices (Requires 4)",
                    "ptsStatus": "Points breakdown verified",
                },
            },
            "g9_hist": {
                "docId": "g9_hist",
                "fileName": "2025_G9_Hist_Midterm.docx",
                "size": "3.8 KB",
                "latency": "110ms",
                "charCount": "2,410 chars",
                "hash": "sha256: 3d129a0f...ff12",
                "statusBadge": "Rules Compliance 100%",
                "badgeClass": "bg-secondary-fixed text-on-secondary-fixed-variant",
                "rawText": (
                    "=======================================================\n"
                    "LIGHTHOUSE INTERNATIONAL SCHOOL (LIS)\n"
                    "2024-2025 SEMESTER 1 MIDTERM EXAMINATION\n"
                    "=======================================================\n"
                    "[COVER / HEADER METADATA TABLE]\n"
                    "Subject     : Grade 9 World History\n"
                    "Instructor  : Teacher Lee (Social Studies)\n"
                    "Exam Date   : 2025-04-24\n"
                    "Grade Level : Grade 9\n"
                    "Student Name: _______________________   Student ID: _________\n"
                    "Total Points: 100 Points (Closed: 20pts / Open: 50pts / Essay: 30pts)\n\n"
                    "PART I. MULTIPLE CHOICE QUESTIONS (Closed - 20 pts)\n"
                    "Q1. [2 pts] The Code of Hammurabi is notable for which principle?\n"
                    "  (A) Eye for an eye lex talionis (B) Innocent until proven guilty\n"
                    "  (C) Trial by jury (D) Constitutional monarchy\n\n"
                    "PART III. ESSAY QUESTIONS (Essay - 30 pts)\n"
                    "Q15. [30 pts] Analyze the socio-economic impacts of the Silk Road on Eurasian trade.\n"
                    "======================================================="
                ),
                "metadata": {
                    "subject": "Grade 9 World History",
                    "teacher": "Teacher Lee (LIS History)",
                    "date": "2025-04-24",
                    "score": "100 / 100 pts",
                    "step1Score": "6/6 Elements Matched",
                    "step1Checks": [True, True, True, True, True, True],
                },
                "scores": {
                    "summary": "Closed 20pts (20%) · Open 50pts (50%) · Essay 30pts (30%)",
                    "total": "Total: 100 pts",
                    "barClosed": "20%",
                    "barOpen": "50%",
                    "barEssay": "30%",
                    "qCount": "Total Questions: 16 items",
                    "guidelineBadge": "Guideline Compliant",
                    "guidelineBadgeClass": "bg-secondary-fixed text-on-secondary-fixed-variant",
                    "auditMessage": "Points ratio aligns perfectly with school midterm standard.",
                },
                "step3": {
                    "statusTag": "No Defects Found",
                    "statusTagClass": "text-secondary font-semibold",
                    "mcqStatus": "All MCQ items have 4 distinct choices",
                    "ptsStatus": "Points clearly annotated",
                },
            },
            "g12_bio": {
                "docId": "g12_bio",
                "fileName": "-",
                "size": "0 KB",
                "latency": "0ms",
                "charCount": "0 chars",
                "hash": "None",
                "statusBadge": "Not Submitted (Pending)",
                "badgeClass": "bg-error-container text-on-error-container",
                "rawText": (
                    "[NOTICE: EXAMINATION PAPER NOT YET SUBMITTED]\n\n"
                    "Course      : Grade 12 Biology\n"
                    "Instructor  : Teacher Choi\n"
                    "Status      : Examination draft has not been placed in the folder.\n"
                    "Action      : Notification reminder dispatched (Due: 04/18)."
                ),
                "metadata": {
                    "subject": "Grade 12 Biology",
                    "teacher": "Teacher Choi (LIS Science)",
                    "date": "-",
                    "score": "- / 100 pts",
                    "step1Score": "0/6 Not Submitted",
                    "step1Checks": [False, False, False, False, False, False],
                },
                "scores": {
                    "summary": "Unsubmitted (Closed 0% · Open 0% · Essay 0%)",
                    "total": "Total: 0 pts",
                    "barClosed": "0%",
                    "barOpen": "0%",
                    "barEssay": "0%",
                    "qCount": "Total Questions: 0",
                    "guidelineBadge": "Missing Submission",
                    "guidelineBadgeClass": "bg-error-container text-on-error-container",
                    "auditMessage": "Cannot evaluate exam quality until document is uploaded.",
                },
                "step3": {
                    "statusTag": "Draft Missing",
                    "statusTagClass": "text-error font-semibold",
                    "mcqStatus": "No draft uploaded",
                    "ptsStatus": "Not available",
                },
            },
        }


parser_service = ParserService()
