"""
Sales Data Analysis Dashboard
================================
A professional, futuristic Streamlit dashboard with dark theme,
glassmorphism UI, ML-powered analytics, and smart insights.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# ── Page Configuration (MUST be first Streamlit command) ──────────────────
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Add project root to path ─────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_loader import load_data, add_features, get_summary_stats
from utils.helpers import format_currency, format_number, get_greeting
from components.kpi_cards import render_kpi_cards
from components.charts import (
    sales_trend_chart, top_products_chart, category_pie_chart,
    region_heatmap, revenue_by_region_chart, quarterly_trend_chart,
    daily_sales_chart, customer_segment_chart, day_of_week_chart,
)
from components.filters import render_filters
from components.insights import render_insights, render_alerts
from ml.forecasting import render_forecasting
from ml.clustering import render_clustering
from ml.anomaly import render_anomaly_detection


# ── Load Custom CSS ───────────────────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# ── Load & Process Data ──────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_data():
    """Load and cache data."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "sales_data.csv")
    if not os.path.exists(data_path):
        from data.generate_data import generate_sales_data
        generate_sales_data(data_path)
    df = load_data(data_path)
    df = add_features(df)
    return df


df_raw = get_data()


# ── Sidebar ───────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0 5px;">
    <h1 style="font-size: 1.5rem; margin: 0;">
        <span style="background: linear-gradient(135deg, #6366f1, #a78bfa);
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                     background-clip: text;">📊 SalesIQ</span>
    </h1>
    <p style="color: #64748b; font-size: 0.75rem; margin: 4px 0 0;">Analytics Dashboard v2.0</p>
</div>
""", unsafe_allow_html=True)

# Role selection
st.sidebar.markdown("---")
role = st.sidebar.selectbox("👤 View Mode", ["Admin", "User"], key="role")

# File upload
st.sidebar.markdown("---")
st.sidebar.markdown('<p class="filter-label">📂 Data Source</p>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel", type=["csv", "xlsx", "xls"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
        from utils.data_loader import clean_data
        df_raw = clean_data(df_raw)
        df_raw = add_features(df_raw)
        st.sidebar.success(f"✅ Loaded {len(df_raw):,} rows")
    except Exception as e:
        st.sidebar.error(f"❌ Error: {e}")

# Filters
st.sidebar.markdown("---")
df = render_filters(df_raw)


# ── Dashboard Header ─────────────────────────────────────────────────────
role_class = "admin" if role == "Admin" else "user"
role_icon = "🔑" if role == "Admin" else "👁️"

st.markdown(f"""
<div class="dashboard-title">
    <h1>📊 Sales Analytics Dashboard</h1>
    <p>{get_greeting()} — Explore your sales performance with AI-powered insights</p>
    <span class="role-badge {role_class}">{role_icon} {role} Mode</span>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────
if role == "Admin":
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Overview", "📊 Analytics", "🤖 ML Insights", "📋 Reports"
    ])
else:
    tab1, tab2, tab4 = st.tabs([
        "🏠 Overview", "📊 Analytics", "📋 Reports"
    ])
    tab3 = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1: OVERVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    if len(df) == 0:
        st.warning("⚠️ No data matches the current filters. Adjust your filters in the sidebar.")
    else:
        # KPI Cards
        stats = get_summary_stats(df)
        render_kpi_cards(stats)

        st.markdown("<br>", unsafe_allow_html=True)

        # Alerts
        render_alerts(df)

        st.markdown("<br>", unsafe_allow_html=True)

        # Main charts row
        col_left, col_right = st.columns([2, 1])

        with col_left:
            fig_trend = sales_trend_chart(df)
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_right:
            fig_pie = category_pie_chart(df)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Second row
        col_a, col_b = st.columns(2)

        with col_a:
            fig_region = revenue_by_region_chart(df)
            st.plotly_chart(fig_region, use_container_width=True)

        with col_b:
            fig_products = top_products_chart(df, top_n=8)
            st.plotly_chart(fig_products, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Smart Insights
        render_insights(df)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2: ANALYTICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    if len(df) == 0:
        st.warning("⚠️ No data matches the current filters.")
    else:
        st.markdown("""
        <div class="section-header">
            <h3>📊 Deep-Dive Analytics</h3>
            <p class="section-subtitle">Detailed breakdowns across time, regions, and categories</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Quarterly performance
        fig_quarterly = quarterly_trend_chart(df)
        st.plotly_chart(fig_quarterly, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Daily sales + Day of week
        col1, col2 = st.columns([2, 1])

        with col1:
            fig_daily = daily_sales_chart(df)
            st.plotly_chart(fig_daily, use_container_width=True)

        with col2:
            fig_dow = day_of_week_chart(df)
            st.plotly_chart(fig_dow, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Heatmap + Customer segments
        col_a, col_b = st.columns(2)

        with col_a:
            fig_heat = region_heatmap(df)
            st.plotly_chart(fig_heat, use_container_width=True)

        with col_b:
            fig_seg = customer_segment_chart(df)
            st.plotly_chart(fig_seg, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Top Products full width
        fig_top = top_products_chart(df, top_n=15)
        st.plotly_chart(fig_top, use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3: ML INSIGHTS (Admin only)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if tab3 is not None:
    with tab3:
        if len(df) == 0:
            st.warning("⚠️ No data matches the current filters.")
        else:
            st.markdown("""
            <div class="section-header">
                <h3>🤖 Machine Learning Insights</h3>
                <p class="section-subtitle">AI-powered forecasting, segmentation, and anomaly detection</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ML Sub-tabs
            ml_tab1, ml_tab2, ml_tab3 = st.tabs([
                "🔮 Forecasting", "👥 Customer Segmentation", "🚨 Anomaly Detection"
            ])

            with ml_tab1:
                render_forecasting(df)

            with ml_tab2:
                render_clustering(df)

            with ml_tab3:
                render_anomaly_detection(df)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4: REPORTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    if len(df) == 0:
        st.warning("⚠️ No data matches the current filters.")
    else:
        st.markdown("""
        <div class="section-header">
            <h3>📋 Reports & Export</h3>
            <p class="section-subtitle">Download data and view summary statistics</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Summary statistics
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 Revenue Summary")
            if "Revenue" in df.columns:
                rev_stats = df["Revenue"].describe()
                st.dataframe(
                    pd.DataFrame({
                        "Metric": ["Count", "Mean", "Std Dev", "Min", "25%", "50%", "75%", "Max"],
                        "Value": [f"{v:,.2f}" for v in rev_stats.values]
                    }),
                    use_container_width=True, hide_index=True,
                )

        with col2:
            st.markdown("#### 💰 Profit Summary")
            if "Profit" in df.columns:
                prof_stats = df["Profit"].describe()
                st.dataframe(
                    pd.DataFrame({
                        "Metric": ["Count", "Mean", "Std Dev", "Min", "25%", "50%", "75%", "Max"],
                        "Value": [f"{v:,.2f}" for v in prof_stats.values]
                    }),
                    use_container_width=True, hide_index=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Top performers
        st.markdown("#### 🏆 Top Performers")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("**By Product**")
            top_prods = df.groupby("Product")["Revenue"].sum().nlargest(5).reset_index()
            top_prods["Revenue"] = top_prods["Revenue"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(top_prods, use_container_width=True, hide_index=True)

        with col_b:
            st.markdown("**By Region**")
            top_regions = df.groupby("Region")["Revenue"].sum().nlargest(5).reset_index()
            top_regions["Revenue"] = top_regions["Revenue"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(top_regions, use_container_width=True, hide_index=True)

        with col_c:
            st.markdown("**By Category**")
            top_cats = df.groupby("Category")["Revenue"].sum().nlargest(5).reset_index()
            top_cats["Revenue"] = top_cats["Revenue"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(top_cats, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Export section
        st.markdown("#### 💾 Export Data")

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv_data,
                file_name="sales_data_filtered.csv",
                mime="text/csv",
            )

        with col_d2:
            # Summary report
            summary_lines = []
            stats = get_summary_stats(df)
            summary_lines.append("SALES ANALYTICS REPORT")
            summary_lines.append("=" * 40)
            summary_lines.append(f"Total Revenue: {format_currency(stats['total_revenue'])}")
            summary_lines.append(f"Total Profit: {format_currency(stats['total_profit'])}")
            summary_lines.append(f"Total Orders: {format_number(stats['total_orders'])}")
            summary_lines.append(f"Profit Margin: {stats['avg_profit_margin']:.1f}%")
            summary_lines.append(f"Revenue Growth: {stats['revenue_growth']:.1f}%")
            summary_lines.append(f"\nDate Range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
            summary_lines.append(f"Records: {len(df):,}")

            summary_text = "\n".join(summary_lines)
            st.download_button(
                label="📥 Download Summary Report (TXT)",
                data=summary_text.encode("utf-8"),
                file_name="sales_summary_report.txt",
                mime="text/plain",
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Raw data preview
        with st.expander("🔍 Preview Raw Data", expanded=False):
            st.dataframe(df.head(100), use_container_width=True, hide_index=True)


# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 40px 0 20px; color: #475569; font-size: 0.8rem;">
    <p>Built with ❤️ using Streamlit • Sales Analytics Dashboard v2.0</p>
</div>
""", unsafe_allow_html=True)
