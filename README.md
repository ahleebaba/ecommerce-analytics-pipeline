# 🛒 E-Commerce Analytics Pipeline

An end-to-end analytics engineering portfolio project showcasing a modern data stack — from REST API ingestion through cloud data warehousing, LLM-powered enrichment, dbt transformation, and business intelligence dashboards. 

Supported by Claude

---

## 📐 Architecture Overview

```
DummyJSON REST API
        ↓
Airbyte (Custom YAML Connector)
        ↓
BigQuery — ingest_ecommerce (Bronze/Raw)
        ↓
Python + Ollama LLM (Tag Enrichment)
        ↓
BigQuery — post_ingest_ecommerce (Silver/Staging)
        ↓
dbt Core (Transformation)
        ↓
BigQuery — hub_ecommerce (Intermediate/SSoT)
        ↓
BigQuery — warehouse_ecommerce (Gold/Marts)
        ↓
Tableau Public (Dashboard) + Streamlit (AI Text-to-SQL Agent) (WIP)
```

---

## 🏗️ Data Architecture — Custom 4-Layer Medallion

| Layer | BigQuery Dataset | Tool | Purpose |
|---|---|---|---|
| 🥉 Bronze | `ingest_ecommerce` | Airbyte | Raw landing zone — untouched source data |
| 🥈 Silver | `post_ingest_ecommerce` | dbt staging + Python | Normalised, cleaned, enriched |
| 🔵 Hub | `hub_ecommerce` | dbt intermediate | Single source of truth — all joins resolved |
| 🥇 Gold | `warehouse_ecommerce` | dbt marts | Business-ready aggregations for Tableau + AI agent |

---

## 🛠️ Tech Stack

| Category | Tool | Purpose |
|---|---|---|
| **Source** | DummyJSON REST API | Free e-commerce dataset (products, users, carts, categories) |
| **Ingestion** | Airbyte OSS + Airbyte hosted on GCP compute Engine | Custom YAML connector — 4 streams |
| **Warehouse** | Google BigQuery (GCP) | Cloud data warehouse — free tier |
| **Enrichment** | Python + Ollama (gemma2:2b) | Local LLM for product tag classification |
| **Transformation** | dbt Core | 4-layer data modelling (staging → intermediate → marts) |
| **Orchestration** | Apache Airflow | DAG-based pipeline scheduling + git-sync deployment |
| **Dashboard** | Tableau Public | Interactive business dashboard |
| **AI Agent** | Streamlit + LLM | Text-to-SQL self-service analytics agent |
| **Version Control** | GitHub | Source of truth for all pipeline code |
| **Infrastructure** | GCP (BigQuery + Compute Engine) | Cloud infrastructure |
| **Local Dev** | Windows + WSL2 + Docker Desktop | Development environment |

---

## 📊 Data Sources

All data sourced from [DummyJSON](https://dummyjson.com) — a free public REST API.

| Endpoint | Records | BigQuery Table | Description |
|---|---|---|---|
| `/products?limit=0` | 194 | `products` | Product catalogue with pricing, ratings, inventory |
| `/users?limit=0` | 208 | `users` | Customer profiles with demographics and address |
| `/carts?limit=0` | 208 | `carts` | Shopping carts with nested product arrays |
| `/products/categories` | 24 | `categories` | Product category lookup table |

> 📁 Postman collection available in `docs/api/` — import to explore all endpoints.

---

## 🔄 Pipeline Orchestration

The pipeline is split into two Airflow DAGs using **Dataset-Aware Scheduling (Airflow 2.4+)**:

### DAG 1: `ecommerce_ingestion`
- **Schedule:** Daily at 5am SGT (`0 5 * * *`)
- **Tasks:**
  1. `airbyte_sync` — triggers Airbyte to sync DummyJSON → BigQuery
  2. `wait_for_airbyte_completion` — waits for sync to finish
- **Emits:** `ECOMMERCE_RAW` dataset signal on completion

### DAG 2: `ecommerce_transformation`
- **Schedule:** Event-driven — triggers when `ECOMMERCE_RAW` signal received
- **Tasks:**
  1. `enrich_product_tags` — runs Ollama LLM to classify new product tags
  2. `dbt_run` — runs all 7 dbt models in dependency order
  3. `dbt_test` — runs data quality tests
  4. `log_completion` — logs pipeline completion

### Git-Sync Deployment
DAG files are automatically synced from GitHub every 5 minutes via a git-sync script — simulating a CI/CD deployment pipeline where pushing to `main` automatically deploys to the Airflow environment.

---

## 🤖 LLM-Powered Tag Enrichment

Products in DummyJSON have a `tags` array (e.g. `["beauty", "mascara"]`). A custom Python script uses **Ollama (gemma2:2b)** — a locally hosted open-source LLM — to intelligently classify the most specific and meaningful tag for each product.

**Why local LLM?**
- ✅ Completely free — no API costs
- ✅ Data never leaves your machine
- ✅ No rate limits
- ✅ Demonstrates MLOps awareness in portfolio

**Incremental processing:**
The script uses a FULL OUTER JOIN logic to detect only NEW products not yet enriched — avoiding redundant LLM calls on every pipeline run.

---

## 🗂️ dbt Models

```
models/
├── staging/          → post_ingest_ecommerce (views)
│   ├── stg_products.sql       — clean + rename product fields, extract dimensions
│   ├── stg_users.sql          — flatten nested JSON address + company fields
│   ├── stg_carts.sql          — cart-level fields only
│   ├── stg_orders.sql         — explode nested products array using UNNEST()
│   └── stg_categories.sql     — category lookup table
│
├── intermediate/     → hub_ecommerce (views)
│   └── int_orders_enriched.sql — join all staging tables + LLM enriched tags
│
└── marts/            → warehouse_ecommerce (tables)
    └── fct_orders.sql          — final business-ready fact table for Tableau
```

**Key dbt techniques demonstrated:**
- `UNNEST()` + `JSON_QUERY_ARRAY()` for nested JSON flattening
- `JSON_VALUE()` for extracting nested struct fields
- Custom `generate_schema_name` macro to prevent schema duplication
- Multi-layer architecture with clear separation of concerns
- Source freshness testing and data quality checks

---

## 📁 Repository Structure

```
ecommerce-analytics-pipeline/
├── docs/
│   └── api/
│       └── dummyjson_ecommerce.postman_collection.json
├── airflow/
│   └── dags/
│       ├── dag_1_ecommerce_ingestion.py
│       └── dag_2_ecommerce_transformation.py
├── ecommerce_pipeline/          ← dbt project
│   ├── dbt_project.yml
│   ├── macros/
│   │   └── generate_schema_name.sql
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── ingestion/
│       ├── enrich_product_tags.py
│       └── archive/
│           └── enrich_product_tags_gemini_v1.py
├── airbyte/
│   └── dummyjson_connector.yaml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Setup Guide

### Prerequisites
- Python 3.11
- Google Cloud account (BigQuery free tier)
- Docker Desktop
- Ollama (for local LLM)
- Airflow 2.9.0 (WSL2/Ubuntu)
- dbt-bigquery

### 1. Clone the repository
```bash
git clone https://github.com/ahleebaba/ecommerce-analytics-pipeline.git
cd ecommerce-analytics-pipeline
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Fill in your GCP credentials and API keys
```

### 3. Set up BigQuery
- Create a GCP project
- Enable BigQuery API
- Create a service account with BigQuery Admin role
- Download credentials JSON
- Create 4 datasets: `ingest_ecommerce`, `post_ingest_ecommerce`, `hub_ecommerce`, `warehouse_ecommerce`

### 4. Set up Airbyte
```bash
# Install abctl
curl -LsfS https://get.airbyte.com | bash
abctl local install
```
- Import `airbyte/dummyjson_connector.yaml` in Connector Builder
- Set up BigQuery destination
- Create connection with Full Refresh | Overwrite sync mode

### 5. Install dbt
```bash
pip install dbt-bigquery
cd ecommerce_pipeline
dbt debug    # verify connection
dbt run      # run all models
dbt test     # run data quality tests
```

### 6. Run LLM enrichment
```bash
# Install Ollama from https://ollama.com
ollama pull gemma2:2b
pip install ollama google-cloud-bigquery python-dotenv
python ecommerce_pipeline/ingestion/enrich_product_tags.py
```

### 7. Set up Airflow
```bash
# In WSL2
pip install "apache-airflow==2.9.0" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.0/constraints-3.11.txt"
airflow db init
airflow users create --username admin --password admin \
  --firstname Lee --lastname JunYan --role Admin \
  --email leejunyan16@gmail.com
airflow webserver --port 8080 -D
airflow scheduler -D
```

---

## ⚠️ Engineering Decisions & Lessons Learned

### Airbyte OSS on Windows/GCP VM
Airbyte OSS (`abctl`) was tested on both Windows WSL2 and GCP Ubuntu VM (e2-standard-2, 8GB RAM, 50GB disk). Both environments encountered a known bug in Airbyte 2.1.0 where replication pods receive 0 memory allocation in STDIO-based Kubernetes deployments. Airbyte Cloud (30-day trial) was used as a managed alternative for the initial data load.

### Full Refresh vs Incremental
DummyJSON is a static API with no timestamp fields — Full Refresh | Overwrite was chosen as the sync mode. In a production pipeline with a real database source, Incremental sync with a cursor field (`updated_at`) would be implemented, with dbt handling deduplication and SCD2 logic.

### Local LLM vs Cloud API
Gemini API (free tier) was initially chosen for tag enrichment but encountered quota exhaustion. Ollama with `gemma2:2b` was adopted as a fully local, free alternative — with the added benefit of keeping data on-premise.

### Dataset-Aware Scheduling
Airflow DAGs use Dataset-Aware Scheduling (Airflow 2.4+) instead of time-based ExternalTaskSensors — eliminating fixed-time dependencies and ensuring the transformation DAG only runs after all upstream data is confirmed ready.

---

## 📈 Dashboard

> 🔗 [View live Tableau Public dashboard](#) ← link coming soon

**Page 1 — Revenue Overview:**
- Total revenue KPIs
- Revenue by category
- Top 10 products by revenue
- Discount impact analysis

**Page 2 — Customer Analysis:**
- Customer demographics (age group, gender)
- Geographic distribution map
- Company and department breakdown
- Basket size analysis

---

## 🤖 AI Analytics Agent

> 🔗 [Launch Streamlit app](#) ← coming soon

A self-service analytics agent powered by an LLM that:
- Accepts natural language questions
- Generates BigQuery SQL automatically
- Executes queries against `warehouse_ecommerce`
- Returns results with visualisations

---

## 👤 Author

**Lee Jun Yan**
Analytics Engineer | 5+ years experience in data pipelines and dashboarding

- 🔗 [LinkedIn](https://linkedin.com/in/leejunyan)
- 📧 leejunyan16@gmail.com
- 🐙 [GitHub](https://github.com/ahleebaba)

---

*This project was built as a portfolio showcase for analytics engineering roles. All data is synthetic (DummyJSON) and no real personal data is used.*