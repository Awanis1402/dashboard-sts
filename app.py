import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import streamlit.components.v1 as components
import os
import base64
import zipfile
import io

# ====== SETUP ======
st.set_page_config(page_title="Dashboard STS", layout="wide")
st.title("📊 Suspicious STS Activity Dashboard - June 2025")

# ====== SETUP SESSION STATE ======
if "selected_vessel_detail" not in st.session_state:
    st.session_state.selected_vessel_detail = None

# ====== PILIH LAYER PAPARAN ======
if st.session_state.selected_vessel_detail:
    selected_tab = "📌 Vessel Details"
else:
    selected_tab = st.sidebar.radio("Pilih Paparan", [
        "ILLEGAL ANCHORING",
        "STS & BUNKERING Activity",
        "Report"])

# ====== LAYER 1: ILLEGAL ANCHORING (EMBED LOOKER) ======
if selected_tab == "ILLEGAL ANCHORING":
    st.subheader("📍 Illegal Anchoring")
    components.iframe("https://lookerstudio.google.com/embed/reporting/f5e896a9-cd90-44ce-8462-8ab7847ce969/page/p_lm853hjitd", height=800, scrolling=True)

# ====== LAYER 2: STS & BUNKERING Activity (EMBED LOOKER) ======
elif selected_tab == "STS & BUNKERING Activity":
    st.subheader("📂 STS & Bunkering Activity ")
    components.iframe("https://lookerstudio.google.com/embed/reporting/912f4ef9-e0cf-4c47-b818-f481c9c67289/page/kN8QF", height=800, scrolling=True)


# ====== LAYER 3: LAPORAN PENUH ======

elif selected_tab == "Report":
    import base64
    import pandas as pd
    from pathlib import Path

    st.markdown("## 📂 Paparan Laporan PDF (Jun 2025)")

    # ========== LOAD DATA ==========
    data_path = "output_laporan_harian.xlsx"
    df = pd.read_excel(data_path)

    # Gabung semua vessel untuk carian
    df["Semua Vessel"] = df[["Vessel 1", "Vessel 2", "Vessel 3"]].astype(str).agg(" | ".join, axis=1)

    # ========== SIDEBAR ==========
    st.sidebar.header("🔍 Filter")
    selected_date = st.sidebar.selectbox("Date", options=["All"] + sorted(df["Tarikh"].dropna().astype(str).unique().tolist()))
    selected_vessel = st.sidebar.selectbox("Filter by Vessel", options=["All"] + sorted(set(df["Vessel 1"].dropna()) | set(df["Vessel 2"].dropna()) | set(df["Vessel 3"].dropna())))
    keyword = st.sidebar.text_input("Search Keyword (File Name / Vessel)")
    expand_all = st.sidebar.checkbox("🔎 Expand All Reports", value=True)

    # ========== FILTER ==========
    filtered_df = df.copy()

    if selected_date != "All":
        filtered_df = filtered_df[filtered_df["Tarikh"].astype(str) == selected_date]

    if selected_vessel != "All":
        filtered_df = filtered_df[
            (filtered_df["Vessel 1"] == selected_vessel) |
            (filtered_df["Vessel 2"] == selected_vessel) |
            (filtered_df["Vessel 3"] == selected_vessel)
        ]

    if keyword:
        keyword_lower = keyword.lower()
        filtered_df = filtered_df[
            filtered_df["Nama Fail"].str.lower().str.contains(keyword_lower) |
            filtered_df["Semua Vessel"].str.lower().str.contains(keyword_lower)
        ]

    # ========== PAPARAN ==========
    st.markdown(f"Reports Encountered: *{len(filtered_df)}*")

    for _, row in filtered_df.iterrows():
        file_name = row["Nama Fail"]
        folder = str(row["Folder"]).strip()
        full_path = Path("01_Jun_2025") / folder / file_name

        with st.expander(f"📄 {file_name}", expanded=expand_all):
            if full_path.exists():
                with open(full_path, "rb") as pdf_file:
                    base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.warning(f"❗Laporan '{file_name}' tak jumpa dalam folder {folder}")

        st.markdown("---")
