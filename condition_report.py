# app.py
import io
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import streamlit as st


def add_spacer(paragraph, lines=1):
    # A small helper to add blank lines for visual spacing
    for _ in range(lines):
        paragraph.add_run("\n")


def add_heading(doc, text, lvl=0):
    h = doc.add_paragraph()
    run = h.add_run(text)
    run.bold = True
    run.font.size = Pt(16 if lvl == 0 else 13)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER if lvl == 0 else WD_ALIGN_PARAGRAPH.LEFT
    return h


def add_label_grid(doc, rows):
    """
    Create a 2-column grid for short labels like Customer Name, Registration, etc.
    rows: list of tuples: [(left_label, right_label), ...]
    Empty strings are fine for spacing.
    """
    table = doc.add_table(rows=len(rows), cols=4)
    table.autofit = True
    for r, (l1, l2) in enumerate(rows):
        table.cell(r, 0).text = l1
        table.cell(r, 1).text = ""
        table.cell(r, 2).text = l2
        table.cell(r, 3).text = ""
    return table


def add_section_table(doc, title, items):
    add_heading(doc, f"  {title}  ", lvl=1)
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Item"
    hdr_cells[1].text = "OK"
    hdr_cells[2].text = "Comments"
    for it in items:
        row_cells = table.add_row().cells
        row_cells[0].text = it
        row_cells[1].text = ""
        row_cells[2].text = ""
    add_spacer(doc.add_paragraph())
    return table


def build_delivery_check_sheet() -> bytes:
    doc = Document()

    # Title
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("CARS24 CONDITION REPORT")
    title_run.bold = True
    title_run.font.size = Pt(18)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_spacer(doc.add_paragraph())

    # Top labels
    add_label_grid(
        doc,
        rows=[
            ("Customer Name:", "Registration:"),
            ("Odometer Reading:", "Sale ID:"),
        ],
    )

    add_spacer(doc.add_paragraph(), lines=1)

    # Sections (matched to your template)
    add_section_table(
        doc,
        "Important Checks",
        [
            "Customer Requests Completed",
            "Quality Control Check Passed",
            "Service Completed (if applicable)",
            "Roadworthy Check Completed",
        ],
    )

    add_section_table(
        doc,
        "Documentation",
        [
            "Registration Papers",
            "Roadworthy Certificate",
            "Contract Signed / Invoice Received",
            "User Manual (if applicable)",
            "Service History (if available)",
            "Diagnostic Report (if applicable)",
            "Battery Test Report",
        ],
    )

    add_section_table(
        doc,
        "Final Inspection",
        [
            "Paintwork & Panels",
            "Windscreen & Windows",
            "Tyres & Wheels",
            "Lights & Indicators",
            "Interior Trim",
            "Boot area",
            "Infotainment/Dashboard Warning Lights",
            "Keys (Count & Battery Status)",
            "Seat/Boot Mats (if applicable)",
        ],
    )

    # Acceptance statement
    p = doc.add_paragraph()
    p_run = p.add_run(
        "I have reviewed this document and accept the vehicle in its described condition. "
        "I also understand that should the vehicle be returned, it must be returned in the same "
        "condition it was accepted in."
    )
    p_run.font.size = Pt(11)
    add_spacer(doc.add_paragraph())

    # Signature row
    sig_table = doc.add_table(rows=1, cols=3)
    sig_cells = sig_table.rows[0].cells
    sig_cells[0].text = "Time & Date:"
    sig_cells[1].text = "Customer Signature:"
    sig_cells[2].text = "Cars24 Specialist Signature:"

    # Save to bytes
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


st.set_page_config(page_title="CARS24 Final Delivery Check Sheet", page_icon="🚗", layout="centered")
st.title("CARS24 Final Delivery Check Sheet")
st.caption("Generates a .docx matching your delivery check template")

st.write(
    "Click the button below to generate a blank **Final Delivery Check Sheet** as a Word document "
    "that mirrors the sections and wording of your template."
)

if "docx_bytes" not in st.session_state:
    st.session_state.docx_bytes = build_delivery_check_sheet()

# Optional: re-generate (if you later add form controls)
if st.button("Rebuild Document"):
    st.session_state.docx_bytes = build_delivery_check_sheet()
    st.success("Document rebuilt!")

st.download_button(
    label="⬇️ Download Final Delivery Check Sheet (.docx)",
    data=st.session_state.docx_bytes,
    file_name=f"Final_Delivery_Check_Sheet_{datetime.now().strftime('%Y-%m-%d')}.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)
