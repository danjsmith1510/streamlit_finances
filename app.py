import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return rows

st.set_page_config(layout="wide")

budget_performance = run_query(
    """
    SELECT category_title, budgeted_amount, expected_amount, actual_amount, actual_amount - expected_amount as progress 
    FROM finances.vw_monthly_budget_performance
    """
)

daily_progress = run_query(
    """
    select day_number, expected_spend, actual_spend
    from finances.daily_progress
    where month = date_trunc(current_date, month)
    order by day_number
    """
)

with st.container():

    print (daily_progress)

    col1, col2 = st.columns(2)

    with col1:
        st.table(budget_performance)

    with col2:
        df = pd.DataFrame(daily_progress)
        print (df)
        st.line_chart(df, x="day_number", y="expected_spend")

# with st.container():

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         st.table(rows)

#     with col2:
#         st.table(rows)
    
#     with col3:
#         st.table(rows)

# Print results.
# st.write("Some wise words from Shakespeare:")
# st.table(rows)

# for row in rows:
#     st.write(row)