# Data Dictionary & Entity-Relationship Schema

## 1. Entity-Relationship Cardinality & Lifecycle Overview

| Parent Entity | Child Entity | Cardinality | Relationship & Foreign Key |
| :--- | :--- | :--- | :--- |
| `Company` | `Contact` | **1:N** | One company employs zero or more contacts (`Contact.Company_ID -> Company.Company_ID`). |
| `Contact` | `Lead` | **1:N** | One contact can generate multiple leads across campaigns (`Lead.Contact_ID -> Contact.Contact_ID`). |
| `Campaign` | `Lead` | **1:N** | One campaign attributes many leads (`Lead.Campaign_ID -> Campaign.Campaign_ID`). |
| `SalesRep` | `Lead` | **1:N** | One sales rep is assigned many leads matching territory (`Lead.Assigned_Rep_ID -> SalesRep.SalesRep_ID`). |
| `Lead` | `Consent` | **1:1** | Each baseline lead has an explicit consent record (`Consent.Lead_ID -> Lead.Lead_ID`). |
| `Lead` | `Activity` | **1:N** | One lead performs 1 to 5+ tracked engagement/intent events (`Activity.Lead_ID -> Lead.Lead_ID`). |
| `Lead` | `Task` | **1:N** (Optional) | Qualified, opted-in leads generate follow-up tasks (`Task.Lead_ID -> Lead.Lead_ID`). |
| `Lead` | `Opportunity` | **1:1** (Optional) | High-scoring leads convert into sales opportunities (`Opportunity.Lead_ID -> Lead.Lead_ID`). |
| `Opportunity` | `StageHistory` | **1:N** | Each opportunity records immutable stage transition logs (`StageHistory.Opportunity_ID -> Opportunity.Opportunity_ID`). |

### Lifecycle States
* **Lead Lifecycle:** `New` $\rightarrow$ `Qualified` (when `Lead_Score >= 50`) $\rightarrow$ `Converted` (when converted into an `Opportunity`).
* **Opportunity Stage Progression:** `Discovery` $\rightarrow$ `Demo` $\rightarrow$ `Negotiation` $\rightarrow$ `Closed Won`.

---

## 2. Entity Field Specifications

### `companies.csv` (`Company`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Company_ID` | String | Required | `CO-000001` .. `CO-999999` | ID | Primary Key (Unique) | Regex `^CO-\d{6}$`, non-null |
| `Company_Name` | String | Required | Any non-empty business name | Text | Non-unique | Length > 0 |
| `Industry` | String | Required | `Technology`, `Healthcare`, `Finance`, `Retail`, `Manufacturing` | Enum | Non-unique | Must belong to allowed enum list |
| `Region` | String | Required | `AMER`, `EMEA`, `APAC`, `LATAM` | Territory Code | Non-unique | Must match valid sales territory |

### `contacts.csv` (`Contact`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Contact_ID` | String | Required | `CON-000001` .. `CON-999999` | ID | Primary Key (Unique) | Regex `^CON-\d{6}$`, non-null |
| `Company_ID` | String | Required | Valid `Company.Company_ID` | ID | Foreign Key | Must exist in `companies.csv` |
| `First_Name` | String | Required | Alphabetic name string | Text | Non-unique | Non-empty string |
| `Last_Name` | String | Required | Alphabetic name string | Text | Non-unique | Non-empty string |
| `Email` | String | Required | Valid email format | Text | Unique (except injected dupes) | Must contain `@` and domain |
| `Job_Title` | String | Required | `CEO`, `VP of Sales`, `Marketing Director`, `Software Engineer`, `HR Manager`, `Intern` | Enum | Non-unique | Maps to `ScoreRule` Fit weights |

### `sales_reps.csv` (`SalesRep`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SalesRep_ID` | String | Required | `REP-000001` .. `REP-999999` | ID | Primary Key (Unique) | Regex `^REP-\d{6}$`, non-null |
| `Name` | String | Required | Full name string | Text | Non-unique | Non-empty string |
| `Territory` | String | Required | `AMER`, `EMEA`, `APAC`, `LATAM` | Territory Code | Non-unique | Must match `Company.Region` |
| `Active` | Boolean | Required | `True`, `False` | Flag | Non-unique | Boolean (`True` for active routing) |

### `campaigns.csv` (`Campaign`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Campaign_ID` | String | Required | `CAMP-000001` .. `CAMP-999999` | ID | Primary Key (Unique) | Regex `^CAMP-\d{6}$`, non-null |
| `Name` | String | Required | Campaign title string | Text | Non-unique | Non-empty string |
| `Channel` | String | Required | `Email`, `Paid Search`, `LinkedIn`, `Webinar`, `Organic` | Enum | Non-unique | Must belong to allowed channels |
| `Budget` | Integer | Required | `5000` .. `50000` | USD ($) | Non-unique | `Budget > 0` |
| `Start_Date` | Date | Required | `YYYY-MM-DD` | Date | Non-unique | Valid ISO date |

### `score_rules.csv` (`ScoreRule`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Rule_ID` | String | Required | `RULE-001` .. `RULE-999` | ID | Primary Key (Unique) | Regex `^RULE-\d{3}$` |
| `Category` | String | Required | `Fit`, `Engagement`, `Intent` | Enum | Non-unique | Must be valid scoring dimension |
| `Condition` | String | Required | Job title or Activity action name | Enum | Unique | Matches `Job_Title` or `Activity.Action` |
| `Points` | Integer | Required | `0` .. `50` | Score Points | Non-unique | `Points >= 0` |

### `leads.csv` (`Lead`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Lead_ID` | String | Required | `LEAD-2026-000001` .. `LEAD-2026-999999` | ID | Primary Key (Unique) | Regex `^LEAD-2026-\d{6}$` |
| `Contact_ID` | String | Required | Valid `Contact.Contact_ID` | ID | Foreign Key | Must exist in `contacts.csv` |
| `Campaign_ID` | String | Required | Valid `Campaign.Campaign_ID` | ID | Foreign Key | Must exist in `campaigns.csv` |
| `Territory` | String | Required | `AMER`, `EMEA`, `APAC`, `LATAM` | Territory Code | Non-unique | Inherited from parent `Company.Region` |
| `Assigned_Rep_ID` | String | Required | Valid `SalesRep.SalesRep_ID` | ID | Foreign Key | Rep territory must match `Lead.Territory` |
| `Consent` | Boolean | Required | `True`, `False` | Flag | Non-unique | Must align with `Consent.Opted_In` |
| `Lead_Score` | Integer | Required | `>= 0` | Score Points | Non-unique | Derived: `Fit_Points + Sum(Activity.Points_Awarded)` |
| `Status` | String | Required | `New`, `Qualified`, `Converted` | Enum | Non-unique | Derived from score threshold & conversion |
| `Created_At` | Timestamp | Required | `YYYY-MM-DD HH:MM:SS` | UTC Timestamp | Non-unique | Must precede all child `Activity` timestamps |
| `Last_Activity_At` | Timestamp | Required | `YYYY-MM-DD HH:MM:SS` | UTC Timestamp | Non-unique | `Last_Activity_At >= Created_At` |

### `consents.csv` (`Consent`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Consent_ID` | String | Required | `CONS-000001` .. `CONS-999999` | ID | Primary Key (Unique) | Regex `^CONS-\d{6}$` |
| `Lead_ID` | String | Required | Valid `Lead.Lead_ID` | ID | Foreign Key (Unique) | Must exist in `leads.csv` |
| `Opted_In` | Boolean | Required | `True`, `False` | Flag | Non-unique | Governs legal outreach eligibility |
| `Updated_At` | Timestamp | Required | `YYYY-MM-DD HH:MM:SS` | UTC Timestamp | Non-unique | `Updated_At >= Lead.Created_At` |

### `activities.csv` (`Activity`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Activity_ID` | String | Required | `ACT-LEAD-2026-XXXXXX-XXX` | ID | Primary Key (Unique) | Prefixed with parent `Lead_ID` |
| `Lead_ID` | String | Required | Valid `Lead.Lead_ID` | ID | Foreign Key | Must exist in `leads.csv` |
| `Action` | String | Required | `Opened Email`, `Clicked Link`, `Downloaded PDF`, `Viewed Pricing`, `Requested Demo` | Enum | Non-unique | Matches `ScoreRule.Condition` |
| `Points_Awarded` | Integer | Required | `2`, `5`, `10`, `15`, `50` | Score Points | Non-unique | Must match `ScoreRule.Points` for `Action` |
| `Occurred_At` | Timestamp | Required | `YYYY-MM-DD HH:MM:SS` | UTC Timestamp | Non-unique | Must occur strictly after `Lead.Created_At` |

### `tasks.csv` (`Task`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Task_ID` | String | Required | `TASK-LEAD-2026-XXXXXX-XXX` | ID | Primary Key (Unique) | Prefixed with parent `Lead_ID` |
| `Lead_ID` | String | Required | Valid `Lead.Lead_ID` | ID | Foreign Key | Must exist in `leads.csv` |
| `SalesRep_ID` | String | Required | Valid `SalesRep.SalesRep_ID` | ID | Foreign Key | Must exist in `sales_reps.csv` |
| `Task_Type` | String | Required | `Follow-Up Call`, `Outbound Sales Email` | Enum | Non-unique | Valid outreach action |
| `Status` | String | Required | `Open`, `Completed` | Enum | Non-unique | Valid task lifecycle state |
| `Created_At` | Timestamp | Required | `YYYY-MM-DD HH:MM:SS` | UTC Timestamp | Non-unique | Forbidden if `Consent.Opted_In == False` |

### `opportunities.csv` (`Opportunity`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Opportunity_ID` | String | Required | `OPP-2026-000001` .. `OPP-2026-999999` | ID | Primary Key (Unique) | Regex `^OPP-2026-\d{6}$` |
| `Lead_ID` | String | Required | Valid `Lead.Lead_ID` | ID | Foreign Key | Must exist in `leads.csv` |
| `SalesRep_ID` | String | Required | Valid `SalesRep.SalesRep_ID` | ID | Foreign Key | Must exist in `sales_reps.csv` |
| `Deal_Value` | Integer | Required | `5000` .. `50000` | USD ($) | Non-unique | `Deal_Value > 0` |
| `Stage` | String | Required | `Discovery`, `Demo`, `Negotiation`, `Closed Won`, `Closed Lost` | Enum | Non-unique | Must match final `StageHistory` state |
| `Created_At` | Timestamp | Required | `YYYY-MM-DD HH:MM:SS` | UTC Timestamp | Non-unique | Must occur after `Lead.Created_At` |

### `stage_history.csv` (`StageHistory`)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `History_ID` | String | Required | `SH-000001` .. `SH-999999` | ID | Primary Key (Unique) | Regex `^SH-\d{6}$` |
| `Opportunity_ID` | String | Required | Valid `Opportunity.Opportunity_ID` | ID | Foreign Key | Must exist in `opportunities.csv` |
| `Stage` | String | Required | `Discovery`, `Demo`, `Negotiation`, `Closed Won` | Enum | Non-unique | Sequential progression without skipped stages |
| `Entered_At` | Timestamp | Required | `YYYY-MM-DD HH:MM:SS` | UTC Timestamp | Non-unique | Monotonically increasing per `Opportunity_ID` |

### `ground_truth.csv` (Held-Out Anomaly Labels)
| Field | Type | Req/Opt | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Issue_Type` | String | Required | `opted_out_lead_contacted`, `score_uses_post_conversion_event`, `lead_assigned_outside_territory`, `duplicate_creates_duplicate_opportunity`, `stage_history_has_gaps` | Enum | Non-unique | One of the 5 required negative scenarios |
| `Lead_ID` | String | Required | Valid `Lead.Lead_ID` | ID | Foreign Key | Target lead associated with the anomaly |
| `Opportunity_ID` | String | Optional | Valid `Opportunity.Opportunity_ID` or empty | ID | Foreign Key | Populated when anomaly affects a deal |
| `Affected_Record_ID` | String | Required | ID of the anomalous row/entity | ID | Non-unique | Points directly to the injected artifact |
| `Details` | String | Required | Human-readable explanation | Text | Non-unique | Describes the exact rule violation |