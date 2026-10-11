# PROJECT BLUEPRINT V1

## 1. Executive Summary
BDIE integrates fiscal, economic, infrastructure, natural-resource, human-capital, environmental and project data to support evidence-based resource allocation and development planning.

The platform is decision support, not an autonomous government decision-maker. Recommendations remain subject to human review, policy constraints and audit.

## 2. Problem Statement
Given limited public resources and heterogeneous regional conditions, determine which interventions and projects could generate the greatest sustainable development impact while respecting budget, equity, environmental, fiscal and implementation constraints.

## 3. Objectives
1. Build a reliable batch data platform.
2. Standardize geographic and indicator data.
3. Quantify development gaps.
4. Identify regional economic opportunities.
5. Track project money, progress and risk.
6. Simulate allocation scenarios.
7. Recommend risk-aware reallocations.
8. Preserve human overrides and audit history.
9. Measure outcomes and create a feedback loop.

## 4. Scope
### Geographic hierarchy
GLOBAL → COUNTRY → STATE/UT → DISTRICT → BLOCK/VILLAGE (future).

### MVP
- ~10 countries
- India states/UTs
- One Indian state at detailed district level
- 40–60 high-value indicators
- Batch-first processing
- Public/open data where available

## 5. Non-Goals for MVP
- Real-time streaming
- Individual-level citizen profiling
- Autonomous government spending decisions
- Full national district/block/village coverage
- Production-grade AI chatbot
- Hundreds of datasets

## 6. Functional Requirements
### FR-01 Geography
Maintain standardized country, state and district identifiers.

### FR-02 Data ingestion
Ingest API, CSV, Excel and selected document-based sources using source-specific adapters.

### FR-03 Data quality
Validate schema, types, duplicates, nulls, dates, units, geography and referential integrity.

### FR-04 Fiscal intelligence
Calculate revenue composition, expenditure composition, fiscal capacity, transfer dependency, capex ratio, debt/GSDP and related metrics.

### FR-05 Development intelligence
Calculate normalized development gaps using selected indicators.

### FR-06 Opportunity intelligence
Combine resources, human capability, infrastructure, markets and constraints to identify potential sectors/value chains.

### FR-07 Project monitoring
Track approved budget, releases, expenditure, physical progress, milestones, schedule and risk.

### FR-08 Allocation simulation
Accept budget, objectives, minimum/maximum constraints and risk reserve; return recommended allocations.

### FR-09 Risk engine
Score cost escalation, delays, revenue shortfall, climate/disaster, implementation and environmental risks.

### FR-10 Reallocation
Recalculate remaining resources and candidate reallocations after material changes.

### FR-11 Human override
Allow authorized users to modify recommendations with reason, timestamp and audit trail.

### FR-12 Outcome feedback
Compare predicted and actual outcomes for future model/strategy improvement.

## 7. Non-Functional Requirements
- Reproducible pipelines
- Historical raw snapshots
- Idempotent ingestion where practical
- Metadata-driven scheduling
- Auditable allocation decisions
- Secure credentials
- Testable transformations
- Clear data lineage
- Graceful handling of NO_NEW_DATA

## 8. System Architecture

Data Sources
→ Azure Data Factory
→ ADLS Gen2 / Bronze
→ Databricks + PySpark / Silver
→ Gold
→ Azure SQL / Warehouse
→ FastAPI / Power BI / Optimization

## 9. Data Layers
### Bronze
Raw source snapshots plus ingestion metadata.

### Silver
Validated, typed, standardized and geographically mapped data.

### Gold
Business-ready analytical entities and facts.

## 10. Batch Strategy
- Daily: project expenditure, progress, status and milestones where available.
- Weekly: project monitoring and risk checks.
- Monthly: fiscal and project datasets where published.
- Quarterly: gap/opportunity/allocation review.
- Annual: strategic evaluation and model recalibration.

Frequency is source-dependent. A monthly scheduler checks source_registry and only processes sources that are due. No-new-data is logged rather than treated as a pipeline failure.

## 11. Core Data Model

Dimensions:
dim_country, dim_state, dim_district, dim_block, dim_sector, dim_resource, dim_project, dim_date, dim_indicator.

Facts:
fact_fiscal, fact_revenue, fact_expenditure, fact_infrastructure, fact_resource, fact_human_capital, fact_economic, fact_environment, fact_project_finance, fact_project_progress, fact_project_risk, fact_allocation, fact_reallocation, fact_outcome.

Governance:
pipeline_run_log, data_quality_results, audit_allocation_override.

## 12. API Architecture
FastAPI sits above curated Azure SQL/warehouse data.

Initial endpoint groups:
- /api/v1/health
- /api/v1/countries
- /api/v1/states
- /api/v1/districts
- /api/v1/fiscal
- /api/v1/development
- /api/v1/resources
- /api/v1/infrastructure
- /api/v1/projects
- /api/v1/allocation
- /api/v1/risk
- /api/v1/reallocation

API implementation follows the data model; the full API is built after core Gold tables exist.

## 13. Allocation Engine
Objective:
maximize development impact subject to budget, fiscal, environmental, equity, essential-service, implementation-capacity and project-readiness constraints.

Potential objectives:
- maximum employment
- maximum poverty reduction
- maximum revenue growth
- maximum infrastructure improvement
- balanced development

OR-Tools is the planned optimization library.

## 14. Risk & Contingency Engine
Risk factors include:
cost escalation, project delay, revenue shortfall, disaster/climate exposure, supply-chain disruption, land acquisition, contractor performance, inflation, environmental restrictions and fiscal stress.

Maintain a risk reserve instead of allocating 100% of available budget.

## 15. Human-in-the-Loop
System recommendations are advisory. Manual changes are stored in audit_allocation_override with:
recommendation ID, original allocation, manual allocation, difference, reason, user/authority, timestamp and approval status.

## 16. Technology Stack
Python, SQL, Azure Data Factory, ADLS Gen2, Databricks, PySpark, Delta Lake, Azure SQL/Warehouse, FastAPI, OR-Tools, scikit-learn, Power BI, GitHub, Pytest and GitHub Actions.

## 17. Security & Governance
- Never commit secrets.
- Use environment variables/managed identity in deployment.
- Maintain source lineage.
- Preserve raw historical snapshots.
- Restrict allocation overrides by role.
- Audit every recommendation and override.
- Do not infer sensitive individual attributes.

## 18. MVP Success Metrics
- Reproducible end-to-end batch pipeline
- Automated source metadata handling
- Data quality score for every ingested dataset
- Geographic referential integrity
- Project financial/physical monitoring
- Working allocation simulation
- Auditable manual override
- Working Power BI decision dashboard
- Documented lineage and architecture

## 19. 12-Week Roadmap
Week 1: architecture, sources, data dictionary, ERD, repository, first ingestion.
Week 2: geography and source registry.
Week 3: ADLS Bronze and ADF batch framework.
Week 4: Silver/PySpark and data quality.
Week 5: Gold and Azure SQL.
Week 6: fiscal/development intelligence.
Week 7: resource/infrastructure/human-capital/opportunity intelligence.
Week 8: project monitoring and risk.
Week 9: allocation optimization.
Week 10: risk/reallocation/manual override/audit.
Week 11: FastAPI and Power BI.
Week 12: testing, CI/CD, documentation and final demonstration.

## 20. Day 1 Definition of Done
- Repository structure exists.
- Blueprint V1 exists.
- Source registry structure exists.
- Data dictionary starter exists.
- Ingestion framework skeleton exists.
- First local ingestion test runs.
- Project can be committed as a coherent first milestone.
