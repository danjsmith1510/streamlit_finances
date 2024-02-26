import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

def bgcolor_positive_or_negative(value):
    # print (value)
    bgcolor = "darkgreen" if value < 0 else "darkred"
    return f"background-color: {bgcolor};"

# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return rows

st.set_page_config(layout="wide")

budget_performance = pd.DataFrame(run_query(
    """
    SELECT 
    category_title as Category, 
    budgeted_amount as Budgeted, 
    expected_amount as Expected, 
    actual_amount as Actual, 
    actual_amount - expected_amount as Progress 
    FROM finances.vw_monthly_budget_performance
    UNION ALL
    SELECT 'TOTAL', SUM(budgeted_amount), sum(expected_amount), sum(actual_amount), sum(actual_amount) - sum(expected_amount)
    from finances.vw_monthly_budget_performance
    order by 2
    """
))

subcategory_amounts = pd.DataFrame(run_query(
    """
    SELECT category_title as Category, amount as Amount
    FROM finances.vw_monthly_subcategory_amounts
    where month = date_trunc(current_date, month)
    order by amount
    """
))

# daily_progress = run_query(
#     """
#     select day_number, expected_spend, actual_spend
#     from finances.daily_progress
#     where month = date_trunc(current_date, month)
#     order by day_number
#     """
# )

budget_performance = budget_performance.style.applymap(bgcolor_positive_or_negative, subset=['Progress'])

with st.container():

    # print (daily_progress)

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(
            data=budget_performance, 
            column_config={
                "Budgeted": st.column_config.NumberColumn(format="$%.2f"),
                "Expected": st.column_config.NumberColumn(format="$%.2f"),
                "Actual": st.column_config.NumberColumn(format="$%.2f"),
                "Progress": st.column_config.NumberColumn(format="$%.2f")
            },
            hide_index=True
        )

    with col2:
        st.dataframe(
            data=subcategory_amounts, 
            # column_config={
            #     "Budgeted": st.column_config.NumberColumn(format="$%.2f"),
            #     "Expected": st.column_config.NumberColumn(format="$%.2f"),
            #     "Actual": st.column_config.NumberColumn(format="$%.2f"),
            #     "Progress": st.column_config.NumberColumn(format="$%.2f")
            # },
            hide_index=True
        )

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