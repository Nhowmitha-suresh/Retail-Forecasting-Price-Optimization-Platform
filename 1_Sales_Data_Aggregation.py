##################################################
# 0. Imports
##################################################

import os
import csv
import pandas as pd
from datetime import datetime, timedelta
from pandas import json_normalize


##################################################
# 1. Paths (MATCH YOUR FOLDER)
##################################################

BASE_DIR = os.getcwd()

DATA_DIR = os.path.join(BASE_DIR, "Data Files")
OUTPUT_DIR = os.path.join(BASE_DIR, "aggregated_sales_data")

os.makedirs(OUTPUT_DIR, exist_ok=True)

products_d_loc = os.path.join(DATA_DIR, "products.csv")
stores_d_loc = os.path.join(DATA_DIR, "stores.csv")
processed_time_d_loc = os.path.join(DATA_DIR, "processed_time_df.csv")

sales_file = os.path.join(
    DATA_DIR, "sales_store1_2019_01_02_00_00_00.json"
)

price_file = os.path.join(
    DATA_DIR, "pc_store1_2019_04_02_00_00_00.json"
)


##################################################
# 2. Read processed time
##################################################

with open(processed_time_d_loc) as f:
    reader = csv.reader(f)
    rows = list(reader)

start_date = datetime.strptime(rows[1][0], "%Y-%m-%d").date()
end_date = datetime.strptime(rows[1][1], "%Y-%m-%d").date()


##################################################
# 3. Read products & stores
##################################################

df_products = pd.read_csv(products_d_loc)
df_stores = pd.read_csv(stores_d_loc)

df_products["ProductID"] = df_products["ProductID"].astype("category")
df_stores["StoreID"] = df_stores["StoreID"].astype("category")


##################################################
# 4. Read SALES JSON
##################################################

df_raw = pd.read_json(sales_file)

transactions = json_normalize(df_raw["Transactions"])
df_raw = df_raw.drop("Transactions", axis=1).join(transactions)

df_raw["TransactionDateTime"] = pd.to_datetime(df_raw["TransactionDateTime"])

sales_rows = []

for _, row in df_raw.iterrows():
    products = json_normalize(row["Products"])
    products["store_id"] = row["StoreID"]
    products["date_date"] = row["TransactionDateTime"]
    sales_rows.append(products)

df_sales = pd.concat(sales_rows, ignore_index=True)

df_sales = df_sales.rename(columns={"ProductID": "product_id"})
df_sales["product_id"] = df_sales["product_id"].astype("category")
df_sales["store_id"] = df_sales["store_id"].astype("category")


##################################################
# 5. Weekly aggregation
##################################################

df_sales["week_start"] = df_sales["date_date"].dt.date

df_sales = (
    df_sales.groupby(["week_start", "store_id", "product_id"])
    .size()
    .reset_index(name="sales")
)


##################################################
# 6. Read PRICE CHANGE JSON
##################################################

df_price = pd.read_json(price_file)

price_updates = json_normalize(df_price["PriceUpdates"])
df_price = df_price.drop("PriceUpdates", axis=1).join(price_updates)

df_price["week_start"] = pd.to_datetime(df_price["PriceDate"]).dt.date

df_price = df_price.rename(
    columns={
        "ProductID": "product_id",
        "StoreID": "store_id",
        "Price": "price",
    }
)


##################################################
# 7. Merge everything
##################################################

df_final = df_sales.merge(
    df_price,
    on=["week_start", "store_id", "product_id"],
    how="left"
)

df_final = df_final.merge(
    df_products, left_on="product_id", right_on="ProductID", how="left"
)

df_final = df_final.merge(
    df_stores, left_on="store_id", right_on="StoreID", how="left"
)


##################################################
# 8. Export
##################################################

output_file = os.path.join(
    OUTPUT_DIR, f"week_start_{start_date}.csv"
)

df_final.to_csv(output_file, index=False)

print("✅ Sales data aggregation completed successfully")
print("📁 File created:", output_file)
print("📊 Rows:", df_final.shape[0])
