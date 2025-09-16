#!/usr/bin/env python3
"""
Streamlit app to produce a PDF that is pixel-perfect to the uploaded DOCX.

How it works (exactness-first pipeline):
1) Try docx2pdf (uses Microsoft Word for Mac) for 1:1 conversion.
2) If not available, fall back to LibreOffice headless (soffice).
3) Return the PDF via a Streamlit download button.

macOS tips:
- Best fidelity: Microsoft Word installed (docx2pdf will use it automatically).
- Fallback: brew install --cask libreoffice  (soffice path is auto-detected).
- Exactness also depends on fonts installed on your machine matching the DOCX.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import streamlit as st


# ------------------------- Helpers -------------------------

def _convert_with_docx2pdf(in_path, out_path):
    """Convert with docx2pdf (MS Word). Returns (ok: bool, err: str|None)."""
    try:
        from docx2pdf import convert  # type: ignore
    except Exception as e:
        return False, f"docx2pdf import failed: {e}"

    try:
        out_dir = str(Path(out_path).parent)
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        # docx2pdf writes <stem>.pdf into output dir
        convert(in_path, out_dir)
        produced = str(Path(out_dir) / (Path(in_path).stem + ".pdf"))
        if produced != out_path and Path(produced).exists():
            shutil.move(produced, out_path)
        return Path(out_path).exists(), None
    except Exception as e:
        return False, f"docx2pdf conversion error: {e}"


def _find_soffice():
    """Best-effort locate LibreOffice 'soffice' on macOS."""
    # 1) PATH
    exe = shutil.which("soffice")
    if exe:
        return exe
    # 2) Common macOS locations
    candidates = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/local/bin/soffice",
        "/opt/homebrew/bin/soffice",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def _convert_with_libreoffice(in_path, out_path):
    """Convert with LibreOffice headless. Returns (ok: bool, err: str|None)."""
    soffice = _find_soffice()
    if not soffice:
        return False, (
            "LibreOffice 'soffice' not found. Install via Homebrew: "
            "`brew install --cask libreoffice` (restart your terminal afterwards)."
        )

    try:
        out_dir = str(Path(out_path).parent)
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        cmd = [
            soffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            out_dir,
            in_path,
        ]
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


def docx_to_pdf_bytes(docx_bytes, file_name_hint="document"):
    """
    Persist uploaded DOCX to a temp file, convert to PDF via best available engine,
    and return (pdf_bytes: bytes|None, error: str|None).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = str(Path(tmpdir) / (Path(file_name_hint).stem + ".docx"))
        out_path = str(Path(tmpdir) / (Path(file_name_hint).stem + ".pdf"))
        with open(in_path, "wb") as f:
            f.write(docx_bytes)

        # 1) Try Word (docx2pdf)
        ok, err = _convert_with_docx2pdf(in_path, out_path)
        if not ok:
            # 2) Fallback to LibreOffice
            ok, err2 = _convert_with_libreoffice(in_path, out_path)
            if not ok:
                combined = " | ".join([e for e in [err, err2] if e]) or "unknown error"
                return None, combined

        with open(out_path, "rb") as f:
            return f.read(), None


# ------------------------- Streamlit UI -------------------------

st.set_page_config(page_title="CARS24 DOCX → PDF (Exact)", page_icon="📄", layout="centered")
st.title("CARS24 — Exact DOCX to PDF Converter")

st.write(
    "Upload your original **.docx**. The app will render it to PDF using Microsoft Word (if available) "
    "or LibreOffice headless. This preserves layout 1:1 for an exact visual match."
)

uploaded = st.file_uploader("Choose a DOCX file", type=["docx"], accept_multiple_files=False)

colA, colB = st.columns([1, 1])
with colA:
    use_repo_template = st.checkbox("Use repo template (template.docx)")
with colB:
    desired_name = st.text_input("Output name (optional)", value="CARS24_Handover_Report")

convert_clicked = st.button("Convert to PDF")

# Optional Docling inspector (not used for rendering, purely informational)
with st.expander("Optional: Inspect the DOCX structure with Docling"):
    st.caption("Docling is not used for rendering; it is only for inspecting content.")
    try:
        from docling.document_converter import DocumentConverter  # type: ignore
        enable_docling = st.checkbox("Extract Markdown with Docling")
        if enable_docling and (uploaded or use_repo_template):
            if uploaded:
                src_bytes = uploaded.getvalue()
                hint = uploaded.name
            else:
                template_path = Path("template.docx")
                if not template_path.exists():
                    st.warning("template.docx not found in repo.")
                    src_bytes = None
                    hint = "template"
                else:
                    src_bytes = template_path.read_bytes()
                    hint = template_path.name
            if src_bytes:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    tmp.write(src_bytes)
                    tmp_path = tmp.name
                doc = DocumentConverter().convert(tmp_path).document
                md_text = doc.export_to_markdown()
                st.download_button(
                    "Download Markdown (Docling)",
                    md_text.encode("utf-8"),
                    file_name=f"{Path(hint).stem}.md",
                )
    except Exception as e:
        st.info(f"Docling not available or failed to import: {e}")

if convert_clicked:
    source_bytes = None
    name_hint = (desired_name or "document").strip() or "document"

    if uploaded is not None:
        source_bytes = uploaded.getvalue()
        name_hint = Path(uploaded.name).stem or name_hint
    elif use_repo_template:
        template_path = Path("template.docx")
        if template_path.exists():
            source_bytes = template_path.read_bytes()
            name_hint = template_path.stem
        else:
            st.error("You selected repo template, but template.docx was not found next to app.py")

    if not source_bytes:
        st.warning("Please upload a DOCX or select the repo template.")
    else:
        with st.spinner("Converting…"):
            pdf_bytes, err = docx_to_pdf_bytes(source_bytes, file_name_hint=name_hint)
        if err:
            st.error(
                "Conversion failed. "
                + err
                + "\n\nHints: On macOS, ensure Microsoft Word is installed for docx2pdf, "
                  "or install LibreOffice: `brew install --cask libreoffice`."
            )
        else:
            st.success("Done. Your PDF is ready.")
            st.download_button(
                label=f"Download {name_hint}.pdf",
                data=pdf_bytes,
                file_name=f"{name_hint}.pdf",
                mime="application/pdf",
            )

st.caption("Exactness depends on rendering with the same layout engine and fonts used when the DOCX was authored.")
