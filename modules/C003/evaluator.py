# Updated evaluator.py with flexible marking for diploma-level students (Q3 and Q4)
import re
import difflib

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s\u2192]+', '', text)  # Allow "→" symbol
    return text.strip()

def extract_values(text):
    return re.findall(r"[A-Za-z0-9]+", text)

def normalize_expression(expr):
    expr = expr.lower().replace("b =", "").replace("=", "").replace("\u00ac", "").replace("~", "").replace("!", "")
    expr = expr.replace("or", "+").replace("not", "")
    return re.sub(r'\s+', '', expr)

def fuzzy_match(a, b):
    return difflib.SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()

def expand_compact_binary(text):
    return list("".join(re.findall(r"[01]", text)))

def normalize_truth_map(text):
    return dict(re.findall(r"(\d{4})\s*\u2192\s*([01])", text))

def score_student(student_answers, guide):
    results = []
    total = 0
    max_total = 0

    for item in guide:
        qid = item["question"]
        expected = item.get("expected", "")
        expected_list = expected.split()
        max_marks = item.get("max_marks", 0)
        keywords = item.get("expected_keywords", [])
        evaluation = item.get("evaluation", "default")

        student_answer = student_answers.get(qid, "").strip()
        max_total += max_marks

        if not student_answer:
            results.append({
                "question": qid,
                "student_answer": "No answer given",
                "awarded": 0,
                "feedback": " No answer provided",
                "max_marks": max_marks
            })
            continue

        cleaned_answer = clean_text(student_answer)
        tokens = extract_values(cleaned_answer)

        if qid.startswith("Q2a_expr"):
            norm_stud = normalize_expression(student_answer)
            norm_exp = normalize_expression(expected)
            if norm_stud == norm_exp:
                awarded = max_marks
                feedback = " Expression is correct"
            elif fuzzy_match(norm_stud, norm_exp) >= 0.8:
                awarded = round(max_marks * 0.6)
                feedback = " Partially correct expression"
            else:
                awarded = max(1, round(max_marks * 0.25))
                feedback = " Incorrect expression"

        elif qid.startswith("Q2a_tt"):
            expected_vals = list("".join(re.findall(r"[01]", expected)))
            student_vals = expand_compact_binary(student_answer)
            matched = sum(1 for i, val in enumerate(expected_vals) if i < len(student_vals) and student_vals[i] == val)
            ratio = matched / len(expected_vals) if expected_vals else 0
            if ratio == 1:
                awarded = max_marks
                feedback = " Truth table is fully correct"
            elif ratio >= 0.5:
                awarded = round(max_marks * 0.6)
                feedback = " Partially correct truth table"
            else:
                awarded = max(1, round(max_marks * 0.25))
                feedback = " Incorrect truth table"

        elif qid == "Q2b_tt":
            expected_map = normalize_truth_map(expected)
            student_map = normalize_truth_map(student_answer)
            matched = sum(1 for k in expected_map if student_map.get(k) == expected_map[k])
            ratio = matched / len(expected_map) if expected_map else 0
            if ratio == 1:
                awarded = max_marks
                feedback = " Logic map fully correct"
            elif ratio >= 0.5:
                awarded = round(max_marks * 0.6)
                feedback = " Partial logic truth table"
            else:
                awarded = max(1, round(max_marks * 0.25))
                feedback = " Incorrect logic map"

        elif qid == "Q2b_eqn":
            if normalize_expression(student_answer) == normalize_expression(expected):
                awarded = max_marks
                feedback = " Correct Boolean equation"
            else:
                awarded = round(max_marks * 0.6)
                feedback = " Partially matched Boolean equation"

        elif qid == "Q2b_circuit":
            if fuzzy_match(student_answer, expected) >= 0.8:
                awarded = max_marks
                feedback = " Circuit description accurate"
            else:
                awarded = round(max_marks * 0.6)
                feedback = " Some elements missing in circuit explanation"

        elif evaluation == "keyword_weighted":
            matched_keywords = [kw for kw in keywords if kw.lower() in cleaned_answer]
            ratio = len(matched_keywords) / len(keywords) if keywords else 0

            #  Flexibility for Diploma level: if 3+ relevant keywords present, full marks
            if ratio >= 0.8 or len(matched_keywords) >= 3:
                awarded = max_marks
                feedback = " Keywords sufficient for diploma level"
            elif ratio >= 0.5:
                awarded = round(max_marks * 0.6)
                feedback = " Partial keyword match"
            else:
                awarded = round(max_marks * 0.4)
                feedback = " Few relevant terms present"

        else:
            correct = sum(1 for val in expected_list if val.lower() in tokens)
            ratio = correct / len(expected_list) if expected_list else 0
            if ratio == 1:
                awarded = max_marks
                feedback = " Fully correct"
            elif ratio >= 0.5:
                awarded = round(max_marks * 0.6)
                feedback = " Partially correct"
            else:
                awarded = round(max_marks * 0.4)
                feedback = " Mostly incorrect"

        results.append({
            "question": qid,
            "student_answer": student_answer,
            "awarded": awarded,
            "feedback": feedback,
            "max_marks": max_marks
        })

        total += awarded

    final_score = round((total / max_total) * 100, 2) if max_total else 0
    return results, round(total, 2), max_total, final_score
