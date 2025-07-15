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
    st.markdown("## 📂 Laporan PDF - Jun 2025")

    from pathlib import Path
    import base64

    report_folder = Path("01_Jun_2025")
    all_pdfs = list(report_folder.rglob("*.pdf"))

    if not all_pdfs:
        st.warning("⚠️ Tiada laporan dijumpai.")
    else:
        st.success(f"📄 Jumlah laporan dijumpai: **{len(all_pdfs)}**")

    keyword = st.sidebar.text_input("🔍 Cari dalam nama fail")

    if keyword:
        all_pdfs = [f for f in all_pdfs if keyword.lower() in f.name.lower()]

    for f in sorted(all_pdfs):
        with st.expander(f"📄 {f.name}"):
            with open(f, "rb") as pdf_file:
                base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

            with open(f, "rb") as pdf_download:
                st.download_button(
                    label="📥 Muat Turun PDF",
                    data=pdf_download,
                    file_name=f.name,
                    mime="application/pdf"
                )

