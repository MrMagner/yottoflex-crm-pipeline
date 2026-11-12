import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

# ---------------------------------------------------------
# 1. FIXED SEED FOR REPRODUCIBILITY
# ---------------------------------------------------------
SEED = 20261022
random.seed(SEED)
fake = Faker()
fake.seed_instance(SEED)

BASE_DATE = datetime(2026, 1, 1, 9, 0, 0)

def random_date(start_dt, min_days=1, max_days=30):
    return start_dt + timedelta(
        days=random.randint(min_days, max_days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

# ---------------------------------------------------------
# 2. MASTER & LOOKUP TABLES
# ---------------------------------------------------------
def generate_master_data(num_companies=5000, num_contacts=10000):
    print("1. Generating Master & Lookup Tables (Companies, Contacts, SalesReps, Campaigns, ScoreRules)...")
    
    regions = ["AMER", "EMEA", "APAC", "LATAM"]
    industries = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing"]
    company_starts = ["Apex", "Bright", "Cedar", "Evergreen", "First", "Global", "Northstar", "Pioneer", "Summit", "Vertex"]
    company_ends = ["Systems", "Solutions", "Industries", "Group", "Holdings", "Technologies", "Partners", "Works"]

    # A. SalesReps (20 reps, 5 per territory)
    sales_reps = []
    reps_by_region = {r: [] for r in regions}
    for i in range(1, 21):
        rep_id = f"REP-{str(i).zfill(6)}"
        region = regions[(i - 1) % len(regions)]
        rep = {
            "SalesRep_ID": rep_id,
            "Name": fake.name(),
            "Territory": region,
            "Active": True
        }
        sales_reps.append(rep)
        reps_by_region[region].append(rep_id)

    # B. Campaigns (15 marketing campaigns)
    campaigns = []
    channels = ["Email", "Paid Search", "LinkedIn", "Webinar", "Organic"]
    for i in range(1, 16):
        campaigns.append({
            "Campaign_ID": f"CAMP-{str(i).zfill(6)}",
            "Name": f"2026 {random.choice(channels)} Push #{i}",
            "Channel": random.choice(channels),
            "Budget": random.randint(5000, 50000),
            "Start_Date": BASE_DATE.strftime("%Y-%m-%d")
        })

    # C. ScoreRules (Transparent weights for Fit + Intent)
    score_rules = [
        {"Rule_ID": "RULE-001", "Category": "Fit", "Condition": "CEO", "Points": 20},
        {"Rule_ID": "RULE-002", "Category": "Fit", "Condition": "VP of Sales", "Points": 15},
        {"Rule_ID": "RULE-003", "Category": "Fit", "Condition": "Marketing Director", "Points": 10},
        {"Rule_ID": "RULE-004", "Category": "Fit", "Condition": "Software Engineer", "Points": 5},
        {"Rule_ID": "RULE-005", "Category": "Fit", "Condition": "HR Manager", "Points": 5},
        {"Rule_ID": "RULE-006", "Category": "Fit", "Condition": "Intern", "Points": 0},
        {"Rule_ID": "RULE-007", "Category": "Engagement", "Condition": "Opened Email", "Points": 2},
        {"Rule_ID": "RULE-008", "Category": "Engagement", "Condition": "Clicked Link", "Points": 5},
        {"Rule_ID": "RULE-009", "Category": "Intent", "Condition": "Downloaded PDF", "Points": 10},
        {"Rule_ID": "RULE-010", "Category": "Intent", "Condition": "Viewed Pricing", "Points": 15},
        {"Rule_ID": "RULE-011", "Category": "Intent", "Condition": "Requested Demo", "Points": 50},
    ]

    # D. Companies (5,000)
    companies = []
    company_region_map = {}
    for i in range(1, num_companies + 1):
        comp_id = f"CO-{str(i).zfill(6)}"
        region = random.choice(regions)
        company_region_map[comp_id] = region
        companies.append({
            "Company_ID": comp_id,
            "Company_Name": f"{random.choice(company_starts)} {random.choice(company_ends)}",
            "Industry": random.choice(industries),
            "Region": region
        })

    # E. Contacts (10,000)
    contacts = []
    contact_map = {}
    job_titles = ["CEO", "VP of Sales", "Marketing Director", "Software Engineer", "HR Manager", "Intern"]
    for i in range(1, num_contacts + 1):
        cont_id = f"CON-{str(i).zfill(6)}"
        comp_id = f"CO-{str(random.randint(1, num_companies)).zfill(6)}"
        first = fake.first_name()
        last = fake.last_name()
        domain = fake.free_email_domain()
        title = random.choice(job_titles)
        record = {
            "Contact_ID": cont_id,
            "Company_ID": comp_id,
            "First_Name": first,
            "Last_Name": last,
            "Email": f"{first.lower()}.{last.lower()}@{domain}",
            "Job_Title": title
        }
        contacts.append(record)
        contact_map[cont_id] = {**record, "Region": company_region_map[comp_id]}

    return sales_reps, reps_by_region, campaigns, score_rules, companies, contacts, contact_map

# ---------------------------------------------------------
# 3. LEADS, CONSENT, ACTIVITIES & TASKS
# ---------------------------------------------------------
def generate_leads_pipeline(contacts, contact_map, campaigns, reps_by_region, score_rules, num_leads=20000):
    print("2. Generating Leads, Consent, Activities, and Follow-Up Tasks...")
    
    fit_points = {r["Condition"]: r["Points"] for r in score_rules if r["Category"] == "Fit"}
    act_points = {r["Condition"]: r["Points"] for r in score_rules if r["Category"] != "Fit"}
    act_types = list(act_points.keys())
    campaign_ids = [c["Campaign_ID"] for c in campaigns]

    leads = []
    consents = []
    activities = []
    tasks = []

    for i in range(1, num_leads + 1):
        lead_id = f"LEAD-2026-{str(i).zfill(6)}"
        contact = contacts[random.randint(0, len(contacts) - 1)]
        cont_id = contact["Contact_ID"]
        region = contact_map[cont_id]["Region"]
        
        # Route strictly to a SalesRep in the matching territory
        assigned_rep = random.choice(reps_by_region[region])
        created_at = random_date(BASE_DATE, 1, 120)

        # Consent record (90% Opt-In, 10% Opt-Out)
        opted_in = random.choices([True, False], weights=[90, 10])[0]
        consent_dt = created_at + timedelta(minutes=5)
        consents.append({
            "Consent_ID": f"CONS-{str(i).zfill(6)}",
            "Lead_ID": lead_id,
            "Opted_In": opted_in,
            "Updated_At": consent_dt.strftime("%Y-%m-%d %H:%M:%S")
        })

        # Start score with Fit points from Job Title
        total_score = fit_points.get(contact["Job_Title"], 0)

        # Generate 1 to 5 chronological Activities strictly AFTER lead creation
        num_acts = random.randint(1, 5)
        curr_dt = created_at
        for a_idx in range(1, num_acts + 1):
            curr_dt = curr_dt + timedelta(hours=random.randint(2, 72))
            action = random.choice(act_types)
            pts = act_points[action]
            total_score += pts
            
            activities.append({
                "Activity_ID": f"ACT-{lead_id}-{str(a_idx).zfill(3)}",
                "Lead_ID": lead_id,
                "Action": action,
                "Points_Awarded": pts,
                "Occurred_At": curr_dt.strftime("%Y-%m-%d %H:%M:%S")
            })

        # Create a follow-up Task ONLY if the lead has Opted-In and has a decent score
        if opted_in and total_score >= 30:
            task_dt = curr_dt + timedelta(hours=random.randint(1, 24))
            tasks.append({
                "Task_ID": f"TASK-{lead_id}-001",
                "Lead_ID": lead_id,
                "SalesRep_ID": assigned_rep,
                "Task_Type": "Follow-Up Call",
                "Status": "Completed",
                "Created_At": task_dt.strftime("%Y-%m-%d %H:%M:%S")
            })

        leads.append({
            "Lead_ID": lead_id,
            "Contact_ID": cont_id,
            "Campaign_ID": random.choice(campaign_ids),
            "Territory": region,
            "Assigned_Rep_ID": assigned_rep,
            "Consent": opted_in,
            "Lead_Score": total_score,
            "Status": "Qualified" if total_score >= 50 else "New",
            "Created_At": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Last_Activity_At": curr_dt.strftime("%Y-%m-%d %H:%M:%S")
        })

    return leads, consents, activities, tasks

# ---------------------------------------------------------
# 4. OPPORTUNITIES & STAGE HISTORY
# ---------------------------------------------------------
def generate_opportunities(leads, num_opps=3000):
    print("3. Generating Opportunities and Chronological Stage History...")
    
    # Only opted-in leads with highest scores convert cleanly in baseline
    eligible_leads = [l for l in leads if l["Consent"] is True]
    eligible_leads.sort(key=lambda x: x["Lead_Score"], reverse=True)
    top_leads = eligible_leads[:num_opps]

    opportunities = []
    stage_history = []
    standard_stages = ["Discovery", "Demo", "Negotiation", "Closed Won"]
    hist_counter = 1

    for idx, lead in enumerate(top_leads, start=1):
        opp_id = f"OPP-2026-{str(idx).zfill(6)}"
        last_act_dt = datetime.strptime(lead["Last_Activity_At"], "%Y-%m-%d %H:%M:%S")
        opp_created_dt = last_act_dt + timedelta(days=random.randint(1, 5))
        
        lead["Status"] = "Converted"

        opportunities.append({
            "Opportunity_ID": opp_id,
            "Lead_ID": lead["Lead_ID"],
            "SalesRep_ID": lead["Assigned_Rep_ID"],
            "Deal_Value": random.randint(5000, 50000),
            "Stage": "Closed Won",
            "Created_At": opp_created_dt.strftime("%Y-%m-%d %H:%M:%S")
        })

        stage_dt = opp_created_dt
        for stage in standard_stages:
            stage_history.append({
                "History_ID": f"SH-{str(hist_counter).zfill(6)}",
                "Opportunity_ID": opp_id,
                "Stage": stage,
                "Entered_At": stage_dt.strftime("%Y-%m-%d %H:%M:%S")
            })
            stage_dt = stage_dt + timedelta(days=random.randint(2, 7))
            hist_counter += 1

    return opportunities, stage_history

# ---------------------------------------------------------
# 5. INJECT THE 5 REQUIRED EDGE CASES + GROUND TRUTH
# ---------------------------------------------------------
def inject_edge_cases(contacts, leads, consents, activities, tasks, opportunities, stage_history, reps_by_region):
    print("4. Injecting 5 Labeled Edge Cases & Building ground_truth.csv...")
    ground_truth = []

    lead_map = {l["Lead_ID"]: l for l in leads}
    consent_map = {c["Lead_ID"]: c for c in consents}

    # EDGE CASE 1: Opted-out lead contacted (10 cases)
    opted_out_leads = [l for l in leads if l["Consent"] is False][:10]
    for lead in opted_out_leads:
        lid = lead["Lead_ID"]
        opt_out_dt = datetime.strptime(consent_map[lid]["Updated_At"], "%Y-%m-%d %H:%M:%S")
        illegal_contact_dt = opt_out_dt + timedelta(days=2)
        bad_task_id = f"TASK-{lid}-999"
        
        tasks.append({
            "Task_ID": bad_task_id,
            "Lead_ID": lid,
            "SalesRep_ID": lead["Assigned_Rep_ID"],
            "Task_Type": "Outbound Sales Email",
            "Status": "Completed",
            "Created_At": illegal_contact_dt.strftime("%Y-%m-%d %H:%M:%S")
        })
        ground_truth.append({
            "Issue_Type": "opted_out_lead_contacted",
            "Lead_ID": lid,
            "Opportunity_ID": "",
            "Affected_Record_ID": bad_task_id,
            "Details": "Task created 2 days after lead opted out"
        })

    # EDGE CASE 2: Score uses post-conversion event (10 cases)
    for opp in opportunities[:10]:
        lid = opp["Lead_ID"]
        opp_dt = datetime.strptime(opp["Created_At"], "%Y-%m-%d %H:%M:%S")
        post_conv_dt = opp_dt + timedelta(days=3)
        bad_act_id = f"ACT-{lid}-999"
        
        activities.append({
            "Activity_ID": bad_act_id,
            "Lead_ID": lid,
            "Action": "Viewed Pricing",
            "Points_Awarded": 15,
            "Occurred_At": post_conv_dt.strftime("%Y-%m-%d %H:%M:%S")
        })
        lead_map[lid]["Lead_Score"] += 15  # Falsely include post-conversion activity in lead score
        ground_truth.append({
            "Issue_Type": "score_uses_post_conversion_event",
            "Lead_ID": lid,
            "Opportunity_ID": opp["Opportunity_ID"],
            "Affected_Record_ID": bad_act_id,
            "Details": "Activity occurred after Opportunity creation and was added to Lead_Score"
        })

    # EDGE CASE 3: Lead assigned outside territory (10 cases)
    used_lead_ids = {g["Lead_ID"] for g in ground_truth}
    emea_leads = [
        l for l in leads
        if l["Territory"] == "EMEA" and l["Status"] != "Converted" and l["Lead_ID"] not in used_lead_ids
    ][:10]
    na_rep = reps_by_region["AMER"][0]
    for lead in emea_leads:
        lead["Assigned_Rep_ID"] = na_rep
        ground_truth.append({
            "Issue_Type": "lead_assigned_outside_territory",
            "Lead_ID": lead["Lead_ID"],
            "Opportunity_ID": "",
            "Affected_Record_ID": na_rep,
            "Details": "EMEA lead routed to AMER sales representative"
        })

    # EDGE CASE 4: Duplicate creates duplicate opportunity (10 cases)
    next_cont_num = len(contacts) + 1
    next_lead_num = len(leads) + 1
    next_opp_num = len(opportunities) + 1
    
    for opp in opportunities[10:20]:
        orig_lead = lead_map[opp["Lead_ID"]]
        orig_cont = next(c for c in contacts if c["Contact_ID"] == orig_lead["Contact_ID"])
        
        dup_cont_id = f"CON-{str(next_cont_num).zfill(6)}"
        dup_lead_id = f"LEAD-2026-{str(next_lead_num).zfill(6)}"
        dup_opp_id = f"OPP-2026-{str(next_opp_num).zfill(6)}"
        
        # Slight email typo bypasses deduplication
        typo_email = orig_cont["Email"].replace("@", ".dup@")
        contacts.append({
            "Contact_ID": dup_cont_id,
            "Company_ID": orig_cont["Company_ID"],
            "First_Name": orig_cont["First_Name"],
            "Last_Name": orig_cont["Last_Name"],
            "Email": typo_email,
            "Job_Title": orig_cont["Job_Title"]
        })
        leads.append({
            "Lead_ID": dup_lead_id,
            "Contact_ID": dup_cont_id,
            "Campaign_ID": orig_lead["Campaign_ID"],
            "Territory": orig_lead["Territory"],
            "Assigned_Rep_ID": orig_lead["Assigned_Rep_ID"],
            "Consent": True,
            "Lead_Score": orig_lead["Lead_Score"],
            "Status": "Converted",
            "Created_At": orig_lead["Created_At"],
            "Last_Activity_At": orig_lead["Last_Activity_At"]
        })
        
        # Clone original lead's activities so score math reconciles 100%
        orig_acts = [a for a in activities if a["Lead_ID"] == orig_lead["Lead_ID"]]
        for a_idx, act in enumerate(orig_acts, start=1):
            activities.append({
                "Activity_ID": f"ACT-{dup_lead_id}-{str(a_idx).zfill(3)}",
                "Lead_ID": dup_lead_id,
                "Action": act["Action"],
                "Points_Awarded": act["Points_Awarded"],
                "Occurred_At": act["Occurred_At"]
            })

        opportunities.append({
            "Opportunity_ID": dup_opp_id,
            "Lead_ID": dup_lead_id,
            "SalesRep_ID": opp["SalesRep_ID"],
            "Deal_Value": opp["Deal_Value"],
            "Stage": "Closed Won",
            "Created_At": opp["Created_At"]
        })
        ground_truth.append({
            "Issue_Type": "duplicate_creates_duplicate_opportunity",
            "Lead_ID": dup_lead_id,
            "Opportunity_ID": dup_opp_id,
            "Affected_Record_ID": orig_lead["Lead_ID"],
            "Details": f"Duplicate of {orig_lead['Lead_ID']} via typo email ({typo_email}) spawned duplicate opportunity"
        })
        next_cont_num += 1
        next_lead_num += 1
        next_opp_num += 1

    # EDGE CASE 5: Stage history has gaps (10 cases)
    gap_opp_ids = {opp["Opportunity_ID"] for opp in opportunities[20:30]}
    # Remove intermediate stages ("Demo" and "Negotiation") so it jumps Discovery -> Closed Won
    stage_history[:] = [
        sh for sh in stage_history
        if not (sh["Opportunity_ID"] in gap_opp_ids and sh["Stage"] in ["Demo", "Negotiation"])
    ]
    for opp in opportunities[20:30]:
        ground_truth.append({
            "Issue_Type": "stage_history_has_gaps",
            "Lead_ID": opp["Lead_ID"],
            "Opportunity_ID": opp["Opportunity_ID"],
            "Affected_Record_ID": opp["Opportunity_ID"],
            "Details": "StageHistory skipped Demo and Negotiation (Discovery -> Closed Won)"
        })

    return ground_truth

# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    sales_reps, reps_by_region, campaigns, score_rules, companies, contacts, contact_map = generate_master_data(5000, 10000)
    leads, consents, activities, tasks = generate_leads_pipeline(contacts, contact_map, campaigns, reps_by_region, score_rules, 20000)
    opportunities, stage_history = generate_opportunities(leads, 3000)
    ground_truth = inject_edge_cases(contacts, leads, consents, activities, tasks, opportunities, stage_history, reps_by_region)

    print("5. Exporting all 12 CSV files...")
    pd.DataFrame(companies).to_csv("companies.csv", index=False)
    pd.DataFrame(contacts).to_csv("contacts.csv", index=False)
    pd.DataFrame(sales_reps).to_csv("sales_reps.csv", index=False)
    pd.DataFrame(campaigns).to_csv("campaigns.csv", index=False)
    pd.DataFrame(score_rules).to_csv("score_rules.csv", index=False)
    pd.DataFrame(leads).to_csv("leads.csv", index=False)
    pd.DataFrame(consents).to_csv("consents.csv", index=False)
    pd.DataFrame(activities).to_csv("activities.csv", index=False)
    pd.DataFrame(tasks).to_csv("tasks.csv", index=False)
    pd.DataFrame(opportunities).to_csv("opportunities.csv", index=False)
    pd.DataFrame(stage_history).to_csv("stage_history.csv", index=False)
    pd.DataFrame(ground_truth).to_csv("ground_truth.csv", index=False)

    print("\n✅ ALL FILES GENERATED SUCCESSFULLY!")
    print("\n--- Preview of ground_truth.csv (Edge Case Summary) ---")
    df_gt = pd.DataFrame(ground_truth)
    print(df_gt["Issue_Type"].value_counts())
    print("\n--- First 5 Rows of ground_truth.csv ---")
    print(df_gt.head())