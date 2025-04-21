import fitz  # PyMuPDF
import re

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    answers = {}
    current_question = None
    answer_buffer = []
    capture = False

    for line in lines:
        # Detect question label like Q2a_expr1, Q3a, etc.
        match = re.match(r"^(Q\d+[a-zA-Z0-9_]*)\)?", line.strip(), re.IGNORECASE)
        if match:
            if current_question and answer_buffer:
                answers[current_question] = "\n".join(answer_buffer).strip()
                answer_buffer = []
            current_question = match.group(1).strip()
            capture = False
            continue

        # Start capturing if "Answer:" line appears
        if "answer:" in line.lower():
            capture = True
            ans_part = line.split("Answer:", 1)[-1].strip()
            if ans_part:
                answer_buffer.append(ans_part)
            continue

        if capture and current_question:
            answer_buffer.append(line.strip())

    if current_question and answer_buffer:
        answers[current_question] = "\n".join(answer_buffer).strip()

    return text, answers
