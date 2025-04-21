# app.py
import streamlit as st
import json
import os
from pdf_generator import generate_result_pdf

# Define module paths
MODULES = {
    "C003 - Computer Systems": "modules/C003",
    "C006 - Programming with Python": "modules/C006"
}

st.set_page_config(page_title="Multi-Module Exam Auto-Marker", layout="wide")
st.title("Multi-Module Exam Answer Evaluator")

# Module selection dropdown
module_label = st.selectbox("Select the module to evaluate:", list(MODULES.keys()))
selected_module_path = MODULES[module_label]

# Upload student PDF
uploaded_file = st.file_uploader("Upload the student's answer sheet (PDF):", type="pdf")

if uploaded_file:
    # Save to temporary file
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # Paths for parser, evaluator, and marking guide
    parser_path = os.path.join(selected_module_path, "pdf_parser.py")
    evaluator_path = os.path.join(selected_module_path, "evaluator.py")
    guide_path = os.path.join(selected_module_path, "marking_guide.json")

    # Load external Python files dynamically
    import importlib.util

    def load_module_from_file(module_name, filepath):
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    try:
        # Load parser and evaluator dynamically
        parser_module = load_module_from_file("pdf_parser", parser_path)
        evaluator_module = load_module_from_file("evaluator", evaluator_path)

        # Extract full text and structured answers from PDF
        full_text, student_answers = parser_module.extract_text_from_pdf("temp.pdf")

        # Load the marking scheme
        with open(guide_path, "r", encoding="utf-8") as f:
            marking_guide = json.load(f)

        # Evaluate answers
        results, total, max_total, percentage = evaluator_module.score_student(student_answers, marking_guide)

        # Generate a feedback PDF
        generate_result_pdf(full_text, results, total, max_total, output_path="student_marked_result.pdf")

        # Display success and download option
        st.success("Evaluation completed successfully.")
        st.download_button(
            "Download Marked Result",
            data=open("student_marked_result.pdf", "rb"),
            file_name="student_marked_result.pdf",
            mime="application/pdf"
        )

        # Show detailed results
        st.subheader("Evaluation Summary")
        st.markdown(f"**Total Marks:** {total} / {max_total}  **Percentage:** {percentage}%")
        for r in results:
            st.markdown(f"**Question:** {r['question']}")
            st.markdown(f"- **Answer Given:** `{r['student_answer']}`")
            st.markdown(f"- **Marks Awarded:** {r['awarded']} / {r['max_marks']}")
            st.markdown(f"- **Feedback:** {r['feedback']}")
            st.markdown("---")

    except Exception as e:
        st.error("An error occurred while processing the answer sheet.")
        st.exception(e)
