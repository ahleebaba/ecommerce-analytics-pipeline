from __future__ import annotations

import pandas as pd
import streamlit as st
from dataclasses import replace
from dotenv import load_dotenv

from ai_sql_agent.bigquery_client import dry_run_query, run_query
from ai_sql_agent.config import load_config
from ai_sql_agent.llm import generate_sql, provider_label
from ai_sql_agent.sql_guard import SqlValidationError, validate_select_only


load_dotenv()

st.set_page_config(
    page_title="Ecommerce AI SQL Agent",
    page_icon=":bar_chart:",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
      --bg: #0F1623;
      --surface: #161E2E;
      --border: #2E3D5C;
      --primary: #4F8EF7;
      --positive: #34D399;
      --warning: #F59E0B;
      --alert: #F43F5E;
    }
    .stApp { background: var(--bg); color: #E5E7EB; }
    [data-testid="stSidebar"] { background: #111827; }
    div[data-testid="stMetric"] {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
    }
    div[data-testid="stDataFrame"] {
      border: 1px solid var(--border);
      border-radius: 8px;
    }
    .block-container { padding-top: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


config = load_config()

with st.sidebar:
    st.header("Connection")
    st.caption("Configured from environment variables")
    st.text_input("GCP project", value=config.gcp_project, disabled=True)
    st.text_input("Dataset", value=config.default_dataset, disabled=True)
    st.text_input("Table", value=config.default_table, disabled=True)
    st.text_input("LLM provider", value=config.llm_provider, disabled=True)
    st.text_input("LLM model", value=provider_label(config), disabled=True)
    st.divider()
    max_rows = st.number_input(
        "Max rows",
        min_value=10,
        max_value=5000,
        value=config.max_rows,
        step=10,
    )
    temperature = st.slider("LLM temperature", 0.0, 0.7, 0.0, 0.1)

config = replace(config, max_rows=int(max_rows))

st.title("Ecommerce AI Text-to-SQL Agent")
st.caption("Ask questions against BigQuery mart `warehouse_ecommerce.fct_orders`.")

example_questions = [
    "What are monthly gross revenue, net revenue, and discount savings?",
    "Which product categories generate the most net revenue?",
    "Who are the top 10 customers by net revenue?",
    "What is average order value by customer gender?",
    "Which products have the highest discount amount?",
]

question = st.text_area(
    "Question",
    value=example_questions[0],
    height=90,
    placeholder="Ask a business question about ecommerce orders...",
)

generate_clicked = st.button("Generate SQL", type="primary")

if "sql" not in st.session_state:
    st.session_state.sql = ""

if generate_clicked:
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        with st.spinner(f"Asking {provider_label(config)} to generate BigQuery SQL..."):
            try:
                generated_sql = generate_sql(question.strip(), config, temperature=temperature)
                st.session_state.sql = validate_select_only(generated_sql, config)
            except Exception as exc:
                st.error(f"SQL generation failed: {exc}")

st.text_area(
    "Generated SQL",
    key="sql",
    height=260,
    placeholder="Generated SQL will appear here.",
)

action_col1, action_col2, action_col3 = st.columns([1, 1, 4])

with action_col1:
    dry_run_clicked = st.button("Dry run")
with action_col2:
    run_clicked = st.button("Run query")

validated_sql = None
if dry_run_clicked or run_clicked:
    try:
        validated_sql = validate_select_only(st.session_state.sql, config)
        st.session_state.sql = validated_sql
    except SqlValidationError as exc:
        st.error(f"SQL blocked by guardrails: {exc}")

if dry_run_clicked and validated_sql:
    with st.spinner("Validating query in BigQuery..."):
        try:
            bytes_processed = dry_run_query(validated_sql, config)
            mb_processed = bytes_processed / 1024 / 1024
            st.success(f"Dry run passed. Estimated bytes processed: {mb_processed:,.2f} MB.")
        except Exception as exc:
            st.error(f"BigQuery dry run failed: {exc}")

if run_clicked and validated_sql:
    with st.spinner("Running query in BigQuery..."):
        try:
            result_df = run_query(validated_sql, config)
            st.success(f"Returned {len(result_df):,} rows.")

            metric_cols = st.columns(3)
            metric_cols[0].metric("Rows", f"{len(result_df):,}")
            metric_cols[1].metric("Columns", f"{len(result_df.columns):,}")
            metric_cols[2].metric("Max rows", f"{config.max_rows:,}")

            st.dataframe(result_df, use_container_width=True, hide_index=True)

            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv,
                file_name="ai_sql_agent_results.csv",
                mime="text/csv",
            )

            numeric_cols = result_df.select_dtypes(include="number").columns.tolist()
            date_cols = [
                col for col in result_df.columns if pd.api.types.is_datetime64_any_dtype(result_df[col])
            ]
            if numeric_cols and (date_cols or len(result_df.columns) >= 2):
                st.subheader("Quick chart")
                x_axis = date_cols[0] if date_cols else result_df.columns[0]
                y_axis = numeric_cols[0]
                chart_df = result_df.set_index(x_axis)[y_axis]
                st.line_chart(chart_df)
        except Exception as exc:
            st.error(f"BigQuery query failed: {exc}")

with st.expander("Try these questions"):
    for item in example_questions:
        st.code(item, language=None)
