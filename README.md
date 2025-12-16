# Retail Forecasting & Price Optimization Platform

An end-to-end retail analytics platform that transforms raw transactional data into actionable business insights using data engineering, machine learning, and an interactive web-based dashboard.

This project simulates a real-world retail decision-support system used for sales analysis, demand forecasting, and pricing strategy evaluation.
<img width="1919" height="1078" alt="Screenshot 2025-12-16 203420" src="https://github.com/user-attachments/assets/fc67e7cc-632a-4670-92b9-ce761eeb065f" />
<img width="1912" height="1060" alt="Screenshot 2025-12-16 203433" src="https://github.com/user-attachments/assets/315cc6ba-4863-4bb4-af35-8243f7408acd" />
<img width="1919" height="1078" alt="Screenshot 2025-12-16 203443" src="https://github.com/user-attachments/assets/8f4ae1a8-7164-4027-a74e-4fd523d91083" />
<img width="1919" height="1058" alt="Screenshot 2025-12-16 203450" src="https://github.com/user-attachments/assets/be587c80-ea8a-41e3-a673-88de72665c62" />
<img width="1919" height="1062" alt="Screenshot 2025-12-16 203459" src="https://github.com/user-attachments/assets/3709de0e-80f2-401c-b6ce-9b5f2cb9041b" />
<img width="1919" height="1075" alt="Screenshot 2025-12-16 203508" src="https://github.com/user-attachments/assets/b6527835-07f7-49e2-b8e4-5260c8f6ce35" />



---


## 📌 Overview

Retail organizations rely on accurate demand forecasts and effective pricing strategies to optimize revenue, manage inventory, and support business planning.

This platform demonstrates how data-driven techniques can be applied to:
- Aggregate raw sales transactions
- Analyze sales performance across stores and products
- Forecast future demand using machine learning
- Simulate the impact of pricing changes on sales and revenue
- Present insights through a clean, professional dashboard

---

## 🚀 Key Features

- Sales data aggregation from raw JSON transaction logs  
- Interactive analytics dashboard with filters and KPIs  
- Weekly demand forecasting using machine learning models  
- Price optimization simulation using elasticity-based modeling  
- Advanced visualizations for trends and comparisons  
- Downloadable, filtered datasets for further analysis  
- Production-style project structure and enterprise-ready UI  

---

## 🏗️ System Architecture

1. **Data Ingestion**  
   Raw sales and pricing data are loaded from structured JSON files.

2. **Data Aggregation**  
   Transactions are aggregated at a weekly level by store and product.

3. **Analytics Layer**  
   Aggregated data is analyzed to compute KPIs and performance metrics.

4. **Machine Learning Layer**  
   A regression-based model is used to forecast future demand trends.

5. **Presentation Layer**  
   An interactive Streamlit dashboard enables business users to explore insights.

---

## 🧰 Tech Stack

- **Programming Language:** Python  
- **Data Processing:** Pandas, NumPy  
- **Machine Learning:** Scikit-learn  
- **Visualization:** Plotly  
- **Web Framework:** Streamlit  
- **Version Control:** Git & GitHub  

---

## 📁 Project Structure

```text
Retail-Forecasting-Price-Optimization-Platform/
│
├── Data Files/                     # Raw input data
├── aggregated_sales_data/          # Aggregated output data
├── 1_Sales_Data_Aggregation.py     # Data processing pipeline
├── ui_app.py                       # Streamlit dashboard
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation
└── screenshots/                    # Dashboard screenshots
