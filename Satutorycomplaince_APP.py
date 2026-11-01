import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="BSNL MH Compliance Dashboard",
    page_icon="📅",
    layout="wide"
)

st.title("📅 BSNL Maharashtra Compliance Dashboard")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:
    df = pd.read_excel("Compliance_Master.xlsx")

    df["Due Date"] = pd.to_datetime(
        df["Due Date"],
        errors="coerce"
    )

    today = pd.Timestamp.today().normalize()

    df["Days Left"] = (
        df["Due Date"] - today
    ).dt.days

except Exception as e:
    st.error(f"Error loading file : {e}")
    st.stop()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

company = st.sidebar.multiselect(
    "Company",
    sorted(df["COMPANY"].dropna().unique())
)

category = st.sidebar.multiselect(
    "Category",
    sorted(df["Category"].dropna().unique())
)

department = st.sidebar.multiselect(
    "Department",
    sorted(df["Department"].dropna().unique())
)

frequency = st.sidebar.multiselect(
    "Frequency",
    sorted(df["Frequency"].dropna().unique())
)

status = st.sidebar.multiselect(
    "Status",
    sorted(df["Status"].dropna().unique())
)

if company:
    df = df[df["COMPANY"].isin(company)]

if category:
    df = df[df["Category"].isin(category)]

if department:
    df = df[df["Department"].isin(department)]

if frequency:
    df = df[df["Frequency"].isin(frequency)]

if status:
    df = df[df["Status"].isin(status)]

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

total = len(df)

completed = len(
    df[df["Status"].astype(str).str.upper() == "COMPLETED"]
)

pending = len(
    df[df["Status"].astype(str).str.upper() == "PENDING"]
)

overdue = len(
    df[df["Days Left"] < 0]
)

due7 = len(
    df[(df["Days Left"] >= 0) &
       (df["Days Left"] <= 7)]
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total", total)
c2.metric("Completed", completed)
c3.metric("Pending", pending)
c4.metric("Overdue", overdue)
c5.metric("Next 7 Days", due7)

st.divider()

# --------------------------------------------------
# UPCOMING ALERTS
# --------------------------------------------------

st.subheader("🚨 Upcoming Compliance Alerts")

alerts = df[
    df["Days Left"] <= 30
].sort_values("Due Date")

for _, row in alerts.iterrows():

    message = (
        f"{row['COMPANY']} | "
        f"{row['Compliance Name']} | "
        f"Due : {row['Due Date'].date()}"
    )

    if row["Days Left"] < 0:
        st.error(message)

    elif row["Days Left"] <= 7:
        st.warning(message)

    else:
        st.info(message)

# --------------------------------------------------
# COMPANY WISE SUMMARY
# --------------------------------------------------

st.subheader("🏢 Company Wise Summary")

company_summary = (
    df.groupby("COMPANY")
    .size()
    .reset_index(name="Compliance Count")
)

st.dataframe(
    company_summary,
    use_container_width=True
)

# --------------------------------------------------
# CATEGORY WISE SUMMARY
# --------------------------------------------------

st.subheader("📊 Category Wise Summary")

category_summary = (
    df.groupby("Category")
    .size()
    .reset_index(name="Count")
)

st.dataframe(
    category_summary,
    use_container_width=True
)

# --------------------------------------------------
# DEPARTMENT WISE SUMMARY
# --------------------------------------------------

st.subheader("🏢 Department Wise Summary")

dept_summary = (
    df.groupby("Department")
    .size()
    .reset_index(name="Count")
)

st.dataframe(
    dept_summary,
    use_container_width=True
)

# --------------------------------------------------
# COMPLIANCE REGISTER
# --------------------------------------------------

st.subheader("📋 Compliance Register")

def highlight_rows(row):

    if row["Days Left"] < 0:
        return ["background-color:#ffcccc"] * len(row)

    elif row["Days Left"] <= 7:
        return ["background-color:#fff3cd"] * len(row)

    elif row["Days Left"] <= 15:
        return ["background-color:#d1ecf1"] * len(row)

    return [""] * len(row)

st.dataframe(
    df.style.apply(
        highlight_rows,
        axis=1
    ),
    use_container_width=True,
    height=600
)

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

st.download_button(
    label="⬇ Download Compliance Report",
    data=df.to_csv(index=False),
    file_name="Compliance_Report.csv",
    mime="text/csv"
)
