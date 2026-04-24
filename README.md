# VA 21-4138 Medical Opinion Theory Corrector

Single-file HTML tool that drafts a VA Form 21-4138 Statement in Support of Claim when the VSR's Medical Exam Request asks the wrong legal theory (e.g., asks about Direct Service Connection when the claim is actually Secondary Service Connection, Aggravation, or a presumptive pathway).

## What it does

Given the VSR's exam question plus the claim's actual medical theory, the tool generates:
- A cover narrative explaining the discrepancy
- A set of **corrected opinion questions** the exam should actually answer (driven by the theory selected)
- A print-ready 21-4138 layout

## Usage

1. Open `4138-theory-corrector.html` in any modern browser. No server, no build step.
2. Fill in the editor pane (left):
   - Case Details (veteran name, VA file number, date, form type)
   - Medical Theory (condition, legal theory, primary SC condition if secondary)
   - The Discrepancy (paste the VSR's exam question, describe what theory it implies)
   - Evidence & Rationale (bullet list)
   - Corrected Opinion Questions (auto-populated from the theory dropdown; editable)
3. Preview updates live in the right pane.
4. Print to PDF for filing.

Case state is persisted via `localStorage` (key: `va_4138_enhanced_v1`).

## Tech stack

- Vanilla HTML / CSS / JavaScript. No framework, no build, no dependencies.
- `localStorage` for auto-save.
- CSS print media query for the filing output.

## Legal theory database

The `theories` object inside the script encodes the supported legal theories (Direct, Secondary, Aggravation, Presumptive variants, etc.) and the corrected opinion questions for each. Extend that object to add new theories.

## Relationship to the VA Paralegal System

This tool is one of several standalone apps that fold into the **VA Paralegal System** (`jerome403/va-paralegal-system`), mapping to the **Develop** phase of the case-work lifecycle. Long-term integration plan: absorb into the Paralegal System's Next.js frontend as a condition-aware page that reads veteran + claim + theory data directly from the system's SQLite backend instead of requiring manual entry.

## License

Private. Spearman Appeals LLC.
