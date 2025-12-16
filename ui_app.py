import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from sklearn.linear_model import LinearRegression

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Retail Forecasting Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
DATA_DIR = "aggregated_sales_data"

if not os.path.exists(DATA_DIR):
    st.error("aggregated_sales_data folder not found.")
    st.stop()

files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
if not files:
    st.error("No aggregated CSV files found. Run data aggregation first.")
    st.stop()

latest_file = sorted(files)[-1]
df = pd.read_csv(os.path.join(DATA_DIR, latest_file))

# ---- enforce consistent types (CRITICAL FIX)
df["store_id"] = df["store_id"].astype(str)
df["product_id"] = df["product_id"].astype(str)
df["week_start"] = pd.to_datetime(df["week_start"])

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Section",
    [
        "Overview",
        "Sales Analytics",
        "Demand Forecasting",
        "Price Optimization",
        "Data Explorer",
        "About"
    ]
)

st.sidebar.divider()
st.sidebar.subheader("Filters")

store_options = sorted(df["store_id"].unique())
product_options = sorted(df["product_id"].unique())

selected_stores = st.sidebar.multiselect(
    "Stores",
    options=store_options,
    default=store_options
)

selected_products = st.sidebar.multiselect(
    "Products",
    options=product_options,
    default=product_options
)

date_range = st.sidebar.date_input(
    "Date Range",
    [df["week_start"].min(), df["week_start"].max()]
)

# --------------------------------------------------
# APPLY FILTERS SAFELY
# --------------------------------------------------
filtered_df = df[
    (df["store_id"].isin(selected_stores)) &
    (df["product_id"].isin(selected_products)) &
    (df["week_start"] >= pd.to_datetime(date_range[0])) &
    (df["week_start"] <= pd.to_datetime(date_range[1]))
]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def forecast_demand(data, weeks=6):
    weekly = data.groupby("week_start")["sales"].sum().reset_index()
    weekly["t"] = np.arange(len(weekly))

    model = LinearRegression()
    model.fit(weekly[["t"]], weekly["sales"])

    future_t = np.arange(len(weekly), len(weekly) + weeks)
    future_X = pd.DataFrame(future_t, columns=["t"])
    future_sales = model.predict(future_X)

    future_dates = pd.date_range(
        weekly["week_start"].max(),
        periods=weeks + 1,
        freq="W"
    )[1:]

    forecast = pd.DataFrame({
        "week_start": future_dates,
        "forecast_sales": future_sales.astype(int)
    })

    return weekly, forecast


def simulate_price(base_sales, base_price, new_price, elasticity=-1.2):
    factor = (new_price / base_price) ** elasticity
    return int(base_sales * factor)

# ==================================================
# OVERVIEW
# ==================================================
if page == "Overview":
    st.title("Retail Performance Overview")

    total_units = int(filtered_df["sales"].sum())
    avg_weekly = int(filtered_df.groupby("week_start")["sales"].sum().mean())
    top_store = filtered_df.groupby("store_id")["sales"].sum().idxmax()
    top_product = filtered_df.groupby("product_id")["sales"].sum().idxmax()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Units Sold", total_units)
    c2.metric("Average Weekly Sales", avg_weekly)
    c3.metric("Top Store", top_store)
    c4.metric("Top Product", top_product)

    trend = filtered_df.groupby("week_start")["sales"].sum().reset_index()

    fig = px.line(
        trend,
        x="week_start",
        y="sales",
        title="Weekly Sales Trend",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# SALES ANALYTICS
# ==================================================
elif page == "Sales Analytics":
    st.title("Sales Analytics")

    col1, col2 = st.columns(2)

    store_sales = filtered_df.groupby("store_id")["sales"].sum().reset_index()
    product_sales = filtered_df.groupby("product_id")["sales"].sum().reset_index()

    with col1:
        fig1 = px.bar(
            store_sales,
            x="store_id",
            y="sales",
            title="Sales by Store",
            template="plotly_white"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            product_sales,
            x="product_id",
            y="sales",
            title="Sales by Product",
            template="plotly_white"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ==================================================
# DEMAND FORECASTING
# ==================================================
elif page == "Demand Forecasting":
    st.title("Demand Forecasting")

    weeks = st.slider("Forecast Horizon (weeks)", 4, 12, 6)

    hist, forecast = forecast_demand(filtered_df, weeks)

    fig = px.line(
        hist,
        x="week_start",
        y="sales",
        title="Historical and Forecasted Demand",
        template="plotly_white"
    )

    fig.add_scatter(
        x=forecast["week_start"],
        y=forecast["forecast_sales"],
        mode="lines+markers",
        name="Forecast"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# PRICE OPTIMIZATION
# ==================================================
elif page == "Price Optimization":
    st.title("Price Optimization Simulation")

    base_price = st.slider("Current Price", 50, 500, 100)
    new_price = st.slider("Proposed Price", 50, 500, 120)

    avg_sales = int(filtered_df["sales"].mean())
    predicted_sales = simulate_price(avg_sales, base_price, new_price)

    r1, r2, r3 = st.columns(3)
    r1.metric("Current Average Sales", avg_sales)
    r2.metric("Predicted Sales", predicted_sales)
    r3.metric(
        "Revenue Change",
        (predicted_sales * new_price) - (avg_sales * base_price)
    )

# ==================================================
# DATA EXPLORER
# ==================================================
elif page == "Data Explorer":
    st.title("Data Explorer")

    st.dataframe(filtered_df, use_container_width=True)

    st.download_button(
        "Download Filtered Data",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_sales_data.csv"
    )

# ==================================================
# ABOUT
# ==================================================
elif page == "About":
    st.title("About This Project")

    st.markdown("""
    This project represents a complete retail analytics platform,
    combining data aggregation, interactive analysis, demand forecasting,
    and pricing simulation.

    It is designed to resemble an internal analytics tool used by
    retail and data science teams.

    **Author:** Nhowmitha S  
    **Domain:** Artificial Intelligence & Data Science
    """)
