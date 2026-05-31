# 🛒 Ecommerce Analytics Pipeline

An end-to-end analytics engineering portfolio project showcasing a modern data stack — from REST API ingestion through cloud data warehousing, LLM-powered enrichment, dbt transformation, and business intelligence dashboards.

Supported by Claude

---

## 📐 Architecture Overview

```
DummyJSON REST API
        ↓
Airbyte OSS (Custom Connector — 4 streams)
        ↓
BigQuery — ingest_ecommerce (Bronze/Raw)
        ↓
Apache Airflow (Orchestration — Dataset-Aware Scheduling)
        ↓
Python + Ollama LLM gemma2:2b (Product Tag Enrichment)
        ↓
BigQuery — post_ingest_ecommerce (Silver/Staging)
        ↓
dbt Core (7 models — staging → intermediate → marts)
        ↓
BigQuery — hub_ecommerce (Intermediate/Single Source of Truth)
        ↓
BigQuery — warehouse_ecommerce (Gold/Marts)
        ↓
Tableau Public (Dashboard) + Streamlit (AI Text-to-SQL Agent) ← coming soon
```

---

## 🏗️ Data Architecture — Custom 4-Layer Medallion

| Layer | BigQuery Dataset | Tool | Purpose |
|---|---|---|---|
| 🥉 Bronze | `ingest_ecommerce` | Airbyte | Raw landing zone — untouched source data |
| 🥈 Silver | `post_ingest_ecommerce` | dbt staging + Python | Normalised, cleaned, LLM-enriched |
| 🔵 Hub | `hub_ecommerce` | dbt intermediate | Single source of truth — all joins resolved |
| 🥇 Gold | `warehouse_ecommerce` | dbt marts | Business-ready fact table for Tableau + AI agent |

---

## 🛠️ Tech Stack

| Category | Tool | Purpose |
|---|---|---|
| **Source** | DummyJSON REST API | Free synthetic e-commerce dataset |
| **Ingestion** | Airbyte OSS | Custom YAML connector — 4 streams |
| **Warehouse** | Google BigQuery | Cloud data warehouse — free tier |
| **Enrichment** | Python + Ollama (gemma2:2b) | Local LLM for product tag classification |
| **Transformation** | dbt Core | 4-layer data modelling |
| **Orchestration** | Apache Airflow 2.9.0 | DAG-based pipeline scheduling |
| **Deployment** | Git-Sync (WSL2 cron) | Auto-deploy DAGs from GitHub |
| **Dashboard** | Tableau Public | Interactive business dashboard |
| **AI Agent** | Streamlit + LLM | Text-to-SQL self-service analytics |
| **Version Control** | GitHub | Source of truth for all pipeline code |
| **Infrastructure** | GCP (BigQuery + Compute Engine) | Cloud infrastructure |
| **Dev Environment** | Windows + WSL2 + Docker Desktop | Local development |

---

## 📊 Data Sources

All data sourced from [DummyJSON](https://dummyjson.com) — a free public REST API requiring no authentication.

| Endpoint | Records | BigQuery Table | Description |
|---|---|---|---|
| `/products?limit=0` | 194 | `products` | Product catalogue with pricing, ratings, inventory |
| `/users?limit=0` | 208 | `users` | Customer profiles with demographics and nested address |
| `/carts?limit=0` | 208 | `carts` | Shopping carts with nested product arrays |
| `/products/categories` | 24 | `categories` | Product category lookup table |

> 📁 Postman collection available in `docs/api/` — import to explore all endpoints interactively.

---

## 🔄 Pipeline Orchestration (Airflow)

The pipeline uses **Dataset-Aware Scheduling (Airflow 2.4+)** — splitting into two isolated DAGs that communicate via dataset signals instead of time-based dependencies.

### DAG 1: `ecommerce_ingestion`
- **File:** `airflow/dags/job__day__ecommerce__ingestion.py`
- **Schedule:** Daily at 5am SGT (`0 5 * * *`)
- **Tasks:**
  1. `airbyte_sync` — triggers Airbyte to sync DummyJSON → BigQuery
  2. `wait_for_airbyte_completion` — waits for sync to finish
- **Emits:** `ECOMMERCE_RAW` dataset signal on completion

### DAG 2: `ecommerce_transformation`
- **File:** `airflow/dags/job__day__ecommerce__hub__warehouse.py`
- **Schedule:** Event-driven — triggers automatically when `ECOMMERCE_RAW` signal received
- **Tasks:**
  1. `enrich_product_tags` — Ollama LLM enriches new product tags
  2. `dbt_run` — runs all 7 dbt models in dependency order
  3. `dbt_test` — runs data quality tests
  4. `log_completion` — logs pipeline completion

### Git-Sync Deployment Architecture

```
 ┌─────────────────────────────┐
 │  1. DEVELOPER (Windows)     │  Writes DAG code in VS Code
 └─────────────────────────────┘
                │
                │  git push origin main
                ▼
 ┌─────────────────────────────┐
 │  2. GITHUB REPOSITORY       │  Source of truth in the cloud
 └─────────────────────────────┘
                │
                │  WSL2 sync script pulls every 5 minutes
                ▼
 ┌─────────────────────────────┐
 │  3. WSL2 REPO FOLDER        │  ~/airflow/dags_repo/airflow/dags
 └─────────────────────────────┘
                │
                │  Airflow scheduler scans folder automatically
                ▼
 ┌─────────────────────────────┐
 │  4. AIRFLOW DASHBOARD       │  localhost:8080 — live DAG updates
 └─────────────────────────────┘
```

> DAG files are automatically synced from GitHub to Airflow every 5 minutes — simulating a CI/CD deployment pipeline where pushing to `main` automatically deploys to the Airflow environment.

---

## 🤖 LLM-Powered Product Tag Enrichment

Products in DummyJSON have a `tags` array (e.g. `["beauty", "mascara"]`). A custom Python script uses **Ollama (gemma2:2b)** — a locally hosted open-source LLM — to intelligently classify the most specific and meaningful tag for each product.

**Why local LLM:**
- ✅ Completely free — no API costs or rate limits
- ✅ Data never leaves the machine
- ✅ Demonstrates MLOps and LLM integration awareness

**Incremental processing:**
Uses a FULL OUTER JOIN to detect only NEW products not yet enriched — avoiding redundant LLM calls on every pipeline run.

**Output:** Written to `post_ingest_ecommerce.stg_product_tag_enriched` and joined in dbt intermediate layer.

---

## 🗂️ dbt Models

```
ecommerce_pipeline/models/
├── staging/                    → post_ingest_ecommerce (views)
│   ├── stg_products.sql        clean + rename + extract dimensions + join LLM tags
│   ├── stg_users.sql           flatten nested JSON address + company fields
│   ├── stg_carts.sql           cart-level summary fields
│   ├── stg_orders.sql          explode nested products array using UNNEST()
│   └── stg_categories.sql      category lookup table
│
├── intermediate/               → hub_ecommerce (views)
│   └── int_orders_enriched.sql join all staging tables into universal SSoT table
│
└── marts/                      → warehouse_ecommerce (tables)
    └── fct_orders.sql          final business-ready fact table (800 rows)
```

**Key dbt techniques:**
- `JSON_QUERY_ARRAY()` + `UNNEST()` for nested JSON array flattening
- `JSON_VALUE()` for extracting nested struct/JSON fields
- Custom `generate_schema_name` macro to prevent schema name duplication
- Multi-layer architecture with clear separation of concerns
- Source definitions with `sources.yml`

---

## 📁 Repository Structure

```
ecommerce-analytics-pipeline/
├── README.md                          ← you are here
├── .gitignore
├── .env.example
│
├── docs/
│   └── api/
│       └── dummyjson_ecommerce.postman_collection.json
│
├── airbyte/
│   └── dummyjson_connector.yaml       ← custom Airbyte connector
│
├── airflow/
│   └── dags/
│       ├── README.md                  ← Airflow deployment guide
│       ├── job__day__ecommerce__ingestion.py
│       └── job__day__ecommerce__hub__warehouse.py
│
├── ecommerce_pipeline/                ← dbt project root
│   ├── dbt_project.yml
│   ├── macros/
│   │   └── generate_schema_name.sql
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── ingestion/
│       ├── enrich_product_tags.py
│       ├── requirements.txt
│       └── archive/
│           └── enrich_product_tags_gemini_v1.py
│
└── streamlit/                         ← AI agent (coming soon)
```

---

## 🚀 Setup Guide

### Prerequisites
- Python 3.11
- Google Cloud account (BigQuery free tier)
- Docker Desktop
- Ollama (`https://ollama.com`)
- Apache Airflow 2.9.0 (WSL2/Ubuntu)
- dbt-bigquery

### 1. Clone the repository
```bash
git clone https://github.com/ahleebaba/ecommerce-analytics-pipeline.git
cd ecommerce-analytics-pipeline
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Fill in GEMINI_API_KEY and GOOGLE_APPLICATION_CREDENTIALS
```

### 3. Set up Google Cloud + BigQuery
- Create a GCP project
- Enable BigQuery API
- Create service account with BigQuery Admin + Storage Admin roles
- Download credentials JSON → save as `gcp_credentials.json`
- Create 4 datasets in `asia-southeast1`:
  - `ingest_ecommerce`
  - `post_ingest_ecommerce`
  - `hub_ecommerce`
  - `warehouse_ecommerce`

### 4. Set up Airbyte
```bash
# Install abctl
curl -LsfS https://get.airbyte.com | bash
abctl local install
```
- Import `airbyte/dummyjson_connector.yaml` in Connector Builder
- Set up BigQuery destination
- Create connection — sync mode: `Full Refresh | Overwrite`
- Set schedule to `Manual` (Airflow controls scheduling)

### 5. Set up dbt
```bash
pip install dbt-bigquery
cd ecommerce_pipeline
dbt debug    # verify BigQuery connection
dbt run      # run all 7 models
dbt test     # run data quality tests
```

### 6. Run LLM tag enrichment
```bash
# Install Ollama from https://ollama.com
ollama pull gemma2:2b
pip install ollama google-cloud-bigquery python-dotenv
python ecommerce_pipeline/ingestion/enrich_product_tags.py
```

### 7. Set up Airflow (WSL2)
```bash
python3.11 -m venv ~/airflow/airflow_env
source ~/airflow/airflow_env/bin/activate
pip install "apache-airflow==2.9.0" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.0/constraints-3.11.txt"
export AIRFLOW_HOME=~/airflow
airflow db init
airflow users create --username admin --password admin \
  --firstname Lee --lastname JunYan --role Admin \
  --email leejunyan16@gmail.com
airflow webserver --port 8080 -D
airflow scheduler -D
```

Set Airflow Variables (Admin → Variables):
| Key | Value |
|---|---|
| `airbyte_host` | your Airbyte VM IP |
| `airbyte_connection_id` | your Airbyte connection UUID |
| `airbyte_basic_auth` | base64 encoded `email:password` |

### 8. Set up Git-Sync
```bash
cd ~/airflow
git clone https://YOUR_PAT@github.com/ahleebaba/ecommerce-analytics-pipeline.git dags_repo
nano ~/airflow/sync_dags.sh
# Add sync script content
chmod +x ~/airflow/sync_dags.sh
nohup ~/airflow/sync_dags.sh > ~/airflow/sync.log 2>&1 &
```

---

## ⚠️ Engineering Decisions & Lessons Learned

### Airbyte OSS on Windows/GCP VM
Airbyte OSS (`abctl`) was tested on both Windows WSL2 and GCP Ubuntu VM (e2-standard-2, 8GB RAM, 50GB disk). Both encountered a known bug in Airbyte 2.1.0 where replication pods receive 0 memory allocation in STDIO-based Kubernetes deployments. Airbyte Cloud (30-day trial) was used as a managed alternative for the initial data load, before successfully deploying Airbyte OSS on a fresh GCP VM.

### Full Refresh vs Incremental Sync
DummyJSON is a static API with no timestamp fields — `Full Refresh | Overwrite` was chosen as the sync mode. In a production pipeline with a real database source, Incremental sync with a cursor field (`updated_at`) would be implemented, with dbt handling deduplication and SCD2 logic.

### Local LLM vs Cloud API
Gemini API (free tier) was initially chosen for product tag enrichment but encountered quota exhaustion. Ollama with `gemma2:2b` was adopted as a fully local, free alternative — with the added benefit of keeping all data on-premise and eliminating API rate limits.

### Dataset-Aware Scheduling
Airflow DAGs use Dataset-Aware Scheduling (Airflow 2.4+) instead of time-based ExternalTaskSensors — eliminating fixed-time dependencies and ensuring the transformation DAG only runs after upstream ingestion is confirmed complete. This approach scales naturally to multiple ingestion sources.

### Single Fact Table Design
Rather than pre-aggregating into multiple mart tables, a single wide `fct_orders` table was designed so Tableau handles all aggregations natively — maximising dashboard flexibility while keeping the dbt layer simple and maintainable.

---

## 📈 Dashboard

> 🔗 [View live Tableau Public dashboard](#) ← coming soon

**Page 1 — Revenue Overview:**
- Total revenue, net revenue, discount savings KPIs
- Revenue by product category
- Top 10 products by revenue
- Discount impact analysis by brand

**Page 2 — Customer Analysis:**
- Customer demographics (age group, gender breakdown)
- Geographic distribution map by country/city
- Company and department spend analysis
- Average basket size and order value

---

## 🤖 AI Analytics Agent

> 🔗 [Launch Streamlit app](#) ← coming soon

A self-service analytics agent that:
- Accepts natural language business questions
- Generates BigQuery SQL automatically using an LLM
- Executes queries against `warehouse_ecommerce.fct_orders`
- Returns results with interactive visualisations

---

## 👤 Author

**Lee Jun Yan**
Analytics Engineer | 5+ years experience in data pipelines, dashboarding and FinOps

- 🔗 [LinkedIn](https://linkedin.com/in/leejunyan)
- 📧 leejunyan16@gmail.com
- 🐙 [GitHub](https://github.com/ahleebaba)

---

*All data is synthetic (DummyJSON) — no real personal data is used in this project.*