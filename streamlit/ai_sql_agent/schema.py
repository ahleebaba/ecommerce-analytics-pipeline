"""Schema context supplied to the local LLM."""

from __future__ import annotations

from ai_sql_agent.config import AppConfig


FCT_ORDERS_COLUMNS = [
    ("order_id", "STRING/INTEGER", "Unique order identifier."),
    ("order_date", "DATE/TIMESTAMP", "Date the order was placed."),
    ("customer_id", "STRING/INTEGER", "Unique customer identifier."),
    ("customer_first_name", "STRING", "Customer first name, if available."),
    ("customer_last_name", "STRING", "Customer last name, if available."),
    ("customer_email", "STRING", "Customer email, if available."),
    ("customer_age", "INTEGER", "Customer age."),
    ("customer_gender", "STRING", "Customer gender."),
    ("customer_city", "STRING", "Customer city."),
    ("customer_state", "STRING", "Customer state or region."),
    ("customer_country", "STRING", "Customer country."),
    ("product_id", "STRING/INTEGER", "Unique product identifier."),
    ("product_title", "STRING", "Product name/title."),
    ("product_brand", "STRING", "Product brand."),
    ("product_category", "STRING", "Product category."),
    ("quantity", "INTEGER", "Units sold."),
    ("unit_price", "NUMERIC/FLOAT", "Listed unit price before discount."),
    ("discount_percentage", "NUMERIC/FLOAT", "Discount percentage applied."),
    ("gross_revenue", "NUMERIC/FLOAT", "Revenue before discount."),
    ("discount_amount", "NUMERIC/FLOAT", "Absolute discount savings."),
    ("net_revenue", "NUMERIC/FLOAT", "Revenue after discount."),
]


def build_schema_context(config: AppConfig) -> str:
    """Return compact BigQuery table context for prompt grounding."""

    columns = "\n".join(
        f"- {name} ({data_type}): {description}"
        for name, data_type, description in FCT_ORDERS_COLUMNS
    )
    return f"""BigQuery table:
{config.fq_table}

Known columns:
{columns}

Business definitions:
- Gross revenue is revenue before discounts.
- Net revenue is revenue after discounts.
- Discount savings are represented by discount_amount.
- Use COUNT(DISTINCT order_id) for total orders unless the user asks for rows.
- Use COUNT(DISTINCT customer_id) for unique customers.
- Prefer product_category for category analysis and product_title for product analysis.
- Prefer DATE(order_date) when grouping by day, and DATE_TRUNC(DATE(order_date), MONTH) when grouping by month.
"""

