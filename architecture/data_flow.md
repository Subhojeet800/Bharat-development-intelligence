# Data Flow

1. Scheduler checks `source_registry`.
2. Sources due for ingestion are selected.
3. Source-specific adapter fetches data.
4. Raw payload is stored in Bronze with ingestion metadata.
5. Data quality checks run.
6. Databricks/PySpark standardizes the data into Silver.
7. Gold tables expose analytical entities.
8. Azure SQL/Warehouse serves curated data.
9. FastAPI and Power BI consume curated data.
10. Allocation/risk/reallocation engines use Gold/warehouse data.
11. Pipeline and decision audit logs preserve lineage.
