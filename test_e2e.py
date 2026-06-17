"""
End-to-end smoke test for the VA Form 21-4138 Theory Corrector.

Drives the real tool in a headless browser with a SYNTHETIC veteran
(never a real client), exercising: identity entry + auto-format, the
client Template save/load, TERA auto-detection, question generation, and
the filled-PDF download — then verifies the resulting AcroFields.

Run:  python -m playwright install chromium   (first time only)
      python test_e2e.py

Requires: flask, PyMuPDF, playwright  (pip install -r requirements.txt playwright)
PII rule: uses only fake data (file number 000 00 0000, 123 Test St). Never
point this at a real client file.
"""
import os
import sys
import time
import tempfile
import subprocess
import urllib.request

import fitz
from playwright.sync_api import sync_playwright

REPO = os.path.dirname(os.path.abspath(__file__))
BASE = "http://127.0.0.1:4138"
OUT = os.path.join(tempfile.gettempdir(), "e2e_4138.pdf")
SHOT = os.path.join(tempfile.gettempdir(), "e2e_4138_page.png")


def wait_health(timeout=25):
    for _ in range(timeout * 2):
        try:
            with urllib.request.urlopen(BASE + "/api/health", timeout=1) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def run():
    srv = subprocess.Popen([sys.executable, "server.py"], cwd=REPO,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        assert wait_health(), "server did not start"
        print("server up")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(accept_downloads=True)
            page = ctx.new_page()
            page.on("dialog", lambda d: d.accept("Test, Veteran") if d.type == "prompt" else d.accept())
            page.goto(BASE + "/", wait_until="networkidle")

            # --- Section 1: identity ---
            page.fill("#firstName", "Test")
            page.fill("#middleInitial", "V")
            page.fill("#lastName", "Veteran")
            page.fill("#ssn", "000000000")          # auto-formats to 000-00-0000
            page.fill("#fileNumber", "999888777")
            page.fill("#dob", "1980-05-15")
            page.fill("#phone", "5551234567")       # auto-formats
            page.fill("#email", "test.veteran@example.com")
            page.fill("#addressStreet", "123 Test St")
            page.fill("#addressCity", "Anytown")
            page.fill("#addressState", "WA")
            page.fill("#addressZip", "00000")
            page.fill("#repName", "Test Rep")
            page.select_option("#repCapacity", "accredited agent")
            page.select_option("#formType", "526EZ")
            assert page.input_value("#ssn") == "000-00-0000"
            assert page.input_value("#phone") == "(555) 123-4567"

            # --- Template save/load ---
            page.click("text=Save as Template")
            page.wait_for_timeout(300)
            opts = page.eval_on_selector_all("#templateSelect option", "els => els.map(e => e.value)")
            assert "Test, Veteran" in opts, "template not saved"
            page.fill("#firstName", "WIPED")
            page.select_option("#templateSelect", "Test, Veteran")
            page.wait_for_timeout(300)
            assert page.input_value("#firstName") == "Test", "template did not restore field"
            print("template save/load OK")

            # --- Section 2: condition + theory ---
            page.click("text=Continue to Condition")
            page.fill("#conditionLabel", "sleep apnea")
            page.select_option("#intendedTheory", "Secondary Connection - Caused By (38 C.F.R. § 3.310(a))")
            page.wait_for_timeout(200)
            page.fill("#serviceConnectedCondition", "PTSD")

            # --- Section 3: VSR request (TERA detection) ---
            page.click("text=Continue to VSR Request")
            page.fill("#examQuestionText",
                      "Is the veteran's condition related to toxic exposure (TERA) including burn pit exposure during service?")
            page.wait_for_timeout(300)
            assert page.input_value("#requestedTheory") == "TERA Toxic Exposure"
            print("TERA auto-detection OK")

            # --- Section 4: evidence ---
            page.click("text=Continue to Evidence")
            page.fill("#priorExamFindings",
                      "November 2023 C&P exam diagnosed obstructive sleep apnea with a positive nexus to service-connected PTSD.")

            # --- Section 5: generate PDF ---
            page.click("text=Continue to Questions")
            page.wait_for_timeout(300)
            assert page.input_value("#questionA"), "questions not generated"

            with page.expect_download() as dl_info:
                page.click("text=Generate Filled 4138 PDF")
            dl_info.value.save_as(OUT)
            print("downloaded:", dl_info.value.suggested_filename)
            page.screenshot(path=SHOT, full_page=True)
            browser.close()
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=5)
        except Exception:
            srv.kill()

    # --- Verify the downloaded PDF ---
    doc = fitz.open(OUT)
    vals = {}
    for pg in doc:
        for w in pg.widgets() or []:
            if w.field_value:
                vals[(w.field_name or "").split(".")[-1]] = w.field_value
    expected = {
        "Veterans_Beneficiary_First_Name[0]": "Test",
        "Last_Name[0]": "Veteran",
        "SocialSecurityNumber_FirstThreeNumbers[0]": "000",
        "TelephoneNumber_FirstThreeNumbers[0]": "555",
        "Veterans_DOB_Month[0]": "05",
        "MailingAddress_City[0]": "Anytown",
        "VA_File_Number_If_Applicable[0]": "999888777",
    }
    ok = True
    for k, exp in expected.items():
        got = vals.get(k, "")
        if got != exp:
            ok = False
            print(f"[FAIL] {k}: got {got!r} exp {exp!r}")
    rem = vals.get("REMARKS[0]", "")
    if not rem:
        ok = False
        print("[FAIL] REMARKS[0] is empty")
    assert ok, "PDF verification failed"
    print(f"ALL CHECKS PASSED. Remarks len={len(rem)}. PDF: {OUT}")


if __name__ == "__main__":
    run()
