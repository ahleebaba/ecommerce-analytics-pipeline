# Streamlit AI Text-to-SQL Agent

This app lets you ask natural-language questions against the BigQuery mart
`warehouse_ecommerce.fct_orders`. It supports two LLM modes:

- `ollama`: local model inference for demos on your own machine.
- `google`: hosted Gemini inference on Vertex AI for deployed/public demos.

BigQuery handles dry runs and read-only query execution.

## Setup

1. Create a virtual environment with Python 3.11.
2. Install dependencies:

   ```powershell
   pip install -r requirements-ai-agent.txt
   ```

3. Copy `.env.example` to `.env` and adjust values if needed.
4. Authenticate to Google Cloud:

   ```powershell
   gcloud auth application-default login
   gcloud config set project ecommerce-analytics-495218
   ```

5. Make sure Ollama is running and the model is available:

   ```powershell
   ollama pull gemma2:2b
   ollama serve
   ```

6. Run the app:

   ```powershell
   streamlit run streamlit_app.py
   ```

## LLM Modes

### Local Ollama Mode

Use this when running the project on your own laptop:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:2b
```

This does not expose your local model to public users. It is best for portfolio
screenshots, local demos, and interview walkthroughs.

### Hosted Google Vertex AI Mode

Use this when deploying the Streamlit app somewhere public:

```env
LLM_PROVIDER=google
VERTEX_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash
```

This mode uses Google Application Default Credentials locally and the deployed
service account in Google Cloud. The service account needs permission to call
Vertex AI and read/query BigQuery.

Hosted Vertex AI mode usually costs money because Gemini is billed by usage.
Your GCP credits can cover this while they last. Keep prompts short, use a Flash
model for demos, set budgets/alerts, and monitor billing.

## Guardrails

- Generated SQL must start with `SELECT` or `WITH`.
- Mutating SQL keywords such as `DROP`, `DELETE`, `UPDATE`, and `INSERT` are blocked.
- Only one SQL statement is allowed.
- Queries must reference the configured mart table.
- A default `LIMIT` is added when the model does not include one.

## Suggested Portfolio Demo Questions

- What are monthly gross revenue, net revenue, and discount savings?
- Which product categories generate the most net revenue?
- Who are the top 10 customers by net revenue?
- What is average order value by customer gender?
- Which products have the highest discount amount?
