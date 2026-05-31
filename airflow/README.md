# 🛒 Ecommerce Analytics Pipeline

A robust, push-driven data engineering pipeline that orchestrates automated E-commerce ingestion and downstream cloud data warehouse transformations. Built using **Apache Airflow**, **WSL2 (Ubuntu 26.04 LTS)**, and synchronized automatically via cloud git tracking loops.

---

## 🏗️ How Airflow Reads Code From GitHub (Instead of Windows)

Airflow does not track your local Windows filesystem (`C:\Users\...`) at all. Instead, it reads from a localized Linux repository directory that updates on autopilot whenever you push new changes up to GitHub.

### 🔄 The Deployment Architecture Lifecycle

```text
 ┌─────────────────────────────┐
 │  1. DEVELOPER (Windows)     │  Writes code in VS Code (Windows host filesystem).
 └─────────────────────────────┘
                │
                │  git push origin main
                ▼
 ┌─────────────────────────────┐
 │  2. GITHUB REPOSITORY       │  Acts as the absolute source of truth in the cloud.
 └─────────────────────────────┘
                │
                │  WSL2 Cron Task connects over internet
                │  (git fetch origin && git reset --hard origin/main)
                ▼
 ┌─────────────────────────────┐
 │  3. WSL2 REPO FOLDER        │  Isolated Linux filesystem directory target:
 │   (~/airflow/dags_repo)     │  /home/lee_jun_yan/airflow/dags_repo/airflow/dags
 └─────────────────────────────┘
                │
                │  Airflow background scheduler scans folder automatically
                ▼
 ┌─────────────────────────────┐
 │  4. AIRFLOW DASHBOARD       │  Updates web console UI (localhost:8080)
 │      (Webserver Engine)     │  instantly with live code modifications.
 └─────────────────────────────┘
```

### ⚙️ Behind-the-Scenes Automation Breakdown
1. **The Disconnect:** Inside WSL2, your `~/airflow/airflow.cfg` configuration file has its target parameter set explicitly to track the Linux directory: `dags_folder = /home/lee_jun_yan/airflow/dags_repo/airflow/dags`. It is completely blind to your Windows folder.
2. **The Cloud Trigger Hook:** Whenever you commit and push updates from your Windows terminal, your code travels directly up to the GitHub cloud workspace servers.
3. **The 60-Second Linux Worker:** Inside WSL2, an automated background task manager daemon (`cron`) triggers your custom execution script (`~/airflow/sync_dags.sh`) every 60 seconds on a silent looping schedule.
4. **The Update:** The script forces your local WSL2 environment to reach out across the internet to GitHub, pull down the freshest commits, overwrite the local file trees, and strip away Windows line endings using `dos2unix`. Airflow detects the file modification and parses the updates instantly.

---

## 📅 Pipeline Workflows (DAGs)

The data movement pipeline is split into isolated modular phases:

### 1. Ingestion Pipeline (`ecommerce_ingestion`)
* **Source Script:** `airflow/dags/job__day__ecommerce__ingestion.py`
* **Schedule:** Daily at 05:00 SGT (`0 5 * * *`)
* **Responsibilities:** Triggers and monitors upstream **Airbyte** source execution synchronization tasks. 
* **Downstream Trigger:** Emits an Airflow Dataset signal payload wrapper (`ECOMMERCE_RAW`) upon successful task execution finish.

### 2. Transformation Pipeline (`ecommerce_transformation`)
* **Source Script:** `airflow/dags/job__day__ecommerce__hub__warehouse.py`
* **Schedule:** Event-driven (Dataset-triggered)
* **Responsibilities:** Wakes up automatically the exact second `ECOMMERCE_RAW` drops, running target analytics modeling and table compilation scripts inside **Google Cloud BigQuery**.

---

## 🛠️ Local Development & Deployment Workflow

To update your DAG paths or data processing functions, use the following operational workflow loop:

### 1. Make Changes on Windows
Open your project files on the Windows filesystem environment and perform code optimizations, updates, or comments.

### 2. Standardize Git Configurations (First Time Only)
To guarantee that Windows line endings (`CRLF`) do not break the Linux interpreter parsing blocks, ensure your local core properties are set:
```bash
git config --global autocrlf true
```

### 3. Deploy via Git Push
Save your code modifications and execute a git update from your Windows tracking terminal or VS Code layout:
```bash
git add .
git commit -m "feat: illustrate architecture integration workflows"
git push origin main
```

---

## 🎛️ Local Troubleshooting Reference

If a DAG gets hidden or stays trapped inside a cached metadata layout after a heavy syntax adjustment, execute a forced environment database reset inside your **WSL2 Terminal**:

```bash
# Enter your isolated operational environment
source ~/airflow/airflow_env/bin/activate

# Clear old metadata cache fragments
airflow db clean
airflow dags reserialize

# Cycle the daemons if a crash occurs
pkill -f "airflow scheduler"
pkill -f "airflow webserver"
airflow webserver --port 8080 -D
airflow scheduler -D
```
