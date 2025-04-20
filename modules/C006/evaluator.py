# evaluator.py
import re
import difflib

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[\s,]+', ',', text)  # normalize spaces and commas
    text = re.sub(r'[^\w,]', '', text)   # remove special characters except commas
    return text.strip()

def score_student(student_answers, guide):
    results = []
    total = 0
    max_total = 0

    for item in guide:
        question_id = item["question"]
        expected = item["expected_answer"]
        alternatives = item.get("alternatives", [])
        max_mark = item["max_marks"]

        max_total += max_mark
        student_answer = student_answers.get(question_id, "").strip()

        if not student_answer:
            results.append({
                "question": question_id,
                "expected": expected,
                "student_answer": "No answer given",
                "score": 0,
                "awarded": 0,
                "feedback": "❌ No answer provided",
                "max_marks": max_mark
            })
            continue

        # Use difflib to measure closeness
        matches = [expected] + alternatives
        best_score = max(
            difflib.SequenceMatcher(None, student_answer.strip(), opt.strip()).ratio() * 100
            for opt in matches
        )

        # Optional exact match check for clean texts
        matched = any(clean_text(student_answer) == clean_text(opt) for opt in matches)

        if matched or best_score >= 90:
            awarded = max_mark
            feedback = "✅ Fully correct"
        elif best_score >= 60:
            awarded = round(max_mark * 0.6)
            feedback = "🟡 Partially correct — logic is mostly present"
        else:
            awarded = max(1, round(max_mark * 0.25))
            feedback = "❌ Incorrect — but attempted"

        results.append({
            "question": question_id,
            "expected": expected,
            "student_answer": student_answer,
            "score": round(best_score, 2),
            "awarded": awarded,
            "feedback": feedback,
            "max_marks": max_mark
        })

        total += awarded

    return results, round(total, 2), max_total
