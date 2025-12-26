import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from sklearn.linear_model import LinearRegression
import time

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Retail Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# GLOBAL CORPORATE STYLING (FIXED VISIBILITY)
# =====================================================
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #e5e7eb;
}

/* White cards */
.section, .kpi {
    background-color: #ffffff;
    color: #111827;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* KPI text */
.kpi h2 { color: #111827; margin: 0; }
.kpi h4 { color: #374151; margin-bottom: 4px; }
.kpi p  { color: #6b7280; margin: 0; }

/* Insight box */
.insight {
    background-color: #eef2ff;
    color: #111827;
    padding: 20px;
    border-radius: 14px;
}

/* Titles inside cards */
.section h2,
.insight h4 {
    color: #111827;
}

/* Sidebar fix */
[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================
DATA_DIR = "aggregated_sales_data"

if not os.path.exists(DATA_DIR):
    st.error("❌ aggregated_sales_data folder not found")
    st.stop()

files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
if not files:
    st.error("❌ No CSV files found")
    st.stop()

latest_file = sorted(files)[-1]

with st.spinner("Loading retail sales data..."):
    time.sleep(1)
    df = pd.read_csv(os.path.join(DATA_DIR, latest_file))

required_cols = {"week_start", "store_id", "product_id", "sales"}
if not required_cols.issubset(df.columns):
    st.error("CSV must contain week_start, store_id, product_id, sales")
    st.stop()

df["week_start"] = pd.to_datetime(df["week_start"])

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("📊 Controls")

page = st.sidebar.radio(
    "Navigation",
    [
        "📌 Executive Dashboard",
        "📈 Sales Analysis",
        "🔮 Demand Forecast",
        "💰 Pricing Impact",
        "📂 Data Explorer",
        "ℹ️ About"
    ]
)

st.sidebar.markdown("### Filters")

stores = sorted(df["store_id"].unique())
products = sorted(df["product_id"].unique())

selected_stores = st.sidebar.multiselect("Stores", stores, default=stores)
selected_products = st.sidebar.multiselect("Products", products, default=products)

date_range = st.sidebar.date_input(
    "Date Range",
    [df["week_start"].min(), df["week_start"].max()]
)

# =====================================================
# FILTER DATA
# =====================================================
filtered_df = df[
    (df["store_id"].isin(selected_stores)) &
    (df["product_id"].isin(selected_products)) &
    (df["week_start"] >= pd.to_datetime(date_range[0])) &
    (df["week_start"] <= pd.to_datetime(date_range[1]))
]

if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def linear_forecast(data, weeks):
    weekly = data.groupby("week_start")["sales"].sum().reset_index()
    weekly["t"] = np.arange(len(weekly))

    model = LinearRegression()
    model.fit(weekly[["t"]], weekly["sales"])

    future_t = pd.DataFrame({"t": np.arange(len(weekly), len(weekly) + weeks)})
    future_sales = model.predict(future_t)

    future_dates = pd.date_range(
        weekly["week_start"].max(), periods=weeks + 1, freq="W"
    )[1:]

    return weekly, pd.DataFrame({
        "week_start": future_dates,
        "forecasted_sales": future_sales.astype(int)
    })

# =====================================================
# 📌 EXECUTIVE DASHBOARD
# =====================================================
if page == "📌 Executive Dashboard":

    st.markdown("""
    <div class="section">
        <h2>Executive Summary</h2>
        <p>
        This dashboard provides a consolidated view of retail sales performance
        across stores and products to support data-driven decision-making.
        </p>
    </div>
    """, unsafe_allow_html=True)

    total_sales = int(filtered_df["sales"].sum())
    avg_weekly = int(filtered_df.groupby("week_start")["sales"].sum().mean())
    best_store = filtered_df.groupby("store_id")["sales"].sum().idxmax()
    best_product = filtered_df.groupby("product_id")["sales"].sum().idxmax()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi">
            <h4>Total Sales</h4>
            <h2>{total_sales}</h2>
            <p>Overall units sold</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi">
            <h4>Average Weekly Sales</h4>
            <h2>{avg_weekly}</h2>
            <p>Sales consistency</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi">
            <h4>Top Performing Store</h4>
            <h2>{best_store}</h2>
            <p>Highest contribution</p>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi">
            <h4>Top Product</h4>
            <h2>{best_product}</h2>
            <p>Highest demand</p>
        </div>
        """, unsafe_allow_html=True)

    trend = filtered_df.groupby("week_start")["sales"].sum().reset_index()

    fig = px.line(
        trend,
        x="week_start",
        y="sales",
        title="Overall Sales Trend",
        markers=True
    )
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    growth = ((trend["sales"].iloc[-1] - trend["sales"].iloc[0]) /
              trend["sales"].iloc[0]) * 100

    st.markdown(f"""
    <div class="insight">
        <h4>Key Insights</h4>
        <ul>
            <li>Sales changed by <b>{growth:.1f}%</b> during the selected period</li>
            <li><b>{best_store}</b> is the highest contributing store</li>
            <li><b>{best_product}</b> is the most demanded product</li>
        </ul>
        <h4>Recommended Actions</h4>
        <ul>
            <li>Increase inventory for high-performing products</li>
            <li>Replicate top store strategies across locations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 📈 SALES ANALYSIS
# =====================================================
elif page == "📈 Sales Analysis":
    st.header("Sales Performance Analysis")
    col1, col2 = st.columns(2)

    with col1:
        store_sales = filtered_df.groupby("store_id")["sales"].sum().reset_index()
        st.plotly_chart(px.bar(store_sales, x="store_id", y="sales"), use_container_width=True)

    with col2:
        product_sales = filtered_df.groupby("product_id")["sales"].sum().reset_index()
        st.plotly_chart(px.bar(product_sales, x="product_id", y="sales"), use_container_width=True)

# =====================================================
# 🔮 DEMAND FORECAST
# =====================================================
elif page == "🔮 Demand Forecast":
    st.header("Demand Forecasting")
    weeks = st.slider("Forecast Horizon (weeks)", 4, 12, 6)

    hist, future = linear_forecast(filtered_df, weeks)

    fig = px.line(hist, x="week_start", y="sales", title="Historical Sales")
    fig.add_scatter(x=future["week_start"], y=future["forecasted_sales"],
                    name="Forecast", mode="lines+markers")
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 💰 PRICING IMPACT
# =====================================================
elif page == "💰 Pricing Impact":
    st.header("Pricing Impact Simulation")

    base_price = st.slider("Current Price (₹)", 50, 500, 100)
    new_price = st.slider("Proposed Price (₹)", 50, 500, 120)

    avg_sales = int(filtered_df["sales"].mean())
    elasticity = -1.2
    predicted_sales = int(avg_sales * (new_price / base_price) ** elasticity)

    revenue_before = avg_sales * base_price
    revenue_after = predicted_sales * new_price

    c1, c2 = st.columns(2)
    c1.metric("Current Revenue", f"₹{revenue_before}")
    c2.metric("Projected Revenue", f"₹{revenue_after}",
              delta=f"₹{revenue_after - revenue_before}")

# =====================================================
# 📂 DATA EXPLORER
# =====================================================
elif page == "📂 Data Explorer":
    st.header("Data Explorer")

    cols = st.multiselect(
        "Select Columns",
        list(filtered_df.columns),
        default=list(filtered_df.columns)
    )

    st.dataframe(filtered_df[cols], use_container_width=True)

    st.download_button(
        "Download CSV",
        filtered_df.to_csv(index=False),
        "filtered_sales_data.csv",
        "text/csv"
    )

# =====================================================
# ℹ️ ABOUT
# =====================================================
elif page == "ℹ️ About":
    st.header("About This Dashboard")

    st.markdown("""
This corporate retail intelligence dashboard demonstrates:

• Executive-level KPIs  
• Sales trend analysis  
• Demand forecasting  
• Pricing impact simulation  

**Developed by:**  
**Nhowmitha S**  
Artificial Intelligence & Data Science
""")
