import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Approval Cadence Analyzer", layout="centered")
st.title("📊 BvD List Approval Cadence Calculator")
st.write("Upload your spreadsheet with changelogs. We'll calculate averages and recommend an approval cadence.")

# Approval cadence thresholds
CADENCE_THRESHOLDS = {
    "Daily": (0, 50),
    "Weekly": (50, 100),
    "Bi-weekly": (100, 200),
    "Monthly": (200, float("inf"))
}

# Parse changelog text
def parse_changelog(text):
    adds = list(map(int, re.findall(r"Add off: (\d+)", text)))
    edits = list(map(int, re.findall(r"Edit off: (\d+)", text)))
    deletes = list(map(int, re.findall(r"Delete: (\d+)", text)))
    return adds, edits, deletes

# Determine approval cadence based on average adds
def get_cadence(avg_add):
    for cadence, (low, high) in CADENCE_THRESHOLDS.items():
        if low <= avg_add < high:
            return cadence
    return "Unknown"

uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Ensure required columns exist
    if 'List Name' not in df.columns or 'Changelog Text' not in df.columns:
        st.error("Your file must include 'List Name' and 'Changelog Text' columns.")
    else:
        avg_adds = []
        avg_edits = []
        avg_deletes = []
        cadences = []

        for _, row in df.iterrows():
            adds, edits, deletes = parse_changelog(str(row['Changelog Text']))

            avg_add = round(sum(adds) / len(adds), 2) if adds else 0
            avg_edit = round(sum(edits) / len(edits), 2) if edits else 0
            avg_delete = round(sum(deletes) / len(deletes), 2) if deletes else 0

            avg_adds.append(avg_add)
            avg_edits.append(avg_edit)
            avg_deletes.append(avg_delete)
            cadences.append(get_cadence(avg_add))

        df['Average Adds'] = avg_adds
        df['Average Edits'] = avg_edits
        df['Average Deletes'] = avg_deletes
        df['Recommended Approval Cadence'] = cadences

        st.success("✅ Analysis complete!")
        st.dataframe(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
        st.download_button(
            label="📥 Download Results as Excel",
            data=output.getvalue(),
            file_name="approval_cadence_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
