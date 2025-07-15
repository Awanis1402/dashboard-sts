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
    st.markdown("## 📂 Report")

    try:
        df = pd.read_excel("output_Daily_Report.xlsx")
        report_folder = Path("01_Jun_2025")

        # Format
        df["Date"] = df["Tarikh"].astype(str).str.zfill(6)
        df["Folder"] = df["Folder"].astype(str).str.zfill(6)

        # Tapisan
        st.sidebar.header("🔍 Filter")
        selected_date = st.sidebar.selectbox("Pilih Tarikh", ["Semua"] + sorted(df["Tarikh"].unique()))
        all_vessels = pd.concat([df["Vessel 1"], df["Vessel 2"], df["Vessel 3"]]).dropna().unique()
        selected_vessel = st.sidebar.selectbox("Filter by Vessel", ["All"] + sorted(all_vessels))
        search_keyword = st.sidebar.text_input("Search Keyword (File Name / Vessel)")


        expand_all = st.sidebar.checkbox("🔽 Expand All Reports", value=False)

        filtered = df.copy()
        if selected_date != "All":
            filtered = filtered[filtered["Tarikh"] == selected_date]
        if selected_vessel != "All":
            filtered = filtered[
                (filtered["Vessel 1"] == selected_vessel) |
                (filtered["Vessel 2"] == selected_vessel) |
                (filtered["Vessel 3"] == selected_vessel)
            ]
        if search_keyword:
            filtered = filtered[
                filtered["File Name"].str.contains(search_keyword, case=False, na=False) |
                filtered["Vessel"].str.contains(search_keyword, case=False, na=False)
            ]

        st.write(f"Jumlah laporan dijumpai: *{len(filtered)}*")

        for _, row in filtered.iterrows():
            folder_str = f"{int(row['Folder']):06d}"
            file_name = row["File Name"]
            file_path = report_folder / folder_str / file_name

            if file_path.suffix.lower() == ".pdf" and file_path.exists():
                with st.expander(f"📄 {file_name}", expanded=expand_all):
                    st.write(f"🛳️ Vessel: *{row['Vessel']}*")

                    with open(file_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                        pdf_viewer = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>'
                        st.markdown(pdf_viewer, unsafe_allow_html=True)

                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download",
                            data=f,
                            file_name=file_name,
                            mime="application/pdf"
                        )

    except Exception as e:
        st.error(f"❌ Gagal papar laporan: {e}")
