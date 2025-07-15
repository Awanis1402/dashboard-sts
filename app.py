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
elif selected_tab == "Laporan Penuh":
    st.markdown("## 📂 Paparan Laporan PDF (Jun 2025)")

    import base64
    from pathlib import Path
    import pandas as pd

    report_root = Path("01_Jun_2025")

    # 📄 Baca senarai laporan dari Excel
    df = pd.read_excel("output_laporan_harian.xlsx", sheet_name=2)
    st.write(f"Reports Encountered: *{len(df)}*")

    # 🔍 Sidebar Filter
    st.sidebar.markdown("### 🔍 Filter")
    tarikh_opsyen = ["All"] + sorted(df["Folder"].astype(str).unique())
    vessel_opsyen = ["All"] + sorted(df["Vessel"].astype(str).unique())

    tarikh_dipilih = st.sidebar.selectbox("Date", tarikh_opsyen)
    vessel_dipilih = st.sidebar.selectbox("Filter by Vessel", vessel_opsyen)
    keyword = st.sidebar.text_input("Search Keyword (File Name / Vessel)")

    show_all = st.sidebar.checkbox("📂 Expand All Reports", value=False)

    # 🔍 Tapisan
    if tarikh_dipilih != "All":
        df = df[df["Folder"].astype(str) == tarikh_dipilih]

    if vessel_dipilih != "All":
        df = df[df["Vessel"].astype(str) == vessel_dipilih]

    if keyword:
        df = df[df.apply(lambda row: keyword.lower() in str(row["Nama Fail"]).lower() or keyword.lower() in str(row["Vessel"]).lower(), axis=1)]

    # ✅ Papar setiap laporan
    for idx, row in df.iterrows():
        file_name = str(row["Nama Fail"]).strip().replace(".docx", ".pdf")
        folder = str(row["Folder"]).strip()
        full_path = report_root / folder / file_name

        with st.expander(f"{file_name}", expanded=show_all):
            if full_path.exists():
                # 👁️ Papar PDF
                with open(full_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)

                # 📥 Muat turun
                with open(full_path, "rb") as f_pdf:
                    st.download_button(
                        label="📥 Muat Turun PDF",
                        data=f_pdf,
                        file_name=file_name,
                        mime="application/pdf"
                    )
            else:
                st.warning(f"❗ Laporan '{file_name}' tak jumpa dalam folder {folder}")
