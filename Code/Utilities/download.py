import streamlit as st


@st.experimental_memo
def convert_df(df):

    """Convert pandas dataframe to CSV format"""

    return df.to_csv(index=False).encode("utf-8")
