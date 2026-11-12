# AI Usage Disclosure, Prompt History & Engineering Reasoning

This document outlines how AI tools were utilized during the 72-hour challenge window, provides access to the prompt history, and details the manual debugging, validation, and architectural decisions made to ensure a reliable, reproducible pipeline.

---

## 1. LLM Tool 

* **AI Assistant Used:** Google Gemini

---

## 2. Where AI Accelerated My Work

* **Boilerplate & Schema Scaffolding:** Accelerated the initial setup of the 11 relational CRM tables (`Company`, `Contact`, `SalesRep`, `Campaign`, `ScoreRule`, `Lead`, `Consent`, `Activity`, `Task`, `Opportunity`, `StageHistory`) and the held-out `ground_truth.csv` export structure using `pandas` and `Faker`.
* **Validation & Checksum Automation:** Assisted in structuring `validate.py` to automate primary key uniqueness checks, foreign key referential integrity assertions, arithmetic score reconciliation, and SHA-256 file hashing.
* **Documentation Formatting:** Sped up the drafting of structured Markdown tables for `data_dictionary.md` and `README.md`.

---

## 3. Where I Relied Heavily on AI

* **Chronological Offset Logic:** Structuring multi-hop timestamp generation (`Lead.Created_At` $\rightarrow$ `Consent.Updated_At` $\rightarrow$ `Activity.Occurred_At` $\rightarrow$ `Opportunity.Created_At` $\rightarrow$ `StageHistory.Entered_At`) so that child events strictly post-date parent records across 150,000+ generated rows.
* **Isolated Edge-Case Injection:** Designing post-generation injection routines for all 5 required negative scenarios (`opted_out_lead_contacted`, `score_uses_post_conversion_event`, `lead_assigned_outside_territory`, `duplicate_creates_duplicate_opportunity`, and `stage_history_has_gaps`) without corrupting unrelated baseline records.

---

## 4. What I Personally Reviewed, Changed & Validated

Rather than treating AI output as plug-and-play, I built, executed, and audited the pipeline incrementally and resolved several data-engineering issues surfaced during testing:

1. **Incremental Stage-by-Stage Execution:**
   * Built and ran the pipeline in discrete milestones (`Companies` $\rightarrow$ `Contacts` $\rightarrow$ `Leads & Activities` $\rightarrow$ `Opportunities` $\rightarrow$ `Edge Cases`), inspecting terminal previews and generated CSVs at every step before adding downstream dependencies.
2. **Resolved Data Structure Mismatch (`list` vs. `DataFrame`):**
   * Identified and fixed a `TypeError` during early integration where `generate_companies` returned a standard Python `list` (via `csv.DictWriter`) while `generate_contacts` expected a `pandas.DataFrame`. Standardized all generator stages on `pd.DataFrame` to maintain clean column indexing and export consistency.
3. **Caught & Fixed Validation Bugs via `validate.py`:**
   * **Duplicate Lead Arithmetic Mismatch:** Running `validate.py` flagged a score mismatch on 10 leads. Upon tracing the logic, I found that Edge Case 4 cloned duplicate `Contact`, `Lead`, and `Opportunity` records with copied `Lead_Score` values, but did not clone their underlying rows in `activities.csv`. I updated the injection logic to clone child activities so 100% of lead scores reconcile mathematically.
   * **Territory Anomaly Overlap & `"NA"` Null Parsing:** `validate.py` flagged unexpected territory mismatches. Investigating this revealed two root causes: (a) Edge Case 3 overlapped with leads later cloned in Edge Case 4, and (b) `pandas.read_csv()` parses the string `"NA"` (North America) as `NaN` (`NULL`), breaking equality checks. I isolated non-converted EMEA leads for Edge Case 3 and standardized the North America territory code to `"AMER"` across the dataset and `ground_truth.csv` descriptions.
4. **Manual CSV Inspection & Reproducibility Verification:**
   * Manually opened `ground_truth.csv`, `leads.csv`, and `stage_history.csv` to verify delimiter alignment and confirm that empty `Opportunity_ID` fields on pre-conversion anomalies were intentional.
   * Verified that all file paths in `generate_data.py` and `validate.py` are relative (no hardcoded local paths) and executed consecutive runs to verify identical 16-character SHA-256 checksums across all 12 CSV files.

---

## 5. Key Engineering Decisions, Trade-offs & Limitations

* **Derived State Over Randomness:** `Lead_Score` is never randomly assigned. Every score is deterministically computed from `score_rules.csv` (`Fit` points from `Contact.Job_Title` + `Engagement`/`Intent` points from `Activity.Action`), ensuring complete auditability.
* **In-Memory Hash Maps for Performance:** Used Python dictionary lookups (`contact_map`, `lead_map`, `consent_map`) during generation instead of repeated DataFrame filtering, keeping full 12-table generation under 3 seconds.
* **Known Limitations:**
  * *Scale:* In-memory generation works well at the target volume (~153,000 total rows), though scaling to 10M+ rows would require chunked streaming or Parquet/DuckDB storage.
  * *Synthetic Email Domains:* Contact emails currently use `Faker`'s free email domains rather than corporate domains derived from their parent `Company_Name`.