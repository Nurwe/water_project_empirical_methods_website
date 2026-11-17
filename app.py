
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Research Project", layout="wide")

st.title("Our Research Replication")

st.header("What is this paper about?")
st.info("Add your research question and main findings here.")

st.header("Explore the Results")

# Example data — replace with your actual results
df = pd.DataFrame({
    "Model": ["Original", "Original", "Alternative", "Alternative"],
    "Variable": ["X1", "X2", "X1", "X2"],
    "Coefficient": [0.5, 0.2, 0.3, 0.1]
})

model = st.selectbox("Choose model", df["Model"].unique())
filtered = df[df["Model"] == model]

st.subheader("Regression Table")
st.dataframe(filtered, hide_index=True)

st.subheader("Interactive Chart")
st.bar_chart(filtered.set_index("Variable")["Coefficient"])

st.header("Exam Questions")
st.write("1. Add your first question.")
st.write("2. Add your second question.")
st.write("3. Add your third question.")
