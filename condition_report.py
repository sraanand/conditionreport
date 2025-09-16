#!/usr/bin/env python3
# streamlit run app.py

import datetime as dt
from io import BytesIO
from pathlib import Path

import streamlit as st

# --- Minimal PDF generator (placeholder content for now) ---
def build_pdf_bytes(delivery_date: dt.date) -> bytes:
    """
    Create a simple one-page PDF for the selected delivery date.
    Replace/extend this function later when wiring HubSpot data.
    """
    # Lazy import so app loads fast
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="H1", fontName="Helvetica-Bold", fontSize=18, leading=22))
    styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=11, leading=16))

    story = []
    story.append(Paragraph("CARS24 Condition Report", styles["H1"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(f"Delivery date: {delivery_date.isoformat()}", styles["Body"]))
    story.append(Spacer(1, 6 * mm))

    # Placeholder table for future HubSpot-driven fields
    data = [
        ["Field", "Value"],
        ["Customer Name", "—"],
        ["Registration", "—"],
        ["Odometer Reading", "—"],
        ["Sale ID", "—"],
    ]
    t = Table(data, colWidths=[50 * mm, 110 * mm])
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10.5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(t)

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Notes", styles["Body"]))
    notes = Table([["—"]], colWidths=[160 * mm])
    notes.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black), ("FONTSIZE", (0, 0), (-1, -1), 10.5)]))
    story.append(notes)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# ----------------- UI -----------------
st.set_page_config(page_title="download condition reports", page_icon="📄", layout="centered")
st.title("download condition reports")

# Row: date selector + CTA download button (side by side)
col_date, col_btn = st.columns([3, 1], gap="small")

with col_date:
    delivery_date = st.date_input("Delivery date", value=dt.date.today(), format="YYYY-MM-DD")

with col_btn:
    # Generate PDF bytes for the selected date (on the fly)
    pdf_bytes = build_pdf_bytes(delivery_date)
    file_name = f"condition_report_{delivery_date.isoformat()}.pdf"
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name=file_name,
        mime="application/pdf",
        use_container_width=True,
    )

st.caption("This is a UI scaffold. Next step: populate the PDF with live data from HubSpot deals/companies.")
