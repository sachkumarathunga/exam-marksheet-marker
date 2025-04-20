import re
import difflib

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def extract_values(text):
    return re.findall(r"[A-Za-z0-9]+", text)

def normalize_expression(expr):
    expr = expr.lower().replace("b =", "").replace("=", "").replace("¬", "").replace("~", "").replace("!", "")
    expr = expr.replace("or", "+").replace("not", "")
    return re.sub(r'\s+', '', expr)

def fuzzy_match(a, b):
    return difflib.SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()

def score_student(student_answers, guide):
    results = []
    total = 0
    max_total = 0

    for item in guide:
        qid = item["question"]
        expected = item.get("expected", "")
        expected_list = expected.split()
        max_marks = item.get("max_marks", 0)
        alternatives = item.get("alternatives", [])
        keywords = item.get("expected_keywords", [])
        evaluation = item.get("evaluation", "default")

        student_answer = student_answers.get(qid, "").strip()
        max_total += max_marks

        if not student_answer:
            results.append({
                "question": qid,
                "student_answer": "No answer given",
                "awarded": 0,
                "feedback": "❌ No answer provided",
                "max_marks": max_marks
            })
            continue

        cleaned_answer = clean_text(student_answer)
        tokens = extract_values(cleaned_answer)

        # ✅ Q2a: Logic Table for AND & OR
        if qid == "Q2a":
            and_match = re.search(r'and[:\s]*([01]{4})', student_answer.lower())
            or_match = re.search(r'or[:\s]*([01]{4})', student_answer.lower())
            if and_match and or_match:
                if and_match.group(1) == "0001" and or_match.group(1) == "0111":
                    awarded = max_marks
                    feedback = "✅ Fully correct"
                else:
                    awarded = round(max_marks * 0.6)
                    feedback = "🟡 Partial mismatch in logic outputs"
            else:
                awarded = max(1, round(max_marks * 0.25))
                feedback = "❌ Logic outputs incorrect"

        # ✅ Q2bi: NOT Gate Answer Handling
        elif qid == "Q2bi":
            patterns = {
                "1": "0",
                "0": "1"
            }
            all_correct = True
            for inp, expected_out in patterns.items():
                match = re.search(rf"input\s*{inp}[:\s]*{expected_out}", student_answer.lower())
                if not match:
                    all_correct = False
                    break
            if all_correct:
                awarded = max_marks
                feedback = "✅ Fully correct"
            else:
                awarded = max(1, round(max_marks * 0.25))
                feedback = "❌ Incorrect NOT gate outputs"

        # ✅ Q2biii: Boolean Logic Expression
        elif qid == "Q2biii":
            normalized_student = normalize_expression(student_answer)
            normalized_expected = normalize_expression(expected)
            normalized_alternatives = [normalize_expression(a) for a in alternatives]

            if normalized_student == normalized_expected or normalized_student in normalized_alternatives:
                awarded = max_marks
                feedback = "✅ Fully correct"
            else:
                best_score = max(fuzzy_match(normalized_student, a) for a in [normalized_expected] + normalized_alternatives)
                if best_score >= 0.9:
                    awarded = max_marks
                    feedback = "✅ Close match"
                elif best_score >= 0.6:
                    awarded = round(max_marks * 0.6)
                    feedback = "🟡 Partially correct"
                else:
                    awarded = max(1, round(max_marks * 0.25))
                    feedback = "❌ Incorrect logic"

        # ✅ Keyword-Based Evaluation (e.g., Q3a, Q3b)
        elif evaluation == "keyword_weighted":
            matched_keywords = [kw for kw in keywords if kw.lower() in cleaned_answer]
            ratio = len(matched_keywords) / len(keywords) if keywords else 0
            if ratio >= 0.8:
                awarded = max_marks
                feedback = "✅ Most keywords matched"
            elif ratio >= 0.5:
                awarded = round(max_marks * 0.6)
                feedback = "🟡 Partial keyword match"
            else:
                awarded = max(1, round(max_marks * 0.25))
                feedback = "❌ Keywords insufficient"

        # ✅ Default: Token match for conversion-based answers
        else:
            correct = sum(1 for val in expected_list if val.lower() in tokens)
            ratio = correct / len(expected_list) if expected_list else 0
            if ratio == 1:
                awarded = max_marks
                feedback = "✅ Fully correct"
            elif ratio >= 0.5:
                awarded = round(max_marks * 0.6)
                feedback = "🟡 Partially correct"
            else:
                awarded = max(1, round(max_marks * 0.25))
                feedback = "❌ Mostly incorrect"

        results.append({
            "question": qid,
            "student_answer": student_answer,
            "awarded": awarded,
            "feedback": feedback,
            "max_marks": max_marks
        })
        total += awarded

    return results, round(total, 2), max_total
