## AI Sales Analytics Copilot
An end-to-end Data Engineering project that combines modern data pipelines, cloud data warehousing, and local AI-powered analytics.
This project enables business users to ask questions in plain English such as:
-Show top 10 customers by sales
-Show top selling items
-Show monthly revenue.
The application automatically converts natural language into SQL, executes queries in Snowflake, and returns business-ready insights.

## Project Overview
The goal of this project is to demonstrate a complete modern data platform architecture:
-Data Ingestion
-ELT Processing
-Data Warehousing
-Dimensional Modeling
-Data Quality Monitoring
-AI-Powered Analytics
The project uses a local Large Language Model (LLM) through Ollama to generate SQL queries from user questions without relying on paid AI APIs.

## Architecture
MySQL
   ▼

Airbyte
   ▼

Snowflake RAW Layer
   ▼

Snowflake GOLD Layer
   ▼

Streamlit Application
   ▼

Ollama (Phi3 LLM)

## Technology Stack
-Data Engineering
-MySQL
-Airbyte
-Snowflake
-Data Modeling
-Star Schema
-Fact Tables
-Dimension Tables
-Analytics
-SQL
-Streamlit
-AI
-Ollama
-Phi3 LLM
-Python Libraries
-snowflake-connector-python
-streamlit
-requests
-pandas
-python-dotenv
-Source Data

The project uses sales data from:
Customer
Contains customer master information:
Customer Code
Customer Name
Address
Contact Information
Credit Limit
Invoice

Contains sales transactions:
Invoice Number
Invoice Date
Revenue
Balance
Status
Items

Contains product information:
Item Code
Item Name
Barcode
Packing

## Data Pipeline

# Step 1 – Data Extraction
Airbyte extracts data from MySQL tables:
customer
invoice1
invoice2
Features:
Incremental Loading
Schema Synchronization
Automated Data Replication

# Step 2 – Data Loading
Data is loaded into Snowflake RAW tables.
Purpose:
Preserve source system data
Maintain auditability
Enable downstream transformations

# Step 3 – Data Transformation
Snowflake transformations create a Gold Layer optimized for analytics.
Implemented:
-Data Cleansing
-Standardization
-Business Rules
-Aggregation Logic

# Dimensional Model
Fact Table
FACT_SALES
Stores transactional sales data.
-Measures:
Quantity
Net Amount
VAT Amount
Balance
-Attributes:
Customer
Item
Invoice
Status

# Dimension Tables
-DIM_CUSTOMER
Contains:
Customer Name
Customer Code
Terms
Credit Limit
-DIM_ITEM
Contains:
Item Name
Barcode
Packing

## AI Analytics Layer
A local LLM (Phi3 via Ollama) converts natural language into Snowflake SQL.
Example:
User Question
Show top 10 customers by sales
Generated SQL
SELECT
    CUSTOMER_NAME,
    SUM(NET_AMOUNT) AS TOTAL_SALES
FROM SALES_DW.GOLD.VW_AI_SALES_COPILOT
GROUP BY CUSTOMER_NAME
ORDER BY TOTAL_SALES DESC
LIMIT 10;
Result
Business users receive immediate answers without writing SQL.

## Application Features
Analytics Copilot
Natural language to SQL conversion.
Examples:
-Show top 10 customers by sales
-Show top 10 items by quantity
-Show monthly revenue
-Show sales by customer
-Data Quality Dashboard

Built-in data quality checks:
-Duplicate Invoices
-Negative Sales
-Missing Customer Records
-Data Dictionary

Automatically reads metadata from Snowflake.
Displays:
Table Name
Column Name
Data Type
