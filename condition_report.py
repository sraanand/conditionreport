#!/usr/bin/env python3
"""
Streamlit app to generate the CARS24 Handover Report PDF and provide a download button.

- Recreates the layout using ReportLab (no external templates required)
- Optional: Parse an original DOCX with Docling and export Markdown (for reference)

Run:
  streamlit run app.py
"""

from io import BytesIO
from pathlib import Path
import tempfile

import streamlit as st

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

BASE_FONT = "Helvetica"  # macOS has Helvetica by default


def _styleset():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleLarge",
            fontName=BASE_FONT,
            fontSize=18,
            leading=22,
            alignment=1,  # center
            spaceAfter=8 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeader",
            fontName=BASE_FONT,
            fontSize=12,
            leading=14,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
        )
    )
    styles.add(ParagraphStyle(name="Body", fontName=BASE_FONT, fontSize=10.5, leading=14))
    styles.add(ParagraphStyle(name="NoteSmall", fontName=BASE_FONT, fontSize=9.5, leading=13))
    return styles


def _header_fields_table(h):
    # h is a dict of values for header fields; default to empty strings
    data = [
        ["Customer Name:", h.get("customer_name", "")],
        ["Registration:", h.get("registration", "")],
        ["Odometer Reading:", h.get("odometer", "")],
        ["Sale ID:", h.get("sale_id", "")],
        ["Contract", h.get("contract", "")],
        ["Trade-in:", h.get("trade_in", "")],
        ["Bank cheque:", h.get("bank_cheque", "")],
        ["VAS:", h.get("vas", "")],
    ]
    t = Table(data, colWidths=[55 * mm, 120 * mm])
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 10.5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (1, 0), (1, -1), 0.6, colors.black),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def _checklist_table(items, col_item_width=80 * mm, rows=0):
    rows_needed = max(rows, len(items))
    data = [["Item", "OK", "Comments"]]
    for i in range(rows_needed):
        data.append([items[i] if i < len(items) else "", "", ""])
    t = Table(data, colWidths=[col_item_width, 15 * mm, 80 * mm])
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (1, 1), (1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def _labeled_line(label_left, underline_width=95 * mm):
    t = Table([[label_left, ""]], colWidths=[80 * mm, underline_width])
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 10.5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (1, 0), (1, 0), 0.6, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def _signature_block(styles):
    note = Paragraph(
        (
            "I have reviewed this document and accept the vehicle in its described condition. "
            "I also understand that should the vehicle be returned, it must be returned in the "
            "same condition it was accepted in."
        ),
        styles["NoteSmall"],
    )
    tbl = Table(
        [["Time & Date:", "", "Customer Signature:", "", "Cars24 Specialist Signature:", ""]],
        colWidths=[25 * mm, 40 * mm, 40 * mm, 47 * mm, 55 * mm, 40 * mm],
    )
    tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (1, 0), (1, 0), 0.6, colors.black),
                ("LINEBELOW", (3, 0), (3, 0), 0.6, colors.black),
                ("LINEBELOW", (5, 0), (5, 0), 0.6, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return [note, Spacer(1, 4 * mm), tbl]


def build_pdf_bytes(header_values: dict) -> bytes:
    """Build the PDF and return raw bytes for Streamlit download_button."""
    styles = _styleset()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    story = []
    story.append(Paragraph("CARS24 HANDOVER REPORT", styles["TitleLarge"]))

    # Header fields
    story.append(_header_fields_table(header_values))
    story.append(Spacer(1, 6 * mm))

    # Important Checks
    story.append(Paragraph("Important Checks", styles["SectionHeader"]))
    story.append(_checklist_table(items=[], rows=6))
    story.append(Spacer(1, 4 * mm))

    # Status lines
    for label in [
        "Customer Requests Completed",
        "Quality Control Check Passed",
        "Service Completed (if applicable)",
        "Roadworthy Check Completed",
    ]:
        story.append(_labeled_line(label))

    story.append(Spacer(1, 6 * mm))

    # Documentation
    story.append(Paragraph("Documentation", styles["SectionHeader"]))
    doc_items = [
        "Registration Papers",
        "Roadworthy Certificate",
        "Contract Signed / Invoice Received",
        "User Manual (if applicable)",
        "Service History (if available)",
        "Diagnostic Report (if applicable)",
        "Battery Test Report",
    ]
    story.append(_checklist_table(items=doc_items, rows=len(doc_items)))
    story.append(Spacer(1, 6 * mm))

    # Final Inspection
    story.append(Paragraph("Final Inspection", styles["SectionHeader"]))
    final_items = [
        "Paintwork & Panels",
        "Windscreen & Windows",
        "Tyres & Wheels",
        "Lights & Indicators",
        "Interior Trim",
        "Boot area",
        "Infotainment/Dashboard Warning Lights",
        "Keys (Count & Battery Status)",
        "Seat/Boot Mats (if applicable)",
    ]
    story.append(_checklist_table(items=final_items, rows=len(final_items)))
    story.append(Spacer(1, 8 * mm))

    # Acceptance + signatures
    story.extend(_signature_block(styles))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# ------------------------- Streamlit UI -------------------------
st.set_page_config(page_title="CARS24 Handover Report PDF", page_icon="🚗", layout="centered")
st.title("CARS24 Handover Report — PDF Generator")
st.write("Fill in the optional header fields, then click **Generate PDF** to get your file.")

# Sidebar: optional Docling parse of an uploaded DOCX
with st.sidebar:
    st.header("Optional: Docling")
    uploaded_docx = st.file_uploader("Original DOCX (for analysis)", type=["docx"], accept_multiple_files=False)
    if uploaded_docx is not None:
        parse_md = st.checkbox("Parse DOCX to Markdown with Docling")
        if parse_md:
            try:
                from docling.document_converter import DocumentConverter  # type: ignore
                # Save the uploaded file to a temporary path for Docling
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    tmp.write(uploaded_docx.getvalue())
                    tmp_path = tmp.name
                converter = DocumentConverter()
                doc = converter.convert(tmp_path).document
                md_text = doc.export_to_markdown()
                st.download_button(
                    "Download Markdown parsed by Docling",
                    md_text.encode("utf-8"),
                    file_name="handover_template.md",
                    mime="text/markdown",
                )
            except Exception as e:
                st.info(
                    "Docling is optional. If it fails to import or parse here, ensure it is listed in requirements.txt and your environment has its dependencies.\n\nError: "
                    + str(e)
                )

# Main form
with st.form("handover_form"):
    c1, c2 = st.columns(2)

    with c1:
        customer_name = st.text_input("Customer Name")
        odometer = st.text_input("Odometer Reading")
        contract = st.text_input("Contract")
        bank_cheque = st.text_input("Bank cheque")
    with c2:
        registration = st.text_input("Registration")
        sale_id = st.text_input("Sale ID")
        trade_in = st.text_input("Trade-in")
        vas = st.text_input("VAS")

    generate = st.form_submit_button("Generate PDF")

if generate:
    header_values = {
        "customer_name": customer_name,
        "registration": registration,
        "odometer": odometer,
        "sale_id": sale_id,
        "contract": contract,
        "trade_in": trade_in,
        "bank_cheque": bank_cheque,
        "vas": vas,
    }
    pdf_bytes = build_pdf_bytes(header_values)
    st.success("PDF generated. Use the button below to download it.")
    st.download_button(
        label="Download CARS24_Handover_Report.pdf",
        data=pdf_bytes,
        file_name="CARS24_Handover_Report.pdf",
        mime="application/pdf",
    )

st.caption(
    "Tip: Commit this app as `app.py` in your repo. Ensure `streamlit`, `reportlab`, and (optionally) `docling` are in `requirements.txt`."
)
