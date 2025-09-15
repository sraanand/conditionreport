# generate_doc.py
import io
from datetime import datetime
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_spacer(paragraph, lines=1):
    for _ in range(lines):
        paragraph.add_run("\n")

def add_label_grid(doc, rows):
    table = doc.add_table(rows=len(rows), cols=4)
    table.autofit = True
    for r, (l1, l2) in enumerate(rows):
        table.cell(r, 0).text = l1
        table.cell(r, 1).text = ""
        table.cell(r, 2).text = l2
        table.cell(r, 3).text = ""
    return table

def add_section_table(doc, title, items):
    h = doc.add_paragraph()
    run = h.add_run(f"  {title}  ")
    run.bold = True
    run.font.size = Pt(13)
    table = doc.add_table(rows=1, cols=3)
    hdr = table.rows[0].cells
    hdr[0].text = "Item"
    hdr[1].text = "OK"
    hdr[2].text = "Comments"
    for it in items:
        row = table.add_row().cells
        row[0].text = it
        row[1].text = ""
        row[2].text = ""
    add_spacer(doc.add_paragraph())

def build_delivery_check_sheet():
    doc = Document()
    title_p = doc.add_paragraph()
    t = title_p.add_run("CARS24 CONDITION REPORT")
    t.bold = True
    t.font.size = Pt(18)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_spacer(doc.add_paragraph())

    add_label_grid(doc, [
        ("Customer Name:", "Registration:"),
        ("Odometer Reading:", "Sale ID:"),
    ])
    add_spacer(doc.add_paragraph())

    add_section_table(doc, "Important Checks", [
        "Customer Requests Completed",
        "Quality Control Check Passed",
        "Service Completed (if applicable)",
        "Roadworthy Check Completed",
    ])
    add_section_table(doc, "Documentation", [
        "Registration Papers",
        "Roadworthy Certificate",
        "Contract Signed / Invoice Received",
        "User Manual (if applicable)",
        "Service History (if available)",
        "Diagnostic Report (if applicable)",
        "Battery Test Report",
    ])
    add_section_table(doc, "Final Inspection", [
        "Paintwork & Panels",
        "Windscreen & Windows",
        "Tyres & Wheels",
        "Lights & Indicators",
        "Interior Trim",
        "Boot area",
        "Infotainment/Dashboard Warning Lights",
        "Keys (Count & Battery Status)",
        "Seat/Boot Mats (if applicable)",
    ])

    p = doc.add_paragraph()
    p.add_run(
        "I have reviewed this document and accept the vehicle in its described condition. "
        "I also understand that should the vehicle be returned, it must be returned in the same "
        "condition it was accepted in."
    ).font.size = Pt(11)

    sig = doc.add_table(rows=1, cols=3).rows[0].cells
    sig[0].text = "Time & Date:"
    sig[1].text = "Customer Signature:"
    sig[2].text = "Cars24 Specialist Signature:"
    return doc

if __name__ == "__main__":
    doc = build_delivery_check_sheet()
    out_name = f"_
