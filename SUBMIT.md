# Submission checklist — Technology in Society (Elsevier)

Double-blind review. Upload files in Editorial Manager in the order and with the labels below.

---

## Cover Letter

| Label in EM | File |
|---|---|
| Cover Letter | `paper/technology-in-society/manuscript/cover_letter.docx` |

---

## Title Page (separate — double-blind requirement)

| Label in EM | File |
|---|---|
| Title Page | `paper/technology-in-society/manuscript/title_page.docx` |

---

## Manuscript (blinded — no author info)

| Label in EM | File |
|---|---|
| Manuscript | `paper/technology-in-society/manuscript/main_blinded.pdf` |
| LaTeX Source (zip) | `main_blinded.tex`, `paper_macros.tex`, `references.bib`, `declarations.tex`, `tables/*.tex` |

EM needs the editable LaTeX source for typesetting; zip the files above and upload alongside the PDF.

> **Do NOT upload** `main.tex` or `main.pdf` — those are the unblinded versions and reveal the authors.

---

## Highlights

| Label in EM | File |
|---|---|
| Highlights | `paper/technology-in-society/manuscript/highlights.docx` |

---

## Author Biographies / Vitae

| Label in EM | File |
|---|---|
| Author Biographies | `paper/technology-in-society/manuscript/author_biographies.docx` |

---

## Figures (upload individually)

| Label in EM | File |
|---|---|
| Figure 1 | `paper/technology-in-society/manuscript/figures/fig_trust_by_intensity.pdf` |
| Figure 2 | `paper/technology-in-society/manuscript/figures/fig_churn_by_intensity.pdf` |
| Figure 3 | `paper/technology-in-society/manuscript/figures/fig_revenue_by_intensity.pdf` |
| Figure 4 | `paper/technology-in-society/manuscript/figures/fig_churn_by_type.pdf` |
| Figure 5 | `paper/technology-in-society/manuscript/figures/fig_per_pattern.pdf` |
| Figure 6 | `paper/technology-in-society/manuscript/figures/fig_sensitivity.pdf` |
| Figure 7 | `paper/technology-in-society/manuscript/figures/fig_morris.pdf` |

> Figure 8 (causal loop diagram) is inline TikZ in `main_blinded.tex` — no separate file needed.

---

## Supplementary Material

| Label in EM | File |
|---|---|
| Supplementary Material | `paper/technology-in-society/supplementary/ODD-protocol.pdf` |

---

## Before hitting Submit

- [ ] Confirm the GenAI declaration in `declarations.tex` reflects actual writing practice (currently names Claude Opus 4.8).
- [ ] Confirm the reference style with the handling editor (manuscript uses Chicago author-date; Elsevier tooling defaults to numbered — one-line switch in `main_blinded.tex` if needed).
- [ ] Deposit the replication package on Zenodo if the editor requests a DOI (GitHub link in the manuscript is sufficient under Elsevier Option C).
