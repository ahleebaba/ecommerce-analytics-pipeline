"""
Product Tag Enrichment Script
Uses Ollama (local LLM - free) to identify the most specific/meaningful tag 
from each product's tag array, excluding generic category terms.

Reads from:  ingest_ecommerce.products (BigQuery)
Writes to:   post_ingest_ecommerce.product_tag_enriched (BigQuery)
"""

import json
import os
import ollama
from google.cloud import bigquery


# ── Config ──────────────────────────────────────────────────────
PROJECT_ID          = "ecommerce-analytics-495218"
INPUT_DATASET_ID    = "ingest_ecommerce"
OUTPUT_DATASET_ID   = "post_ingest_ecommerce"
SOURCE_TABLE        = "products"
OUTPUT_TABLE = "stg_product_tag_enriched"
CREDENTIALS_PATH    = r"C:\Users\Lee Jun Yan\OneDrive\Documents\ecommerce-analytics-pipeline\gcp_credentials.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

# ── Clients ──────────────────────────────────────────────────────
bq_client = bigquery.Client(project=PROJECT_ID)


def get_best_tag(title: str, category: str, tags: list) -> str:
    if not tags:
        return None
    if len(tags) == 1:
        return tags[0]

    prompt = f"""You are a product categorisation expert.
Given a product's details, identify the MOST SPECIFIC and MEANINGFUL tag.

Product: {title}
Category: {category}
Tags: {tags}

Rules:
- Pick the most specific tag describing what the product IS
- Avoid generic terms repeating the category
- Return ONLY the chosen tag, nothing else

Examples:
category=beauty, tags=["beauty","mascara"] → mascara
category=groceries, tags=["pet supplies","cat food"] → cat food
category=home-decoration, tags=["home decor","photo frame"] → photo frame"""

    response = ollama.chat(
        model="gemma2:2b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"].strip().lower()


def main():
    print("=" * 60)
    print("Product Tag Enrichment — Powered by Ollama (Local LLM)")
    print("=" * 60)
    print(f"Source:      {PROJECT_ID}.{INPUT_DATASET_ID}.{SOURCE_TABLE}")
    print(f"Destination: {PROJECT_ID}.{OUTPUT_DATASET_ID}.{OUTPUT_TABLE}")
    print("=" * 60)

    # ── Fetch products from BigQuery ─────────────────────────────
    print("\nFetching products from BigQuery...")

    query = f"""
        SELECT 
            p.id,
            p.title,
            p.category,
            p.tags
        FROM `{PROJECT_ID}.{OUTPUT_DATASET_ID}.{OUTPUT_TABLE}` e
        FULL OUTER JOIN `{PROJECT_ID}.{INPUT_DATASET_ID}.{SOURCE_TABLE}` p
            ON e.product_id = p.id
        WHERE e.product_tag IS NULL
        ORDER BY p.id
    """

        rows = list(bq_client.query(query).result())
        print(f"Found {len(rows)} products to enrich\n")

    results = []

    # ── Enrich each product ──────────────────────────────────────
    for i, row in enumerate(rows):
        product_id  = row["id"]
        title       = row["title"]
        category    = row["category"]
        tags_raw    = row["tags"]

        # Parse tags from JSON string if needed
        if isinstance(tags_raw, str):
            tags = json.loads(tags_raw)
        else:
            tags = list(tags_raw) if tags_raw else []

        print(f"[{i+1}/{len(rows)}] {title}")
        print(f"  category: {category} | tags: {tags}")

        best_tag = get_best_tag(title, category, tags)
        print(f"  → product_tag: {best_tag}")

        results.append({
            "product_id":   int(product_id),
            "product_tag":  best_tag
        })

    # ── Write results to BigQuery ────────────────────────────────
    print(f"\nWriting {len(results)} enriched tags to BigQuery...")

    schema = [
        bigquery.SchemaField("product_id",  "INTEGER"),
        bigquery.SchemaField("product_tag", "STRING"),
    ]

    table_ref   = f"{PROJECT_ID}.{OUTPUT_DATASET_ID}.{OUTPUT_TABLE}"
    job_config  = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition="WRITE_TRUNCATE"
    )

    job = bq_client.load_table_from_json(
        results,
        table_ref,
        job_config=job_config
    )
    job.result()

    # ── Summary ──────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"✅ Done! {len(results)} products enriched")
    print(f"   Saved to: {table_ref}")
    print(f"{'=' * 60}")

    print("\nFirst 5 results:")
    for r in results[:5]:
        print(f"  product_id={r['product_id']} | product_tag={r['product_tag']}")


if __name__ == "__main__":
    main()
