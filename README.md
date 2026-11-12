# Deterministic CRM Lead Scoring & Opportunity Pipeline Generator

End-to-end synthetic data engineering pipeline simulating a B2B CRM workflow: master data creation, consent governance, transparent feature-based lead scoring (Fit + Engagement + Intent), territory-based sales rep routing, follow-up task creation, opportunity conversion, chronological stage history tracking, and labeled anomaly injection.

## 1. Architecture & Workflow

1. **Master & Lookup Layer (`generate_master_data`):** Generates `SalesRep` (20 reps across 4 territories), `Campaign` (15 marketing campaigns), `ScoreRule` (11 explicit scoring weights), `Company` (5,000 accounts), and `Contact` (10,000 individuals) with strict referential integrity.
2. **Lead, Consent & Activity Engine (`generate_leads_pipeline`):** Generates 20,000 leads linked to valid contacts and campaigns, assigns initial opt-in/opt-out `Consent` records, routes leads to territory-matched sales reps, generates chronological `Activity` histories strictly post-creation, computes `Lead_Score` deterministically from `ScoreRule`, and creates follow-up `Task` records for qualified, opted-in leads.
3. **Opportunity & Stage Progression (`generate_opportunities`):** Filters top-scoring opted-in leads, converts 3,000 into `Opportunity` records, and logs immutable stage transitions (`Discovery` $\rightarrow$ `Demo` $\rightarrow$ `Negotiation` $\rightarrow$ `Closed Won`) in `StageHistory`.
4. **Edge Case Injection (`inject_edge_cases`):** Injects 50 labeled anomalies (10 per required negative scenario) without corrupting unrelated records, exporting held-out labels to `ground_truth.csv`.
5. **Automated Reconciliation (`validate.py`):** Verifies primary key uniqueness, foreign key integrity, arithmetic score reconciliation, chronological ordering, anomaly isolation, and SHA-256 checksum reproducibility.

## 2. Quickstart & Commands

### Prerequisites
```bash
pip install pandas faker
```

### Generate Dataset (Fixed Seed: `20261022`)
```bash
python generate_data.py
```

### Validate Integrity & Compute SHA-256 Checksums
```bash
python validate.py
```

## 3. Reproducibility Proof (Fixed Seed: `20261022`)

Running `python generate_data.py` twice with `SEED = 20261022` produces byte-for-byte identical CSV exports with the following row counts and SHA-256 checksums:

| File Name | Row Count | SHA-256 Checksum (16-char prefix) |
| :--- | :--- | :--- |
| `companies.csv` | 5,000 | `129d9d4cb90d4621` |
| `contacts.csv` | 10,010 | `a6774ca033959117` |
| `sales_reps.csv` | 20 | `e7241857dcfa91aa` |
| `campaigns.csv` | 15 | `e55769b3d825c335` |
| `score_rules.csv` | 11 | `fbd637c6ffeedbee` |
| `leads.csv` | 20,010 | `dcf07e033cbc90b5` |
| `consents.csv` | 20,000 | `c273dbf6a1f21f72` |
| `activities.csv` | 60,396 | `8a92a693692810b2` |
| `tasks.csv` | 13,035 | `d2dcc99feeaa7381` |
| `opportunities.csv` | 3,010 | `9344269bb7beb5f1` |
| `stage_history.csv` | 11,980 | `b5fdf90932765603` |
| `ground_truth.csv` | 50 | `0bb2a5f912636ed2` |

## 4. Injected Edge Cases (`ground_truth.csv`)

| Issue Type | Count | Description |
| :--- | :--- | :--- |
| `opted_out_lead_contacted` | 10 | Follow-up outreach `Task` created 2 days after the lead explicitly opted out (`Consent = False`). |
| `score_uses_post_conversion_event` | 10 | `Activity` occurred 3 days after `Opportunity.Created_At` and was improperly added to `Lead_Score`. |
| `lead_assigned_outside_territory` | 10 | `EMEA` lead routed to an `AMER` sales representative (`REP-000001`). |
| `duplicate_creates_duplicate_opportunity` | 10 | Slight email typo (`.dup@`) bypassed deduplication and spawned a duplicate `Contact`, `Lead`, and `Opportunity`. |
| `stage_history_has_gaps` | 10 | Intermediate stages (`Demo`, `Negotiation`) omitted from `StageHistory`, jumping directly from `Discovery` to `Closed Won`. |

## 5. Validation Summary

`validate.py` enforces 5 automated test suites:
1. **Primary Key Uniqueness:** Confirms 0 duplicate IDs across all 12 tables.
2. **Foreign Key Referential Integrity:** Confirms 100% valid parent-child joins across all relationships.
3. **Arithmetic Reconciliation:** Recomputes `Fit + Activity` weights from `score_rules.csv` and confirms 100% agreement with `leads.csv`.
4. **Chronological Ordering:** Confirms every `Activity` and `Opportunity` timestamp occurs strictly after its parent `Lead.Created_At`.
5. **Anomaly Reconciliation:** Confirms that the exact set of rule violations detected across the dataset matches the 50 records in `ground_truth.csv` with zero unintended errors.

## 6. Lawful Data Provenance
All records are 100% synthetically generated via deterministic pseudo-random rules and the `Faker` library. No external proprietary, scraped, or personally identifiable datasets were used.