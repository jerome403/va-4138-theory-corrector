# CLAUDE.md — VA Form 21-4138 Theory Corrector

A single-file, no-build browser tool that drafts **VA Form 21-4138 (Statement in
Support of Claim)**. It corrects the recurring mismatch between the theory of
entitlement a veteran raised and the narrower theory implied by the AOJ's C&P exam
question, and requests corrected medical-opinion questions. Part of the Spearman
Appeals client-lifecycle filing system; companion to `va-form-filler` and
`cfile-sorter`.

## PII rule (hard constraint — read first)

This tool handles **real veteran PII**. The rules are non-negotiable:

- **Never open, read, print, echo, or copy the contents of any real client file** —
  especially `Client_Data.txt` or anything under a client folder. Not in chat, code,
  comments, commit messages, or logs.
- **Never reproduce a real client or folder name.** Describe structure generically
  ("each client folder has a `Client_Data.txt`") or use `<ClientName>`. Don't dump
  directory listings of client folders. Pasted logs are pre-redacted — never echo a
  client name.
- **Validate/screenshot ONLY against the synthetic `Test Veteran` fixture** you create
  with fake data (e.g. file number `000 00 0000`, `123 Test St, Anytown, WA 00000`),
  kept in a throwaway temp folder, never among real clients.
- **Local-only is a privacy guarantee, not a preference.** Nothing transmits profile
  data off-machine — no telemetry, no cloud, no new external calls. The client data
  itself lives **outside this repo** and must never be copied into it.
- **Never write PII into memory, code, or git.** If you'd need real data to proceed,
  **stop and ask**. If you realize you've captured PII, **say so immediately and stop**.

## Core model (read before touching the form logic)

- **The entire app is `4138-theory-corrector.html`** — HTML + CSS + JS in one file,
  vanilla JS, `document.getElementById`, inline `oninput="updatePreview()"` handlers.
- **State** persists to `localStorage` under the key **`va4138Draft`** (JSON). The
  live key is `va4138Draft` — *not* any older `va_4138_*` name.
- **Flow:** 5-step form (`section-1`..`section-5`) → live preview (`previewDocument`)
  → copy / download as plain text.
- **`gatherFormData` is the single source of form state.** `generateDocumentHTML`
  (preview) and `generatePlainText` (export) both render from it.
- **Theory → corrected questions is a `switch` in `generateQuestions(theoryType)`** —
  there is no `theories` object. Add a theory by adding a `case`.
- **Profile import:** `handleProfileFile` → `parseProfileText` → `applyProfileData`.

**For substantial legal/feature work, use the `va-4138-drafting-architect` agent**
(`.claude/agents/`). It owns the theory→corrected-questions logic, the citations, the
statement template, and the profile mapping — and briefs-then-builds with check-ins.
Pure visual polish goes to the impeccable loop instead.

### Adding/renaming a form field is a MULTI-FUNCTION change

A new field touches **all of** `gatherFormData`, `saveProgress`, `loadProgress`, and
(if it appears in output) `generateDocumentHTML` + `generatePlainText`. Update them
together, and **guard the new key in `loadProgress`** (`if (data.x) ...`) so older
saved `va4138Draft` drafts still load. Never break existing drafts.

## Profile data contract (the #2 footgun: silent field drift)

`Client_Data.txt` (from `va-form-filler`) is flat `key=value`, one file per client
folder. Populated fields are usually `Name`, `FileNumber`, `Address`, `EffectiveDate`;
a larger superset (`FirstName`, `LastName`, `MiddleInitial`, `Street`, `Apt`, `City`,
`State`, `ZIP`, `Country`, …) is defined but usually empty. **If `va-form-filler`
renames a key, import silently stops filling that field** — diff the two apps' field
names if a load looks empty.

| Profile key     | 4138 field        | Notes                                               |
|-----------------|-------------------|-----------------------------------------------------|
| `Name`          | `veteranName`     | Fallback: `FirstName`+`MiddleInitial`+`LastName`    |
| `FileNumber`    | `fileNumber`      |                                                     |
| `Address`       | `mailingAddress`  | Fallback: `Street`/`Apt`/`City`/`State`/`ZIP`/`Country` |
| `EffectiveDate` | **(unmapped)**    | ≠ Date of Rating Decision (different legal meaning) |

Everything else (condition, theories, exam question, evidence, opinion questions) is
**manual** — the profile can't supply it. Loaded values fill identity fields; fields
the profile lacks keep whatever was typed (manual fallback). Keys are matched
case-insensitively; `#` and blank lines are ignored.

## Conventions / invariants

- **Preserve single-file, no-build.** No bundler, framework, npm runtime deps, or
  server. Must run by double-clicking the HTML from `file://`. Choose `file://`-safe
  techniques (`<input type="file">` + `FileReader`, **not** the File System Access
  API).
- **Legal accuracy is correctness.** Citations, theory mappings, and opinion-question
  wording are domain-critical. Don't "improve" legal text unasked; respect mappings
  that carry legal meaning (e.g. `EffectiveDate` ≠ rating date).
- **OneDrive file locks.** This repo lives on OneDrive; sync can cause transient
  `PermissionError`/WinError 32 on writes. Retry rather than assuming corruption.
- **Keep changes scoped.** Smallest change that does the job over speculative refactor.
- **Confirm before destructive/outward-facing actions** (overwrite, delete, push).
  Report outcomes faithfully — if a step was skipped or a check failed, say so.

## Deployment & sync — the #1 footgun: two copies drift

- **Source of truth = this git/APPS repo.** Edit and commit HERE.
- A **Desktop working copy** exists so the tool survives moving off OneDrive, with a
  shortcut (`4138 Theory Corrector.lnk`) pointing at the **Desktop** copy. It is a
  **derivative — never edit it directly; it gets overwritten.**
- **A single HTML file in two places WILL drift.** After any change here, run
  **`sync-to-desktop.ps1`** to refresh the Desktop copy. Treat "synced to Desktop" as
  part of "done" (see standing rule).

## impeccable design loop (for any front-end work)

The [impeccable](https://impeccable.style) skill is installed at `.claude/skills/`
(reinstall: `npx impeccable install --providers=claude -y`). Front-end changes are a
**deliberate design surface**, not a generic form — see `PRODUCT.md` (who/feel) and
`DESIGN.md` (tokens); both at repo root are the **live source of truth** and drive
impeccable. Keep them in sync with what ships.

- **Run the loop on every UI phase:** shape → craft → critique → polish / bolder /
  delight. `critique` checks for *under-crafted*; the detector checks for *wrong* —
  run both.
- **Mechanical gate before shipping UI:** `npx impeccable detect 4138-theory-corrector.html`.
  Don't introduce **new** findings. (The current 8 are pre-existing palette/contrast
  items — slate help-text, placeholders, navy chrome glow — slated for a `polish`
  pass; `PRODUCT.md` records no formal WCAG target.) Point `detect` **only** at the
  HTML, **never** a firm root / client folder.
- **The after-edit hook** (`.claude/settings.local.json`, machine-local) only fires
  when Claude Code is rooted at THIS repo — open the project here for design passes.
- **Local assets only.** Today the one external request is the Google Fonts
  stylesheet; add no others, and bundling those fonts to remove even that is the goal.
  Keep a `prefers-reduced-motion` fallback (currently missing — a known gap).

## Session continuity / handoff workflow

Keep progress in its lane (no duplication, which drifts):
- **git history + commit messages** — the detailed, automatic changelog. Write good
  ones; reference work plainly.
- **This file (`CLAUDE.md`)** — durable "how this project works": model, conventions,
  invariants. Slow-changing. **No task status here.**
- **`PRODUCT.md` / `DESIGN.md`** — strategy and visual tokens; update when the product
  intent or the shipped look changes.
- **`NEXT_SESSION.md`** (optional) — a SHORT pointer to "what's next," not a log.

**Standing rule (do this without being asked):** when a change ships, finishing the
unit of work includes — validate in a browser against the synthetic fixture, run the
`impeccable detect` gate, **show the diff**, **run `sync-to-desktop.ps1`**, then commit
(and push). The human shouldn't have to ask for the handoff.

**Safety net (as in `cfile-sorter`):** a `Stop` hook can print a non-blocking reminder
when a session ends with uncommitted/unpushed work. Add one if desired; it never
blocks and stays silent when clean.

## Validation

No automated harness. Before shipping, load the HTML in a browser with the **synthetic**
`Test Veteran` profile and confirm: Load Profile fills only the identity fields; the
caption block + plain-text export render; manual fields stay untouched; `EffectiveDate`
does NOT populate the rating date; an old `va4138Draft` still loads; print output looks
right. Never validate with a real client file.

## Repo

`github.com/jerome403/va-4138-theory-corrector`. **Canonical:**
`…\OneDrive - Spearman Appeals LLC\APPS\va-4138-theory-corrector` (this repo).
**Derivative:** `…\OneDrive\Desktop\4138-theory-corrector.html` (synced, never edited
directly). `settings.local.json` is machine-local — gitignored, never committed.
