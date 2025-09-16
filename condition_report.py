#!/usr/bin/env python3
"""
Streamlit app: exact DOCX → PDF conversion with small fixes
- Fix 1: Widen the 'OK' column so 'OK' stays on one line.
- Fix 2: Trim a trailing blank page from the output PDF.

Pipeline:
1) (Optional) Pre-fix the uploaded DOCX with python-docx (only the specific table).
2) Convert DOCX → PDF using Microsoft Word (docx2pdf) or LibreOffice headless.
3) Trim blank last page from the PDF with pypdf.

Notes:
- For EXACT rendering, fonts used by the DOCX must be installed.
- On Linux, install LibreOffice (soffice) and fonts; on macOS, having Word enables docx2pdf.
"""

from __future__ import annotations
import shutil
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

import streamlit as st

# ---------- Optional: DOCX fixes (OK column width, etc.) ----------
def _set_table_fixed_layout(table):
    """Force table to fixed layout so widths are honored."""
    try:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
    except Exception:
        return
    tbl = table._tbl
    tblPr = tbl.tblPr
    # Ensure <w:tblLayout w:type="fixed"/>
    has_layout = tblPr.xpath("./w:tblLayout")
    if not has_layout:
        el = OxmlElement("w:tblLayout")
        el.set(qn("w:type"), "fixed")
        tblPr.append(el)
    # Disable autofit if available
    try:
        table.allow_autofit = False
    except Exception:
        pass


def _set_ok_column_width(table, ok_mm: float = 20.0, item_mm: float = 110.0, comments_mm: float = 80.0):
    """Set column widths for Item | OK | Comments (in millimetres)."""
    from docx.shared import Mm

    # Ensure fixed layout
    _set_table_fixed_layout(table)

    widths = [Mm(item_mm), Mm(ok_mm), Mm(comments_mm)]
    for row in table.rows:
        for i, w in enumerate(widths):
            # Set width on every cell in the column
            try:
                row.cells[i].width = w
            except Exception:
                pass


def fix_docx_layout(docx_bytes: bytes) -> bytes:
    """
    Open DOCX, find the table with header ['Item', 'OK', 'Comments'] (case-insensitive),
    widen the OK column so 'OK' does not wrap, then return the modified DOCX bytes.
    """
    try:
        from docx import Document
    except Exception:
        # If python-docx is not available, just return original bytes.
        return docx_bytes

    f = BytesIO(docx_bytes)
    doc = Document(f)

    def norm(s: str) -> str:
        return (s or "").strip().lower()

    # Find and fix the first matching table
    for table in doc.tables:
        if not table.rows:
            continue
        hdr = [norm(c.text) for c in table.rows[0].cells]
        if len(hdr) >= 3 and hdr[0].startswith("item") and hdr[1] == "ok" and hdr[2].startswith("comments"):
            # Adjust widths; tweak numbers as needed
            _set_ok_column_width(table, ok_mm=20.0, item_mm=110.0, comments_mm=80.0)
            break

    out = BytesIO()
    doc.save(out)
    return out.getvalue()


# ---------- DOCX → PDF conversion ----------
def _convert_with_docx2pdf(in_path: str, out_path: str) -> Tuple[bool, Optional[str]]:
    """Use Microsoft Word via docx2pdf (macOS/Windows only)."""
    if sys.platform not in ("darwin", "win32"):
        return False, "docx2pdf requires Microsoft Word (macOS/Windows). Skipping on non-supported platform."
    try:
        from docx2pdf import convert  # type: ignore
    except Exception as e:
        return False, f"docx2pdf import failed: {e}"

    try:
        out_dir = str(Path(out_path).parent)
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        convert(in_path, out_dir)  # produces <stem>.pdf in out_dir
        produced = str(Path(out_dir) / (Path(in_path).stem + ".pdf"))
        if produced != out_path and Path(produced).exists():
            shutil.move(produced, out_path)
        return Path(out_path).exists(), None
    except Exception as e:
        return False, f"docx2pdf conversion error: {e}"


def _find_soffice() -> Optional[str]:
    """Locate LibreOffice 'soffice' / 'lowriter'."""
    for name in ("soffice", "lowriter"):
        p = shutil.which(name)
        if p:
            return p
    for p in (
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
        "/opt/homebrew/bin/soffice",
        "/snap/bin/libreoffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ):
        if Path(p).exists():
            return p
    return None


def _convert_with_libreoffice(in_path: str, out_path: str) -> Tuple[bool, Optional[str]]:
    """Use LibreOffice headless to convert DOCX → PDF."""
    soffice = _find_soffice()
    if not soffice:
        return False, "LibreOffice 'soffice' not found. On Linux: apt install libreoffice. On macOS: brew install --cask libreoffice."
    try:
        out_dir = str(Path(out_path).parent)
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        cmd = [soffice, "--headless", "--convert-to", "pdf", "--outdir", out_dir, in_path]
        proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            err = proc.stderr.decode(errors="ignore") or proc.stdout.decode(errors="ignore")
            return False, f"LibreOffice conversion failed: {err.strip()}"
        produced = str(Path(out_dir) / (Path(in_path).stem + ".pdf"))
        if produced != out_path and Path(produced).exists():
            shutil.move(produced, out_path)
        return Path(out_path).exists(), None
    except Exception as e:
        return False, f"LibreOffice conversion error: {e}"


def docx_to_pdf_bytes(docx_bytes: bytes, file_name_hint: str = "document") -> Tuple[Optional[bytes], Optional[str]]:
    """Convert DOCX bytes to PDF bytes using the best available engine."""
    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = str(Path(tmpdir) / (Path(file_name_hint).stem + ".docx"))
        out_path = str(Path(tmpdir) / (Path(file_name_hint).stem + ".pdf"))
        with open(in_path, "wb") as f:
            f.write(docx_bytes)

        ok, err = _convert_with_docx2pdf(in_path, out_path)
        if not ok:
            ok, err2 = _convert_with_libreoffice(in_path, out_path)
            if not ok:
                return None, " | ".join([e for e in (err, err2) if e]) or "unknown conversion error"

        with open(out_path, "rb") as f:
            return f.read(), None


# ---------- PDF post-processing (trim trailing blank page) ----------
def trim_trailing_blank_page(pdf_bytes: bytes, force_single_page: bool = False) -> bytes:
    """
    Remove the last page if it is blank. Optionally force single page (keep only page 1).
    """
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(BytesIO(pdf_bytes))
    if force_single_page and len(reader.pages) > 1:
        writer = PdfWriter()
        writer.add_page(reader.pages[0])
        out = BytesIO()
        writer.write(out)
        return out.getvalue()

    n = len(reader.pages)
    if n <= 1:
        return pdf_bytes

    # Heuristic: if last page has no extractable text and empty content stream → blank.
    last = reader.pages[-1]
    is_blank = True
    try:
        text = (last.extract_text() or "").strip()
        if text:
            is_blank = False
    except Exception:
        pass
    if is_blank:
        try:
            contents = last.get_contents()
            if contents is None:
                is_blank = True
            else:
                if isinstance(contents, list):
                    data = b"".join([c.get_data() for c in contents])
                else:
                    data = contents.get_data()
                if data and data.strip():
                    is_blank = False
        except Exception:
            # If unsure, do not drop the page.
            is_blank = False

    if not is_blank:
        return pdf_bytes

    writer = PdfWriter()
    for i in range(n - 1):
        writer.add_page(reader.pages[i])
    out = BytesIO()
    writer.write(out)
    return out.getvalue()


# ---------- Streamlit UI ----------
st.set_page_config(page_title="CARS24 DOCX → PDF (Exact, with fixes)", page_icon="📄", layout="centered")
st.title("CARS24 — Exact DOCX to PDF (with OK-column & blank-page fixes)")

uploaded = st.file_uploader("Upload the original .docx", type=["docx"], accept_multiple_files=False)

col1, col2 = st.columns([1, 1])
with col1:
    apply_ok_fix = st.checkbox("Widen 'OK' column", value=True)
with col2:
    trim_blank = st.checkbox("Trim blank last page", value=True)

force_single = st.checkbox("Force single page (keep only page 1)", value=False, help="Use only if you always want a one-page PDF.")
desired_name = st.text_input("Output name", value="CARS24_Handover_Report")

if st.button("Convert to PDF"):
    if not uploaded:
        st.warning("Please upload a DOCX.")
    else:
        src = uploaded.getvalue()

        # Pre-fix DOCX (only adjusts the specific table)
        if apply_ok_fix:
            try:
                src = fix_docx_layout(src)
            except Exception as e:
                st.info(f"Could not adjust OK column automatically: {e}")

        with st.spinner("Converting…"):
            pdf_bytes, err = docx_to_pdf_bytes(src, file_name_hint=Path(uploaded.name).stem or "document")

        if err:
            st.error(
                "Conversion failed: "
                + err
                + "\n\nLinux: install LibreOffice (e.g., `sudo apt-get install -y libreoffice`). "
                  "macOS: install Microsoft Word (for docx2pdf) or `brew install --cask libreoffice`."
            )
        else:
            # Trim trailing blank page (or force single)
            try:
                if force_single:
                    pdf_bytes = trim_trailing_blank_page(pdf_bytes, force_single_page=True)
                elif trim_blank:
                    pdf_bytes = trim_trailing_blank_page(pdf_bytes, force_single_page=False)
            except Exception as e:
                st.info(f"Could not post-process PDF pages: {e}")

            st.success("Done. Your PDF is ready.")
            st.download_button(
                label=f"Download {desired_name or 'document'}.pdf",
                data=pdf_bytes,
                file_name=f"{(desired_name or 'document').strip()}.pdf",
                mime="application/pdf",
            )

st.caption(
    "Fidelity comes from using the original DOCX renderer (Word/LibreOffice). "
    "This app only nudges the 'OK' column width and removes an extra blank page."
)
