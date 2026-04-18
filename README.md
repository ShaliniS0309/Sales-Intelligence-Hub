# 📊 Sales Intelligence Hub

## Project Overview
A comprehensive Branch-Based Sales Management System that helps organizations track sales, manage payment collections, monitor pending amounts, and maintain structured financial records across multiple branches.

## Problem Statement
Organizations operating across multiple branches often face challenges in tracking sales, managing payment collections, monitoring pending amounts, and maintaining structured financial records. Manual tracking methods may result in data inconsistencies, duplicate entries, incorrect payment calculations, and lack of transparency in revenue sharing.

## Objectives
- Store branch-wise sales records
- Automatically calculate net sales
- Support split payment tracking
- Automatically update received and pending amounts using database triggers
- Provide an interactive Streamlit dashboard for Admin users

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend logic |
| MySQL | Database management |
| Streamlit | Web dashboard |
| Pandas | Data manipulation |
| Plotly | Interactive charts |
| MySQL Connector | Database connection |


## Database Tables

| Table | Records |
|-------|---------|
| branches | 8 |
| customer_sales | 1000 |
| payment_splits | 2011 |
| users | 9 |

## Key Features
- ✅ Generated Column: `pending_amount` auto-calculated
- ✅ Trigger: Auto-updates `received_amount` on payment
- ✅ Role-Based Access: Super Admin & Admin
- ✅ Split Payment Tracking

## Installation

```bash
# Install packages
pip install streamlit pandas mysql-connector-python plotly

# Run database (MySQL Workbench)
CREATE DATABASE sales_intelligence_hub;
# Run sales.sql script

# Run Jupyter notebook to load data
jupyter notebook sales.ipynb

# Run Streamlit app
streamlit run app.py
```

## 🔐 Login Credentials

| Username | Password | Role |
|----------|----------|------|
| superadmin | super123 | Super Admin |
| admin_chennai | admin123 | Admin |
| admin_bangalore | admin123 | Admin |
| admin_hyderabad | admin123 | Admin |
| admin_delhi | admin123 | Admin |
| admin_mumbai | admin123 | Admin |
| admin_pune | admin123 | Admin |
| admin_kolkata | admin123 | Admin |
| admin_ahmedabad | admin123 | Admin |

## ✨ Dashboard Features

- 📊 Real-time KPIs (Sales, Received, Pending)
- ➕ Add Sales & Payments
- 📋 Sales Reports with Filters
- 🔍 SQL Query Execution
- 📥 Export CSV

## 📈 Business Insights

| Metric | Value |
|--------|-------|
| Total Gross Sales | ₹36,768,000 |
| Collection Rate | 51.75% |
| Top Branch | Kolkata (₹5,101,000) |


## Project Files Structure
├── app.py              # Streamlit dashboard 
├── sales.ipynb         # Jupyter analysis 
├── sales.sql           # Database schema 
└── .csv               # Data files 


