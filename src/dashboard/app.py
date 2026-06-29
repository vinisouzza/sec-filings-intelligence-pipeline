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

# ── Translations ──────────────────────────────────────────────────────────────

TRANSLATIONS: dict[str, dict[str, str]] = {
    "English": {
        # Page
        "page_title": "SEC Filings Intelligence",
        "app_title": "📈 SEC Filings Intelligence Dashboard",
        "app_caption": (
            "End-to-end Data Engineering pipeline powered by "
            "Python, DuckDB, dbt, Airflow and Streamlit."
        ),
        # Sidebar
        "sidebar_header": "Filters",
        "sidebar_language": "Language",
        "sidebar_company": "Company",
        # Pipeline Health
        "section_pipeline": "⚙️ Pipeline Health",
        "metric_companies_processed": "Companies Processed",
        "metric_filings_processed": "Filings Processed",
        "metric_active_companies": "Active Companies",
        "last_execution": "Last Pipeline Execution",
        "subsection_exec_history": "Execution History",
        "chart_pipeline_growth": "Pipeline Growth Over Time",
        "metric_new_filings": "New Filings Since Last Run",
        # Data Quality
        "section_data_quality": "Data Quality",
        "metric_quality_score": "Quality Score",
        "metric_null_cik": "Null CIK",
        "metric_null_form": "Null Forms",
        "metric_duplicate": "Duplicate Filings",
        # KPIs
        "metric_companies": "Companies",
        "metric_companies_with_filings": "Companies With Filings",
        "metric_total_filings": "Total Filings",
        "metric_latest_date": "Latest Filing Date",
        # Charts
        "subsection_trends": "Filing Trends",
        "chart_filings_over_time": "Filings Over Time",
        "axis_month": "Month",
        "axis_total_filings": "Total Filings",
        "info_no_trend": "No filing trend data available.",
        "subsection_form_dist": "Form Distribution",
        "chart_top_forms": "Top Filing Forms",
        "axis_form": "Form",
        "info_no_form": "No form distribution available.",
        "subsection_top_companies": "Top Companies",
        "chart_most_filings": "Companies With Most Filings",
        "axis_company": "Company",
        "info_no_company": "No company activity data available.",
        "subsection_sic": "SIC Summary",
        "chart_top_sic": "Top SIC Segments",
        "axis_sic": "SIC Description",
        "info_no_sic": "No SIC summary available.",
        # Company Explorer
        "section_explorer": "Company Explorer",
        "subsection_filing_history": "Company Filing History",
        # Recent Filings
        "section_recent": "Recent Filings",
        # Footer
        "footer": "SEC Filings Intelligence Pipeline | Python • DuckDB • dbt • Airflow • Streamlit",
        # Errors / Warnings
        "warn_no_companies": "No companies found in the Gold layer.",
    },
    "Português": {
        # Page
        "page_title": "Inteligência de Registros SEC",
        "app_title": "📈 Dashboard de Inteligência de Registros SEC",
        "app_caption": (
            "Pipeline de Engenharia de Dados de ponta a ponta com "
            "Python, DuckDB, dbt, Airflow e Streamlit."
        ),
        # Sidebar
        "sidebar_header": "Filtros",
        "sidebar_language": "Idioma",
        "sidebar_company": "Empresa",
        # Pipeline Health
        "section_pipeline": "⚙️ Saúde do Pipeline",
        "metric_companies_processed": "Empresas Processadas",
        "metric_filings_processed": "Registros Processados",
        "metric_active_companies": "Empresas Ativas",
        "last_execution": "Última Execução do Pipeline",
        "subsection_exec_history": "Histórico de Execuções",
        "chart_pipeline_growth": "Crescimento do Pipeline ao Longo do Tempo",
        "metric_new_filings": "Novos Registros Desde a Última Execução",
        # Data Quality
        "section_data_quality": "Qualidade dos Dados",
        "metric_quality_score": "Pontuação de Qualidade",
        "metric_null_cik": "CIK Nulo",
        "metric_null_form": "Formulários Nulos",
        "metric_duplicate": "Registros Duplicados",
        # KPIs
        "metric_companies": "Empresas",
        "metric_companies_with_filings": "Empresas com Registros",
        "metric_total_filings": "Total de Registros",
        "metric_latest_date": "Data do Registro Mais Recente",
        # Charts
        "subsection_trends": "Tendências de Registros",
        "chart_filings_over_time": "Registros ao Longo do Tempo",
        "axis_month": "Mês",
        "axis_total_filings": "Total de Registros",
        "info_no_trend": "Nenhum dado de tendência disponível.",
        "subsection_form_dist": "Distribuição por Formulário",
        "chart_top_forms": "Principais Formulários",
        "axis_form": "Formulário",
        "info_no_form": "Nenhuma distribuição de formulário disponível.",
        "subsection_top_companies": "Principais Empresas",
        "chart_most_filings": "Empresas com Mais Registros",
        "axis_company": "Empresa",
        "info_no_company": "Nenhum dado de atividade de empresas disponível.",
        "subsection_sic": "Resumo SIC",
        "chart_top_sic": "Principais Segmentos SIC",
        "axis_sic": "Descrição SIC",
        "info_no_sic": "Nenhum resumo SIC disponível.",
        # Company Explorer
        "section_explorer": "Explorador de Empresas",
        "subsection_filing_history": "Histórico de Registros da Empresa",
        # Recent Filings
        "section_recent": "Registros Recentes",
        # Footer
        "footer": "Pipeline de Inteligência de Registros SEC | Python • DuckDB • dbt • Airflow • Streamlit",
        # Errors / Warnings
        "warn_no_companies": "Nenhuma empresa encontrada na camada Gold.",
    },
}

# ── Page config (must come before any other st call) ─────────────────────────

st.set_page_config(
    page_title="SEC Filings Intelligence",
    page_icon="📈",
    layout="wide",
)

# ── Language selector (sidebar – resolved before rendering) ──────────────────

st.sidebar.header("Filters / Filtros")

selected_language = st.sidebar.selectbox(
    "🌐 Language / Idioma",
    list(TRANSLATIONS.keys()),
    index=0,
)

T = TRANSLATIONS[selected_language]

# ── Data loading ─────────────────────────────────────────────────────────────

st.title(T["app_title"])
st.caption(T["app_caption"])

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
    st.warning(T["warn_no_companies"])
    st.stop()

# ── Sidebar – company filter ──────────────────────────────────────────────────

st.sidebar.header(T["sidebar_header"])
selected_company_name = st.sidebar.selectbox(
    T["sidebar_company"],
    companies_df["company_name"].tolist(),
)

selected_cik = companies_df.loc[
    companies_df["company_name"] == selected_company_name,
    "cik",
].iloc[0]

# ── Pipeline Health ───────────────────────────────────────────────────────────

st.header(T["section_pipeline"])

if not pipeline_metrics_df.empty:

    latest_metrics = pipeline_metrics_df.iloc[0]

    p1, p2, p3 = st.columns(3)

    p1.metric(
        T["metric_companies_processed"],
        f"{latest_metrics['total_companies']:,}"
    )

    p2.metric(
        T["metric_filings_processed"],
        f"{latest_metrics['total_filings']:,}"
    )

    p3.metric(
        T["metric_active_companies"],
        f"{latest_metrics['companies_with_activity']:,}"
    )

    st.caption(
        f"{T['last_execution']}: {latest_metrics['execution_timestamp']}"
    )

st.subheader(T["subsection_exec_history"])

if not execution_history_df.empty:

    fig_pipeline = px.line(
        execution_history_df,
        x="execution_timestamp",
        y="total_filings",
        markers=True,
        title=T["chart_pipeline_growth"],
    )

    st.plotly_chart(fig_pipeline, use_container_width=True)

if len(execution_history_df) >= 2:

    current = execution_history_df.iloc[-1]
    previous = execution_history_df.iloc[-2]

    growth = (
        current["total_filings"]
        - previous["total_filings"]
    )

    st.metric(T["metric_new_filings"], growth)

st.divider()

# ── Data Quality ──────────────────────────────────────────────────────────────

st.header(T["section_data_quality"])

if not data_quality_df.empty:

    dq = data_quality_df.iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(T["metric_quality_score"], f"{dq['quality_score']}%")
    c2.metric(T["metric_null_cik"], int(dq["null_cik"]))
    c3.metric(T["metric_null_form"], int(dq["null_form"]))
    c4.metric(T["metric_duplicate"], int(dq["duplicate_filings"]))

st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)

col1.metric(T["metric_companies"], f"{kpis['total_companies']:,}")
col2.metric(T["metric_companies_with_filings"], f"{kpis['companies_with_filings']:,}")
col3.metric(T["metric_total_filings"], f"{kpis['total_filings']:,}")
col4.metric(T["metric_latest_date"], str(kpis["latest_filing_date"]))

st.divider()

# ── Trends & Form Distribution ────────────────────────────────────────────────

left, right = st.columns(2)

with left:
    st.subheader(T["subsection_trends"])
    if not timeline_df.empty:
        fig_timeline = px.line(
            timeline_df,
            x="filing_month",
            y="total_filings",
            markers=True,
            title=T["chart_filings_over_time"],
        )
        fig_timeline.update_layout(
            xaxis_title=T["axis_month"],
            yaxis_title=T["axis_total_filings"],
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info(T["info_no_trend"])

with right:
    st.subheader(T["subsection_form_dist"])
    if not forms_df.empty:
        fig_forms = px.bar(
            forms_df.head(10),
            x="form",
            y="total_filings",
            text="total_filings",
            title=T["chart_top_forms"],
        )
        fig_forms.update_layout(
            xaxis_title=T["axis_form"],
            yaxis_title=T["axis_total_filings"],
        )
        st.plotly_chart(fig_forms, use_container_width=True)
    else:
        st.info(T["info_no_form"])

st.divider()

# ── Top Companies & SIC Summary ───────────────────────────────────────────────

left, right = st.columns(2)

with left:
    st.subheader(T["subsection_top_companies"])
    if not top_companies_df.empty:
        fig_companies = px.bar(
            top_companies_df.head(10).sort_values("total_filings"),
            x="total_filings",
            y="company_name",
            orientation="h",
            text="total_filings",
            title=T["chart_most_filings"],
        )
        fig_companies.update_layout(
            xaxis_title=T["axis_total_filings"],
            yaxis_title=T["axis_company"],
        )
        st.plotly_chart(fig_companies, use_container_width=True)
    else:
        st.info(T["info_no_company"])

with right:
    st.subheader(T["subsection_sic"])
    if not sic_df.empty:
        fig_sic = px.bar(
            sic_df.head(10).sort_values("total_filings"),
            x="total_filings",
            y="sic_description",
            orientation="h",
            text="total_filings",
            title=T["chart_top_sic"],
        )
        fig_sic.update_layout(
            xaxis_title=T["axis_total_filings"],
            yaxis_title=T["axis_sic"],
        )
        st.plotly_chart(fig_sic, use_container_width=True)
    else:
        st.info(T["info_no_sic"])

st.divider()

# ── Company Explorer ──────────────────────────────────────────────────────────

st.header(T["section_explorer"])

company_detail_df = load_company_detail(selected_cik)
company_filings_df = load_company_filings(selected_cik)

st.subheader(selected_company_name)
st.dataframe(company_detail_df, use_container_width=True, hide_index=True)

st.subheader(T["subsection_filing_history"])
st.dataframe(company_filings_df, use_container_width=True, hide_index=True)

st.divider()

# ── Recent Filings ────────────────────────────────────────────────────────────

st.header(T["section_recent"])
st.dataframe(recent_filings_df, use_container_width=True, hide_index=True)

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────

st.caption(T["footer"])