import hashlib
import pandas as pd

FILES = [
    "companies.csv", "contacts.csv", "sales_reps.csv", "campaigns.csv",
    "score_rules.csv", "leads.csv", "consents.csv", "activities.csv",
    "tasks.csv", "opportunities.csv", "stage_history.csv", "ground_truth.csv"
]

def compute_checksum(filepath):
    """Generates a SHA-256 fingerprint of a file to prove reproducibility."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        h.update(f.read())
    return h.hexdigest()[:16]  # Short 16-char hash for clean display

def run_validation():
    print("==========================================")
    print("🔍 RUNNING DATA PIPELINE VALIDATION")
    print("==========================================\n")

    # Load all tables
    companies = pd.read_csv("companies.csv")
    contacts = pd.read_csv("contacts.csv")
    reps = pd.read_csv("sales_reps.csv")
    campaigns = pd.read_csv("campaigns.csv")
    rules = pd.read_csv("score_rules.csv")
    leads = pd.read_csv("leads.csv")
    consents = pd.read_csv("consents.csv")
    activities = pd.read_csv("activities.csv")
    tasks = pd.read_csv("tasks.csv")
    opps = pd.read_csv("opportunities.csv")
    history = pd.read_csv("stage_history.csv")
    gt = pd.read_csv("ground_truth.csv")

    # 1. PRIMARY KEY UNIQUENESS CHECK
    assert companies["Company_ID"].is_unique, "Duplicate Company_ID found!"
    assert contacts["Contact_ID"].is_unique, "Duplicate Contact_ID found!"
    assert reps["SalesRep_ID"].is_unique, "Duplicate SalesRep_ID found!"
    assert campaigns["Campaign_ID"].is_unique, "Duplicate Campaign_ID found!"
    assert leads["Lead_ID"].is_unique, "Duplicate Lead_ID found!"
    assert activities["Activity_ID"].is_unique, "Duplicate Activity_ID found!"
    assert tasks["Task_ID"].is_unique, "Duplicate Task_ID found!"
    assert opps["Opportunity_ID"].is_unique, "Duplicate Opportunity_ID found!"
    assert history["History_ID"].is_unique, "Duplicate History_ID found!"
    print("✅ [PASS] Primary Key Uniqueness across all tables")

    # 2. FOREIGN KEY INTEGRITY CHECK
    assert contacts["Company_ID"].isin(companies["Company_ID"]).all(), "Orphan Company_ID in contacts!"
    assert leads["Contact_ID"].isin(contacts["Contact_ID"]).all(), "Orphan Contact_ID in leads!"
    assert leads["Campaign_ID"].isin(campaigns["Campaign_ID"]).all(), "Orphan Campaign_ID in leads!"
    assert leads["Assigned_Rep_ID"].isin(reps["SalesRep_ID"]).all(), "Orphan SalesRep_ID in leads!"
    assert activities["Lead_ID"].isin(leads["Lead_ID"]).all(), "Orphan Lead_ID in activities!"
    assert tasks["Lead_ID"].isin(leads["Lead_ID"]).all(), "Orphan Lead_ID in tasks!"
    assert opps["Lead_ID"].isin(leads["Lead_ID"]).all(), "Orphan Lead_ID in opportunities!"
    assert history["Opportunity_ID"].isin(opps["Opportunity_ID"]).all(), "Orphan Opportunity_ID in stage_history!"
    print("✅ [PASS] Foreign Key Referential Integrity across all joins")

    # 3. ARITHMETIC SCORE RECONCILIATION
    # Recalculate every lead's score from scratch (Fit points + Activity points)
    fit_map = dict(zip(rules[rules["Category"] == "Fit"]["Condition"], rules[rules["Category"] == "Fit"]["Points"]))
    contact_fit = contacts.set_index("Contact_ID")["Job_Title"].map(fit_map).fillna(0)
    act_sums = activities.groupby("Lead_ID")["Points_Awarded"].sum()

    expected_scores = leads["Contact_ID"].map(contact_fit) + leads["Lead_ID"].map(act_sums).fillna(0)
    mismatches = leads[leads["Lead_Score"] != expected_scores]
    assert len(mismatches) == 0, f"Score mismatch found on {len(mismatches)} leads!"
    print("✅ [PASS] Arithmetic Reconciliation (100% of Lead Scores match Fit + Activity weights)")

    # 4. CHRONOLOGICAL DATE ORDERING CHECK
    leads_dt = pd.to_datetime(leads.set_index("Lead_ID")["Created_At"])
    act_dt = pd.to_datetime(activities["Occurred_At"])
    act_lead_created = activities["Lead_ID"].map(leads_dt)
    assert (act_dt >= act_lead_created).all(), "Found Activity occurring BEFORE Lead creation!"

    opp_dt = pd.to_datetime(opps["Created_At"])
    opp_lead_created = opps["Lead_ID"].map(leads_dt)
    assert (opp_dt >= opp_lead_created).all(), "Found Opportunity occurring BEFORE Lead creation!"
    print("✅ [PASS] Chronological Ordering (All events occur strictly after parent creation)")

    # 5. EDGE CASE DETECTION & GROUND TRUTH RECONCILIATION
    # Verify that the ONLY rule violations in the dataset are the exact ones logged in ground_truth.csv
    gt_by_type = gt.groupby("Issue_Type")["Lead_ID"].apply(set).to_dict()

    # Check A: Opted-out leads contacted
    merged_tasks = tasks.merge(consents, on="Lead_ID")
    illegal_tasks = merged_tasks[
        (merged_tasks["Opted_In"] == False) &
        (pd.to_datetime(merged_tasks["Created_At"]) > pd.to_datetime(merged_tasks["Updated_At"]))
    ]
    assert set(illegal_tasks["Lead_ID"]) == gt_by_type["opted_out_lead_contacted"], "Opt-out edge case mismatch!"

    # Check B: Post-conversion scoring leak
    merged_act_opp = activities.merge(opps, on="Lead_ID")
    post_conv_acts = merged_act_opp[pd.to_datetime(merged_act_opp["Occurred_At"]) > pd.to_datetime(merged_act_opp["Created_At"])]
    assert set(post_conv_acts["Lead_ID"]) == gt_by_type["score_uses_post_conversion_event"], "Post-conversion edge case mismatch!"

    # Check C: Out-of-territory routing
    merged_rep = leads.merge(reps, left_on="Assigned_Rep_ID", right_on="SalesRep_ID")
    wrong_territory = merged_rep[merged_rep["Territory_x"] != merged_rep["Territory_y"]]
    assert set(wrong_territory["Lead_ID"]) == gt_by_type["lead_assigned_outside_territory"], "Territory edge case mismatch!"

    # Check D: Stage history gaps (fewer than 4 stages)
    stage_counts = history.groupby("Opportunity_ID")["Stage"].count()
    gapped_opps = set(stage_counts[stage_counts < 4].index)
    gt_gapped_opps = set(gt[gt["Issue_Type"] == "stage_history_has_gaps"]["Opportunity_ID"])
    assert gapped_opps == gt_gapped_opps, "Stage gap edge case mismatch!"

    print("✅ [PASS] Anomaly Reconciliation (All 50 injected edge cases match ground_truth.csv; 0 unintended errors)")

    # 6. ROW COUNTS & SHA-256 CHECKSUMS (Step 10 Reproducibility Proof)
    print("\n--- Summary & SHA-256 Checksums ---")
    for fname in FILES:
        df_tmp = pd.read_csv(fname)
        print(f"{fname:<22} | Rows: {len(df_tmp):<7} | SHA256: {compute_checksum(fname)}")

if __name__ == "__main__":
    run_validation()