# VA 21-4138 Medical Opinion Theory Corrector

A guided tool that drafts a VA Form 21-4138 (Statement in Support of Claim) when
the VSR's C&P exam request asks the wrong legal theory (e.g., asks about Direct
Service Connection when the claim is actually Secondary Service Connection,
Aggravation, TERA toxic exposure, or a presumptive pathway) — and **fills the real
21-4138 PDF** so the output is a sign-ready filing, not just text.

## What it does

1. Collects the veteran's identity (the fields that map to the 21-4138 PDF) and
   lets you **save them as a reusable client template** to reload later.
2. Walks you through the case: claim info → claimed condition/theory → the VSR's
   exam-request mismatch → supporting evidence → corrected opinion questions.
3. Generates the theory-mismatch **argument** and stamps it into the form's
   **Remarks** section, with the identity fields filled into the PDF's own boxes
   and today's date in the signature block.
4. Outputs a filled `vba-21-4138-are.pdf` — ready to save to the client's file and sign.

## Running it

Double-click **`Start-4138-Theory-Corrector.bat`**. On first run it installs the
two Python dependencies (Flask, PyMuPDF), then starts a **local-only** server at
`http://127.0.0.1:4138/` and opens it in your browser. Keep the console window
open while you work; close it to stop.

- Fill the wizard, then click **Generate 4138 PDF** (preview pane or the final step).
- **Copy** / **.txt** still export the argument as plain text if you want it.

Requires Python 3 on the machine. Nothing is transmitted off-device — no telemetry,
no cloud, no external calls; the veteran's data never leaves your computer.

## Architecture

- **`4138-theory-corrector.html`** — the entire UI and case logic (vanilla HTML/CSS/JS,
  live preview). Case state auto-saves to `localStorage` under `va4138Draft`; saved
  client templates (identity only) live under `va4138Templates`.
- **`server.py`** — a tiny local Flask app that serves the page and exposes
  `POST /api/fill`. It reuses the companion `va-form-filler`'s proven technique for
  VA's XFA forms (set AcroForm values, strip `/XFA`, flag `NeedAppearances`) rather
  than reimplementing PDF filling in the browser, where VA XFA forms render blank.
- **`field_mappings_4138.py`** — the 21-4138 AcroField mapping (vendored from
  `va-form-filler`).
- **`forms/vba-21-4138-are.pdf`** — the blank government form that gets filled.
- **`test_e2e.py`** — headless-browser smoke test against a synthetic veteran.

The supported legal theories and their corrected opinion questions live in the
`generateQuestions(theoryType)` `switch` inside the HTML — add a theory by adding a `case`.

## Legal theories & TERA

Each *intended* theory auto-selects its anchor citations (`autoSelectCitations`) and
generates theory-specific corrected opinion questions:

| Intended theory | Auto-citations |
|---|---|
| Direct Service Connection | § 3.303, §§ 1110/1131 |
| Secondary — Caused By / Aggravated By | § 3.310 |
| Presumption of Aggravation | § 1153, § 3.306 |
| Gulf War MUCMI | § 3.317, § 1117 |
| PACT Act Presumption | PACT Act, § 3.320 |

**TERA is handled on the *requested* (VSR) side, not as an intended theory** — because
VA frequently orders a Toxic Exposure Risk Activity exam as a path to *denial* instead of
examining the theory the veteran actually raised. When the requested theory is **TERA
Toxic Exposure**, the statement adds a targeted argument that a **38 U.S.C. § 1168** TERA
examination addresses only toxic-exposure nexus and **cannot substitute** for an adequate
opinion on the veteran's actual theory — so a negative/inconclusive TERA opinion does not
discharge the duty to assist and the claim may not be denied on that basis. (§ 1168 is the
non-presumptive nexus route, defined via § 1710(e)(4); distinct from the presumptive
§ 3.320 particulate-matter route.)

## Relationship to the VA Paralegal System

This tool is one of several standalone apps that fold into the **VA Paralegal System**
(`jerome403/va-paralegal-system`), mapping to the **Develop** phase of the case-work
lifecycle, and is a companion to `va-form-filler`. Long-term plan: absorb into the
Paralegal System's frontend as a condition-aware page that reads veteran + claim +
theory data directly from the backend instead of requiring manual entry.

## License

Private. Spearman Appeals LLC.
