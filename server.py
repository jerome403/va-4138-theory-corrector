"""
VA Form 21-4138 Theory Corrector - local fill server.

A tiny local-only Flask app that does ONE job the browser can't do reliably:
stamp the wizard's output into the REAL `vba-21-4138-are.pdf` so the user gets
a filing-ready, sign-ready PDF.

It reuses the companion `va-form-filler`'s proven technique for VA's XFA forms
(set AcroForm values, strip /XFA, flag NeedAppearances) rather than
reimplementing PDF filling in the browser, where VA XFA forms render blank.

PII / privacy: binds to 127.0.0.1 only. Nothing is transmitted off-machine;
no telemetry, no external calls. The veteran's data never leaves this process.
"""

import io
import os
import webbrowser
from datetime import datetime
from threading import Timer

import fitz  # PyMuPDF
from flask import Flask, request, send_file, send_from_directory, jsonify

from field_mappings_4138 import FORM_21_4138

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FORMS_DIR = os.path.join(BASE_DIR, "forms")
HTML_FILE = "4138-theory-corrector.html"
PORT = 4138

app = Flask(__name__)

# Remarks rendering: normal-weight, slightly smaller than the form's default
# 10pt bold so a full legal statement fits and reads cleanly across the two
# REMARKS boxes (page 1 box + page 2 continuation).
REMARKS_FONT = "helv"
REMARKS_FONTSIZE = 9
LINE_HEIGHT = REMARKS_FONTSIZE * 1.2


@app.after_request
def allow_local(resp):
    # Permit the page to call this server even if opened from file://.
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


def _wrap(text, width_pt):
    """Word-wrap text to a pixel width at the remarks font, preserving blank
    lines and hard newlines. Returns a list of rendered lines."""
    lines = []
    for paragraph in text.split("\n"):
        if paragraph.strip() == "":
            lines.append("")
            continue
        cur = ""
        for word in paragraph.split(" "):
            trial = word if not cur else cur + " " + word
            if fitz.get_text_length(trial, REMARKS_FONT, REMARKS_FONTSIZE) <= width_pt:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                # Hard-break a single word longer than the box.
                while fitz.get_text_length(word, REMARKS_FONT, REMARKS_FONTSIZE) > width_pt and len(word) > 1:
                    cut = len(word)
                    while cut > 1 and fitz.get_text_length(word[:cut], REMARKS_FONT, REMARKS_FONTSIZE) > width_pt:
                        cut -= 1
                    lines.append(word[:cut])
                    word = word[cut:]
                cur = word
        lines.append(cur)
    return lines


def _split_remarks(text, rect0, rect1):
    """Split wrapped remarks into (page1_text, page2_text, overflow_chars).
    Wrap at the narrower box width so lines fit either box."""
    width = min(rect0.width, rect1.width) - 12
    cap0 = max(1, int((rect0.height - 8) / LINE_HEIGHT))
    cap1 = max(1, int((rect1.height - 8) / LINE_HEIGHT))
    lines = _wrap(text, width)
    page1 = lines[:cap0]
    page2 = lines[cap0:cap0 + cap1]
    leftover = lines[cap0 + cap1:]
    overflow = sum(len(l) for l in leftover)
    if overflow:
        # Don't silently drop legal text: append remainder to page 2.
        page2 = page2 + leftover
    return "\n".join(page1).strip("\n"), "\n".join(page2).strip("\n"), overflow


def _split_parts(data):
    """Derive the PDF's split sub-fields (SSN, phone, ZIP, DOB) from the
    whole-value inputs sent by the page. Mirrors va-form-filler's logic."""
    out = dict(data)

    ssn = (data.get("ssn", "") or "").replace("-", "").replace(" ", "")
    if len(ssn) >= 9:
        out["ssn_first"], out["ssn_middle"], out["ssn_last"] = ssn[:3], ssn[3:5], ssn[5:9]

    phone = "".join(c for c in (data.get("phone", "") or "") if c.isdigit())
    if len(phone) >= 10:
        out["phone_area"], out["phone_middle"], out["phone_last"] = phone[:3], phone[3:6], phone[6:10]

    zip_code = (data.get("address_zip", "") or "").replace("-", "").replace(" ", "")
    out["address_zip"] = zip_code[:5]
    out["address_zip4"] = zip_code[5:9] if len(zip_code) > 5 else ""

    # DOB accepted as YYYY-MM-DD (HTML date input) -> month/day/year.
    dob = (data.get("dob", "") or "").strip()
    if dob and "-" in dob:
        parts = dob.split("-")
        if len(parts) == 3:
            out["dob_year"], out["dob_month"], out["dob_day"] = parts[0], parts[1], parts[2]

    # The two email boxes are 20-cell comb fields, so wrap at 20 chars onto the
    # second line (EMAIL_ADDRESS[1]); together they hold up to 40 characters.
    email = (data.get("email", "") or "").strip()
    if len(email) > 20:
        out["email"], out["email_line2"] = email[:20], email[20:40]

    return out


def fill_4138(data):
    """Fill the 21-4138 PDF and return bytes."""
    form_path = os.path.join(FORMS_DIR, FORM_21_4138["form_file"])
    doc = fitz.open(form_path)
    mapping = FORM_21_4138["fields"]
    data = _split_parts(data)

    # Locate the two REMARKS widgets to measure and split the argument.
    remarks_rects = {}
    for page in doc:
        for w in page.widgets() or []:
            short = (w.field_name or "").split(".")[-1]
            if short in ("REMARKS[0]", "REMARKS[1]"):
                remarks_rects[short] = w.rect

    remarks_text = (data.get("remarks", "") or "").strip()
    page1_remarks = page2_remarks = ""
    if remarks_text and "REMARKS[0]" in remarks_rects and "REMARKS[1]" in remarks_rects:
        page1_remarks, page2_remarks, _ = _split_remarks(
            remarks_text, remarks_rects["REMARKS[0]"], remarks_rects["REMARKS[1]"]
        )

    # Build short-name -> value map.
    values = {}
    for ui_key, pdf_field in mapping.items():
        if ui_key in ("remarks", "remarks_continued"):
            continue
        v = data.get(ui_key, "")
        if v:
            values[pdf_field] = str(v)
    values[mapping["remarks"]] = page1_remarks
    values[mapping["remarks_continued"]] = page2_remarks

    # Auto-fill today's date in the signature date fields.
    today = datetime.now()
    values.setdefault(mapping["date_signed_month"], today.strftime("%m"))
    values.setdefault(mapping["date_signed_day"], today.strftime("%d"))
    values.setdefault(mapping["date_signed_year"], today.strftime("%Y"))

    remarks_fields = {mapping["remarks"], mapping["remarks_continued"]}
    for page in doc:
        for w in page.widgets() or []:
            if not w.field_name:
                continue
            short = w.field_name.split(".")[-1]
            if short not in values:
                continue
            if short in remarks_fields:
                w.text_font = REMARKS_FONT
                w.text_fontsize = REMARKS_FONTSIZE
            w.field_value = values[short]
            w.update()

    # Strip XFA + flag NeedAppearances so values render in every viewer.
    for i in range(doc.xref_length()):
        try:
            obj = doc.xref_object(i)
            if "/XFA" in obj and "/Fields" in obj:
                doc.xref_set_key(i, "XFA", "null")
                doc.xref_set_key(i, "NeedAppearances", "true")
                break
        except Exception:
            pass

    out = io.BytesIO()
    doc.save(out, garbage=4, deflate=True)
    doc.close()
    out.seek(0)
    return out.getvalue()


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, HTML_FILE)


@app.route("/api/fill", methods=["POST", "OPTIONS"])
def api_fill():
    if request.method == "OPTIONS":
        return ("", 204)
    data = request.get_json(force=True, silent=True) or {}
    try:
        pdf_bytes = fill_4138(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    last = (data.get("last_name", "") or "Veteran").strip() or "Veteran"
    first = (data.get("first_name", "") or "").strip()
    stamp = datetime.now().strftime("%Y-%m-%d")
    name = f"VA-21-4138_{last}_{first}_{stamp}.pdf".replace(" ", "-")
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=name,
    )


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "form": FORM_21_4138["form_name"]})


def _open_browser():
    webbrowser.open(f"http://127.0.0.1:{PORT}/")


if __name__ == "__main__":
    print(f"\n  VA Form 21-4138 Theory Corrector running at http://127.0.0.1:{PORT}/")
    print("  Local-only. Veteran data never leaves this machine. Ctrl+C to stop.\n")
    Timer(1.0, _open_browser).start()
    app.run(host="127.0.0.1", port=PORT, debug=False)
