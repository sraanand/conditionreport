#!/usr/bin/env python3
"""
Generate the CARS24 Handover Report as a PDF.

- Recreates your template with tables and signature lines
- Optional: export the source DOCX to Markdown using Docling for reference

Usage:
  python generate_handover_report.py --out build/CARS24_Handover_Report.pdf
  python generate_handover_report.py --source-docx Final_Delivery_Check_Sheet_No_VIN.docx --export-md build/template.md
"""

from pathlib import Path
import argparse

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

BASE_FONT = "Helvetica"  # macOS has Helvetica by default


def styleset():
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


def header_fields_table():
    data = [
        ["Customer Name:", ""],
        ["Registration:", ""],
        ["Odometer Reading:", ""],
        ["Sale ID:", ""],
        ["Contract", ""],
        ["Trade-in:", ""],
        ["Bank cheque:", ""],
        ["VAS:", ""],
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


def checklist_table(items, col_item_width=80 * mm, rows=0):
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


def labeled_line(label_left, underline_width=95 * mm):
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


def signature_block(styles):
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


def build_pdf(out_path: Path):
    styles = styleset()
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )
    story = []
    story.append(Paragraph("CARS24 HANDOVER REPORT", styles["TitleLarge"]))
    story.append(header_fields_table())
    story.append(Spacer(1, 6 * mm))

    # Important Checks
    story.append(Paragraph("Important Checks", styles["SectionHeader"]))
    story.append(checklist_table(items=[], rows=6))
    story.append(Spacer(1, 4 * mm))

    # Status lines
    for label in [
        "Customer Requests Completed",
        "Quality Control Check Passed",
        "Service Completed (if applicable)",
        "Roadworthy Check Completed",
    ]:
        story.append(labeled_line(label))

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
    story.append(checklist_table(items=doc_items, rows=len(doc_items)))
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
    story.append(checklist_table(items=final_items, rows=len(final_items)))
    story.append(Spacer(1, 8 * mm))

    # Acceptance + signatures
    story.extend(signature_block(styles))

    doc.build(story)


def export_docx_to_markdown(source_docx: Path, md_out: Path):
    """
    Optional helper that uses Docling to parse your DOCX and export its contents to Markdown.
    This is handy for diffing changes to the template over time.
    """
    from docling.document_converter import DocumentConverter  # requires `docling`

    converter = DocumentConverter()
    doc = converter.convert(str(source_docx)).document
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(doc.export_to_markdown(), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("build/CARS24_Handover_Report.pdf"))
    ap.add_argument("--source-docx", type=Path, help="Path to original DOCX to analyse with Docling (optional)")
    ap.add_argument("--export-md", type=Path, help="If set, export Markdown parsed by Docling to this path")
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(args.out)

    if args.source_docx and args.export_md:
        export_docx_to_markdown(args.source_docx, args.export_md)


if __name__ == "__main__":
    main()
