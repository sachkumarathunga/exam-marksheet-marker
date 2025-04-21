from fpdf import FPDF

def clean_unicode(text):
    try:
        return text.encode('latin-1', 'replace').decode('latin-1')
    except Exception:
        return text.encode('ascii', 'replace').decode('ascii')

def generate_result_pdf(student_text, results, total, max_total, output_path="student_marked_result.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ✅ Final score scaled to 100
    scaled_score = round((total / max_total) * 100, 2) if max_total else 0

    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(255, 0, 0)  # Red
    pdf.cell(200, 10, txt=f"Final Marks: {scaled_score}/100", ln=True, align='C')

    # Reset text color
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    # 📝 Evaluation Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Evaluation Summary", ln=True)
    pdf.set_font("Arial", size=11)

    for res in results:
        feedback_text = (
            f"\nQuestion: {res['question']}\n"
            f"Answer Given: {res['student_answer']}\n"
            f"Marks Awarded: {res['awarded']} / {res['max_marks']}\n"
            f"Feedback: {res['feedback']}\n"
            "---------------------------------------------\n"
        )
        pdf.multi_cell(0, 10, clean_unicode(feedback_text))

    pdf.output(output_path)
