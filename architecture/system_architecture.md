# System Architecture

```text
Public/Open Data Sources
        |
        v
Azure Data Factory
        |
        v
ADLS Gen2 - Bronze
        |
        v
Databricks / PySpark
        |
        +--> Silver
        |
        +--> Gold
                |
                v
        Azure SQL / Warehouse
          /       |        \
         v        v         v
     FastAPI   Power BI   Optimization
                           |
                           v
                    Risk / Reallocation
```

Batch processing is primary. Raw historical snapshots are preserved and downstream layers are derived from validated data.
