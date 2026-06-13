import os
os.makedirs(r"D:\AI_SALES_COPILOT\sf_tmp", exist_ok=True)
os.makedirs(r"D:\AI_SALES_COPILOT\sf_cache", exist_ok=True)

os.environ["TMP"] = r"D:\AI_SALES_COPILOT\sf_tmp"
os.environ["TEMP"] = r"D:\AI_SALES_COPILOT\sf_tmp"
os.environ["SF_OCSP_RESPONSE_CACHE_DIR"] = r"D:\AI_SALES_COPILOT\sf_cache"

import requests
import streamlit as st
import snowflake.connector
from dotenv import load_dotenv

st.set_page_config(page_title="AI Sales Copilot", layout="wide")

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"


def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        login_timeout=20,
        network_timeout=20
    )


st.write("Before Snowflake connection")

def run_sql(sql):

    st.write("Opening connection...")

    conn = get_connection()

    st.write("Connection opened")

    cur = conn.cursor()

    try:
        st.write("Executing SQL...")

        cur.execute(sql)

        st.write("Fetching data...")

        df = cur.fetch_pandas_all()

        st.write("Data fetched")

        return df

    finally:
        cur.close()
        conn.close()


def ask_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    return response.json()["response"].strip()


def generate_sql(question):
    prompt = f"""
You are a Snowflake SQL expert.

Generate ONLY SQL. No explanation. No markdown.

Table:
SALES_DW.GOLD.VW_AI_SALES_COPILOT

Columns:
INVOICE_ID, INVOICE_NO, INVOICE_DATE,
CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME,
ITEM_CODE, ITEM_NAME, QTY, UNIT_PRICE,
NET_AMOUNT, STATUS

Rules:
1. Return SQL only.
2. Use NET_AMOUNT as revenue.
3. Use GROUP BY when SUM() is used.
4. Limit to 20 rows.
5. SELECT only.

Question:
{question}
"""

    sql = ask_ollama(prompt)
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def get_template(question):
    q = question.lower()

    if "top 10 customer" in q or "top customer" in q:
        return """
SELECT
    CUSTOMER_NAME,
    SUM(NET_AMOUNT) AS TOTAL_SALES
FROM SALES_DW.GOLD.VW_AI_SALES_COPILOT
GROUP BY CUSTOMER_NAME
ORDER BY TOTAL_SALES DESC
LIMIT 10;
"""

    if "top 10 item" in q or "top item" in q:
        return """
SELECT
    ITEM_NAME,
    SUM(QTY) AS TOTAL_QTY
FROM SALES_DW.GOLD.VW_AI_SALES_COPILOT
GROUP BY ITEM_NAME
ORDER BY TOTAL_QTY DESC
LIMIT 10;
"""

    if "monthly revenue" in q:
        return """
SELECT
    DATE_TRUNC('MONTH', INVOICE_DATE) AS SALES_MONTH,
    SUM(NET_AMOUNT) AS TOTAL_REVENUE
FROM SALES_DW.GOLD.VW_AI_SALES_COPILOT
GROUP BY SALES_MONTH
ORDER BY SALES_MONTH;
"""

    return None


st.set_page_config(page_title="AI Sales Copilot", layout="wide")

st.title("🚀 AI Sales Data Engineering Copilot")
st.caption("MySQL → Airbyte → Snowflake → Streamlit → Ollama")


if st.button("Test Snowflake Connection"):
    try:
        df = run_sql("""
        SELECT
            CURRENT_DATABASE() AS DATABASE_NAME,
            CURRENT_SCHEMA() AS SCHEMA_NAME,
            CURRENT_WAREHOUSE() AS WAREHOUSE_NAME
        """)
        st.success("Snowflake Connection Successful")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("Snowflake Connection Failed")
        st.exception(e)


tab1, tab2, tab3 = st.tabs([
    "Analytics Copilot",
    "Data Quality",
    "Data Dictionary"
])


with tab1:
    st.subheader("Ask your sales data")

    question = st.text_input("Example: Show top 10 customers by sales")

    if st.button("Generate and Run SQL"):
        try:
            sql = get_template(question)

            if sql is None:
                sql = generate_sql(question)

            st.subheader("Generated SQL")
            st.code(sql, language="sql")

            st.info("Running SQL in Snowflake...")

            df = run_sql(sql)

            st.success("SQL executed successfully.")
            st.subheader("Result")
            st.write(f"Rows returned: {len(df)}")
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error("Execution failed.")
            st.exception(e)


with tab2:
    st.subheader("Data Quality Checks")

    checks = {
        "Duplicate Invoices": """
SELECT
    INVOICE_NO,
    COUNT(*) AS RECORDS
FROM SALES_DW.GOLD.FACT_SALES
GROUP BY INVOICE_NO
HAVING COUNT(*) > 1;
""",
        "Negative Sales": """
SELECT *
FROM SALES_DW.GOLD.FACT_SALES
WHERE NET_AMOUNT < 0;
""",
        "Missing Customer": """
SELECT *
FROM SALES_DW.GOLD.FACT_SALES
WHERE CUSTOMER_KEY IS NULL;
"""
    }

    selected = st.selectbox("Choose check", list(checks.keys()))

    if st.button("Run Check"):
        try:
            df = run_sql(checks[selected])
            st.dataframe(df, use_container_width=True)
            st.write(f"Rows returned: {len(df)}")
        except Exception as e:
            st.error("Data quality check failed.")
            st.exception(e)


with tab3:
    st.subheader("Data Dictionary")

    if st.button("Load Data Dictionary"):
        try:
            sql = """
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE
FROM SALES_DW.INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'GOLD'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
"""
            df = run_sql(sql)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error("Failed to load data dictionary.")
            st.exception(e)
