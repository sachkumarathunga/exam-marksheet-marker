import fitz  # PyMuPDF
import re

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    answers = {}
    section = "section1"
    current_question = None
    capturing_answer = False
    answer_buffer = []

    for line in lines:
        lower_line = line.lower()

        if "section 2" in lower_line:
            section = "section2"
            continue

        q_match = re.match(r"^(Q\d(?:\.\w+)*|\s*Q\d[a-d]?)", line.strip(), re.IGNORECASE)
        if q_match:
            if current_question and capturing_answer and answer_buffer:
                answers[current_question] = "\n".join(answer_buffer).strip()
                answer_buffer = []

            raw_code = q_match.group(1).strip().upper().replace(" ", "")
            parts = raw_code.split(".")

            if section == "section2":
                parts[0] = parts[0] + "_section2"
            else:
                parts[0] = parts[0] + "_section1"

            current_question = ".".join([parts[0]] + [p.lower() for p in parts[1:]])
            capturing_answer = False
            continue

        if "answer:" in lower_line:
            capturing_answer = True
            ans_part = line.split("Answer:", 1)[-1].strip()
            answer_buffer = [ans_part] if ans_part else []
            continue

        if capturing_answer and current_question:
            answer_buffer.append(line)

    if current_question and capturing_answer and answer_buffer:
        answers[current_question] = "\n".join(answer_buffer).strip()

    return text, answers
