# Bharat Development Intelligence & Resource Optimization Platform

BDIE is a batch-first data engineering and decision-support platform for analysing development gaps, fiscal capacity, resources, infrastructure, human capital, economic opportunities, public projects, allocation efficiency and reallocation needs across countries and Indian regions.

## MVP
- ~10 countries for comparison
- India: states/UTs
- One Indian state: district-level analysis (~30–40 districts, subject to data availability)
- 40–60 high-value indicators
- Batch processing as the primary architecture
- Human-in-the-loop allocation, risk and reallocation controls

## Architecture

Data Sources → Azure Data Factory → ADLS Gen2 Bronze → Databricks/PySpark Silver → Gold → Azure SQL/Warehouse → FastAPI + Power BI + Optimization

## Core principle

Regional Capability → Development Gap → Opportunity → Investment → Outcome

## Status

Day 1 — project foundation and ingestion framework.
