import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import streamlit.components.v1 as components
import os
import base64
import zipfile
import io
import pdfplumber

# ====== SETUP ======
st.set_page_config(page_title="Dashboard STS", layout="wide")
st.title("📊 Dashboard Aktiviti STS Mencurigakan - Jun 2025")

# ====== SETUP SESSION STATE ======
if "selected_vessel_detail" not in st.session_state:
    st.session_state.selected_vessel_detail = None

# ====== PILIH LAYER PAPARAN ======
if st.session_state.selected_vessel_detail:
    selected_tab = "📌 Butiran Kapal"
else:
    selected_tab = st.sidebar.radio("Pilih Paparan", [
        "ILLEGAL ANCHORING",
        "STS & BUNKERING Activity",
        "Laporan Penuh"])

# ====== LAYER 1: ILLEGAL ANCHORING (EMBED LOOKER) ======
if selected_tab == "ILLEGAL ANCHORING":
    st.subheader("📍 Illegal Anchoring – Looker Studio (Jun 2025)")
    components.iframe("https://lookerstudio.google.com/embed/reporting/f5e896a9-cd90-44ce-8462-8ab7847ce969/page/p_lm853hjitd", height=800, scrolling=True)

# ====== LAYER 2: STS & BUNKERING Activity (EMBED LOOKER) ======
elif selected_tab == "STS & BUNKERING Activity":
    st.subheader("📂 STS & Bunkering Activity – Looker Studio")
    components.iframe("https://lookerstudio.google.com/embed/reporting/912f4ef9-e0cf-4c47-b818-f481c9c67289/page/kN8QF", height=800, scrolling=True)


# ====== LAYER 3: LAPORAN PENUH ======
elif selected_tab == "Laporan Penuh":
    st.markdown("## 📂 Pilih Fail Excel Untuk Tunjuk Data")
    uploaded_excel = st.file_uploader("Muat naik fail Excel (format sama seperti output_laporan_harian.xlsx)", type=["xlsx"])

    if uploaded_excel:
        df = pd.read_excel(uploaded_excel)
    else:
        excel_file = "output_laporan_harian.xlsx"
        df = pd.read_excel(excel_file)

    report_folder = Path("01_Jun_2025")
    df["Tarikh"] = df["Tarikh"].astype(str).str.zfill(6)
    df["Folder"] = df["Folder"].astype(str).str.zfill(6)

    st.sidebar.header("🔍 Tapisan")
    selected_date = st.sidebar.selectbox("Pilih Tarikh", ["Semua"] + sorted(df["Tarikh"].unique()))
    all_vessels = pd.concat([df["Vessel 1"], df["Vessel 2"], df["Vessel 3"]]).dropna().unique()
    selected_vessel = st.sidebar.selectbox("Tapis Ikut Kapal", ["Semua"] + sorted(all_vessels))
    search_keyword = st.sidebar.text_input("Cari Kata Kunci Dalam Nama Fail / Kapal")

    filtered = df.copy()
    if selected_date != "Semua":
        filtered = filtered[filtered["Tarikh"] == selected_date]

    if selected_vessel != "Semua":
        filtered = filtered[
            (filtered["Vessel 1"] == selected_vessel) |
            (filtered["Vessel 2"] == selected_vessel) |
            (filtered["Vessel 3"] == selected_vessel)
        ]

    if search_keyword:
        filtered = filtered[
            filtered["Nama Fail"].str.contains(search_keyword, case=False, na=False) |
            filtered["Kapal Terlibat"].str.contains(search_keyword, case=False, na=False)
        ]

    if selected_date == "Semua":
        st.write(f"### 📅 Tarikh Dipilih: **Semua Tarikh**")
    else:
        st.write(f"### 📅 Tarikh Dipilih: {selected_date}")

    st.write(f"Jumlah laporan dijumpai: **{len(filtered)}**")

    with st.container():
        for i, row in filtered.iterrows():
            folder_str = f"{int(row['Folder']):06d}"
            file_path = report_folder / folder_str / row["Nama Fail"]

            with st.container():
                st.markdown(f"#### 📄 {row['Nama Fail']}")
                st.write(f"Kapal Terlibat: **{row['Kapal Terlibat']}**")

                if file_path.exists():
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="📥 Muat Turun Report",
                            data=f,
                            file_name=row["Nama Fail"],
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error(f"❌ Fail tak jumpa: {file_path}")

    st.markdown("---")
    st.subheader("📤 Muat Turun Rekod Ini Dalam Excel")

    export_excel = filtered.drop(columns=["Folder"]).copy()
    st.download_button(
        label="⬇️ Muat Turun Senarai Ini",
        data=export_excel.to_csv(index=False).encode('utf-8'),
        file_name=f"laporan_{selected_date}.csv",
        mime="text/csv"
    )

st.caption("Dibangunkan oleh MDSC ✨")
