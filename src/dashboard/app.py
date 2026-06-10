from __future__ import annotations

import streamlit as st
import plotly.express as px

from dashboard.queries import (
    load_kpis,
    load_filings_by_form,
    load_top_companies,
    load_recent_filings,
    load_filings_timeline,
    load_companies,
    load_company_detail,
    load_company_filings,
)

# ==========================================================
# Page Config
# ==========================================================

st.set_page_config(
    page_title="SEC Filings Intelligence",
    page_icon="📈",
    layout="wide",
)

# ==========================================================
# Header
# ==========================================================

st.title("📈 SEC Filings Intelligence Dashboard")

st.markdown(
    """
Analytics platform built from SEC filings data.

**Tech Stack**
- Python
- DuckDB
- dbt
- Streamlit
- Plotly
"""
)

st.divider()

# ==========================================================
# Load Data
# ==========================================================

try:
    kpis = load_kpis()

    forms_df = load_filings_by_form()

    companies_summary_df = load_top_companies()

    recent_filings_df = load_recent_filings()

    timeline_df = load_filings_timeline()

    companies_df = load_companies()

except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

except Exception as exc:
    st.error(f"Unexpected error: {exc}")
    st.stop()

# ==========================================================
# Sidebar
# ==========================================================

st.sidebar.header("Filters")

selected_company_name = st.sidebar.selectbox(
    "Company",
    companies_df["company_name"].tolist(),
)

selected_cik = companies_df.loc[
    companies_df["company_name"] == selected_company_name,
    "cik",
].iloc[0]

# ==========================================================
# KPI Cards
# ==========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Companies",
    f"{kpis['total_companies']:,}",
)

col2.metric(
    "Filings",
    f"{kpis['total_filings']:,}",
)

col3.metric(
    "Companies With Filings",
    f"{kpis['total_companies_with_filings']:,}",
)

col4.metric(
    "Latest Filing",
    str(kpis["latest_filing_date"]),
)

st.divider()

# ==========================================================
# Charts
# ==========================================================

left, right = st.columns(2)

# ----------------------------------------------------------
# Filing Types
# ----------------------------------------------------------

with left:

    st.subheader("Most Common Filing Types")

    if not forms_df.empty:

        fig_forms = px.bar(
            forms_df.head(10),
            x="form",
            y="filings_count",
            text="filings_count",
            title="Top Filing Forms",
        )

        fig_forms.update_layout(
            xaxis_title="Form",
            yaxis_title="Number of Filings",
        )

        st.plotly_chart(
            fig_forms,
            use_container_width=True,
        )

    else:
        st.info("No filing forms available.")

# ----------------------------------------------------------
# Companies
# ----------------------------------------------------------

with right:

    st.subheader("Top Companies by Filing Volume")

    if not companies_summary_df.empty:

        fig_companies = px.bar(
            companies_summary_df.head(10),
            x="company_name",
            y="total_filings",
            text="total_filings",
            title="Top Companies",
        )

        fig_companies.update_layout(
            xaxis_title="Company",
            yaxis_title="Total Filings",
        )

        st.plotly_chart(
            fig_companies,
            use_container_width=True,
        )

    else:
        st.info("No company metrics available.")

st.divider()

# ==========================================================
# Timeline
# ==========================================================

st.subheader("Filings Timeline")

if not timeline_df.empty:

    fig_timeline = px.line(
        timeline_df,
        x="filing_date",
        y="filings",
        markers=True,
        title="Filings Over Time",
    )

    fig_timeline.update_layout(
        xaxis_title="Filing Date",
        yaxis_title="Number of Filings",
    )

    st.plotly_chart(
        fig_timeline,
        use_container_width=True,
    )

else:
    st.info("No timeline data available.")

st.divider()

# ==========================================================
# Insights
# ==========================================================

st.header("Insights")

if not companies_summary_df.empty:

    top_company = companies_summary_df.iloc[0]

    st.info(
        f"""
Most active company:

**{top_company['company_name']}**

Total filings: **{top_company['total_filings']}**
"""
    )

st.divider()

# ==========================================================
# Company Explorer
# ==========================================================

st.header("Company Explorer")

company_detail_df = load_company_detail(selected_cik)

if not company_detail_df.empty:

    st.subheader(selected_company_name)

    st.dataframe(
        company_detail_df,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.warning("Company details not found.")

st.divider()

# ==========================================================
# Company Filings
# ==========================================================

st.subheader("Company Filing History")

company_filings_df = load_company_filings(selected_cik)

if not company_filings_df.empty:

    st.dataframe(
        company_filings_df,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.warning("No filings found for selected company.")

st.divider()

# ==========================================================
# Recent Filings
# ==========================================================

st.header("Recent Filings")

st.dataframe(
    recent_filings_df,
    use_container_width=True,
    hide_index=True,
)

# ==========================================================
# Footer
# ==========================================================

st.divider()

st.caption(
    """
SEC Filings Intelligence Pipeline

Built with Python, DuckDB, dbt, Pytest and Streamlit.
"""
)