"""
Anomaly Detection using IQR method on daily sales.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from components.charts import apply_layout


def detect_anomalies(df: pd.DataFrame, iqr_multiplier: float = 1.5) -> pd.DataFrame:
    """Detect anomalies in daily revenue using IQR method."""
    daily = df.groupby("Date")["Revenue"].sum().reset_index()
    daily = daily.sort_values("Date")

    # Rolling statistics (30-day window)
    daily["MA30"] = daily["Revenue"].rolling(30, min_periods=7).mean()
    daily["Residual"] = daily["Revenue"] - daily["MA30"]

    Q1 = daily["Residual"].quantile(0.25)
    Q3 = daily["Residual"].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - iqr_multiplier * IQR
    upper_bound = Q3 + iqr_multiplier * IQR

    daily["IsAnomaly"] = (daily["Residual"] < lower_bound) | (daily["Residual"] > upper_bound)
    daily["AnomalyType"] = "Normal"
    daily.loc[daily["Residual"] > upper_bound, "AnomalyType"] = "Spike"
    daily.loc[daily["Residual"] < lower_bound, "AnomalyType"] = "Drop"

    return daily


def anomaly_chart(daily: pd.DataFrame) -> go.Figure:
    """Create anomaly visualization chart."""
    fig = go.Figure()

    # Normal points
    normal = daily[~daily["IsAnomaly"]]
    fig.add_trace(go.Scatter(
        x=normal["Date"], y=normal["Revenue"],
        name="Normal",
        mode="markers",
        marker=dict(size=4, color="#6366f1", opacity=0.4),
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    ))

    # Moving average
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["MA30"],
        name="30-Day Average",
        mode="lines",
        line=dict(color="#94a3b8", width=2, dash="dot"),
    ))

    # Spikes
    spikes = daily[daily["AnomalyType"] == "Spike"]
    fig.add_trace(go.Scatter(
        x=spikes["Date"], y=spikes["Revenue"],
        name="⚡ Spike",
        mode="markers",
        marker=dict(
            size=12, color="#f59e0b", symbol="triangle-up",
            line=dict(width=2, color="#fbbf24"),
        ),
        hovertemplate="<b>🔺 SPIKE</b><br>%{x|%b %d, %Y}<br>Revenue: $%{y:,.0f}<extra></extra>",
    ))

    # Drops
    drops = daily[daily["AnomalyType"] == "Drop"]
    fig.add_trace(go.Scatter(
        x=drops["Date"], y=drops["Revenue"],
        name="📉 Drop",
        mode="markers",
        marker=dict(
            size=12, color="#ef4444", symbol="triangle-down",
            line=dict(width=2, color="#f87171"),
        ),
        hovertemplate="<b>🔻 DROP</b><br>%{x|%b %d, %Y}<br>Revenue: $%{y:,.0f}<extra></extra>",
    ))

    return apply_layout(fig, "🚨 Anomaly Detection — Sales Outliers", height=480)


def render_anomaly_detection(df: pd.DataFrame):
    """Render the complete anomaly detection section."""
    st.markdown("""
    <div class="section-header">
        <h3>🚨 Anomaly Detection</h3>
        <p class="section-subtitle">IQR-based detection of unusual sales spikes and drops</p>
    </div>
    """, unsafe_allow_html=True)

    iqr_mult = st.slider("Sensitivity (IQR Multiplier)", 1.0, 3.0, 1.5, 0.1,
                          help="Lower = more sensitive (more anomalies), Higher = less sensitive",
                          key="iqr_mult")

    daily = detect_anomalies(df, iqr_multiplier=iqr_mult)

    # Summary metrics
    n_spikes = len(daily[daily["AnomalyType"] == "Spike"])
    n_drops = len(daily[daily["AnomalyType"] == "Drop"])
    anomaly_pct = (daily["IsAnomaly"].sum() / len(daily) * 100)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">⚡ Spikes Detected</p>
            <p class="metric-value" style="color: #f59e0b;">{n_spikes}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">📉 Drops Detected</p>
            <p class="metric-value" style="color: #ef4444;">{n_drops}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">📊 Anomaly Rate</p>
            <p class="metric-value">{anomaly_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    # Chart
    fig = anomaly_chart(daily)
    st.plotly_chart(fig, use_container_width=True)

    # Anomaly details table
    anomalies = daily[daily["IsAnomaly"]].sort_values("Date", ascending=False).head(20)
    if len(anomalies) > 0:
        st.markdown("#### 📋 Recent Anomalies")
        display_df = anomalies[["Date", "Revenue", "MA30", "AnomalyType"]].copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%b %d, %Y")
        display_df["Revenue"] = display_df["Revenue"].apply(lambda x: f"${x:,.0f}")
        display_df["MA30"] = display_df["MA30"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
        display_df.columns = ["Date", "Revenue", "30-Day Avg", "Type"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No anomalies detected with current sensitivity settings.")
