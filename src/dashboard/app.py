from __future__ import annotations

import streamlit as st
import plotly.express as px

from dashboard.queries import (
    load_company_detail,
    load_company_filings,
    load_companies,
    load_filings_by_form,
    load_filings_timeline,
    load_kpis,
    load_pipeline_metrics,
    load_recent_filings,
    load_sic_summary,
    load_top_companies,
    load_execution_history,
    load_data_quality,
)

st.set_page_config(
    page_title="SEC Filings Intelligence",
    page_icon="📈",
    layout="wide",
)

st.title("📈 SEC Filings Intelligence Dashboard")
st.caption(
    "End-to-end Data Engineering pipeline powered by Python, DuckDB, dbt, Airflow and Streamlit."
)

try:
    kpis = load_kpis()
    pipeline_metrics_df = load_pipeline_metrics()
    forms_df = load_filings_by_form()
    top_companies_df = load_top_companies()
    recent_filings_df = load_recent_filings(10)
    timeline_df = load_filings_timeline()
    companies_df = load_companies()
    sic_df = load_sic_summary()
    execution_history_df = load_execution_history()
    data_quality_df = load_data_quality()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()
except Exception as exc:
    st.error(f"Unexpected error: {exc}")
    st.stop()

if companies_df.empty:
    st.warning("No companies found in the Gold layer.")
    st.stop()

st.sidebar.header("Filters")
selected_company_name = st.sidebar.selectbox(
    "Company",
    companies_df["company_name"].tolist(),
)

selected_cik = companies_df.loc[
    companies_df["company_name"] == selected_company_name,
    "cik",
].iloc[0]

st.header("⚙️ Pipeline Health")

if not pipeline_metrics_df.empty:

    latest_metrics = pipeline_metrics_df.iloc[0]

    p1, p2, p3 = st.columns(3)

    p1.metric(
        "Companies Processed",
        f"{latest_metrics['total_companies']:,}"
    )

    p2.metric(
        "Filings Processed",
        f"{latest_metrics['total_filings']:,}"
    )

    p3.metric(
        "Active Companies",
        f"{latest_metrics['companies_with_activity']:,}"
    )

    st.caption(
        f"Last Pipeline Execution: {latest_metrics['execution_timestamp']}"
    )

st.subheader("Execution History")

if not execution_history_df.empty:

    fig_pipeline = px.line(
        execution_history_df,
        x="execution_timestamp",
        y="total_filings",
        markers=True,
        title="Pipeline Growth Over Time"
    )

    st.plotly_chart(
        fig_pipeline,
        use_container_width=True
    )

if len(execution_history_df) >= 2:

    current = execution_history_df.iloc[-1]
    previous = execution_history_df.iloc[-2]

    growth = (
        current["total_filings"]
        - previous["total_filings"]
    )

    st.metric(
        "New Filings Since Last Run",
        growth
    )


st.divider()

st.header("Data Quality")
if not data_quality_df.empty:

    dq = data_quality_df.iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Quality Score",
        f"{dq['quality_score']}%"
    )

    c2.metric(
        "Null CIK",
        int(dq["null_cik"])
    )

    c3.metric(
        "Null Forms",
        int(dq["null_form"])
    )

    c4.metric(
        "Duplicate Filings",
        int(dq["duplicate_filings"])
    )

st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Companies", f"{kpis['total_companies']:,}")
col2.metric("Companies With Filings", f"{kpis['companies_with_filings']:,}")
col3.metric("Total Filings", f"{kpis['total_filings']:,}")
col4.metric("Latest Filing Date", str(kpis["latest_filing_date"]))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Filing Trends")
    if not timeline_df.empty:
        fig_timeline = px.line(
            timeline_df,
            x="filing_month",
            y="total_filings",
            markers=True,
            title="Filings Over Time",
        )
        fig_timeline.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Filings",
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No filing trend data available.")

with right:
    st.subheader("Form Distribution")
    if not forms_df.empty:
        fig_forms = px.bar(
            forms_df.head(10),
            x="form",
            y="total_filings",
            text="total_filings",
            title="Top Filing Forms",
        )
        fig_forms.update_layout(
            xaxis_title="Form",
            yaxis_title="Total Filings",
        )
        st.plotly_chart(fig_forms, use_container_width=True)
    else:
        st.info("No form distribution available.")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Top Companies")
    if not top_companies_df.empty:
        fig_companies = px.bar(
            top_companies_df.head(10).sort_values("total_filings"),
            x="total_filings",
            y="company_name",
            orientation="h",
            text="total_filings",
            title="Companies With Most Filings",
        )
        fig_companies.update_layout(
            xaxis_title="Total Filings",
            yaxis_title="Company",
        )
        st.plotly_chart(fig_companies, use_container_width=True)
    else:
        st.info("No company activity data available.")

with right:
    st.subheader("SIC Summary")
    if not sic_df.empty:
        fig_sic = px.bar(
            sic_df.head(10).sort_values("total_filings"),
            x="total_filings",
            y="sic_description",
            orientation="h",
            text="total_filings",
            title="Top SIC Segments",
        )
        fig_sic.update_layout(
            xaxis_title="Total Filings",
            yaxis_title="SIC Description",
        )
        st.plotly_chart(fig_sic, use_container_width=True)
    else:
        st.info("No SIC summary available.")

st.divider()

st.header("Company Explorer")

company_detail_df = load_company_detail(selected_cik)
company_filings_df = load_company_filings(selected_cik)

st.subheader(selected_company_name)
st.dataframe(company_detail_df, use_container_width=True, hide_index=True)

st.subheader("Company Filing History")
st.dataframe(company_filings_df, use_container_width=True, hide_index=True)

st.divider()

st.header("Recent Filings")
st.dataframe(recent_filings_df, use_container_width=True, hide_index=True)

st.divider()

st.caption("SEC Filings Intelligence Pipeline | Python • DuckDB • dbt • Airflow • Streamlit")