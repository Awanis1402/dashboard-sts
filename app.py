import streamlit as st
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components

# ====== SETUP ======
st.set_page_config(page_title="Dashboard STS", layout="wide")
st.title("📊 Dashboard Aktiviti STS Mencurigakan - Jun 2025")

# ====== PILIH LAYER PAPARAN ======
selected_tab = st.sidebar.radio("Pilih Paparan", ["ILLEGAL ANCHORING", "STS & BUNKERING Activity", "Statistik Ringkas", "Rekod Keseluruhan", "Laporan Penuh"])

# ====== LAYER 1: ILLEGAL ANCHORING (EMBED LOOKER) ======
if selected_tab == "ILLEGAL ANCHORING":
    st.subheader("📍 Illegal Anchoring – Looker Studio (Jun 2025)")
    components.iframe("https://lookerstudio.google.com/embed/reporting/q3pWaEwKP1o/page/p_zye5kx3ddc", height=800, scrolling=True)

# ====== LAYER 2: STS & BUNKERING Activity (EMBED LOOKER) ======
elif selected_tab == "STS & BUNKERING Activity":
    st.subheader("📂 STS & Bunkering Activity – Looker Studio")
    components.iframe("https://lookerstudio.google.com/embed/reporting/912f4ef9-e0cf-4c47-b818-f481c9c67289/page/kN8QF?s=uRlJkUW3v34", height=800, scrolling=True)

# ====== LAYER 3: STATISTIK RINGKAS ======
elif selected_tab == "Statistik Ringkas":
    st.subheader("📊 Statistik Ringkas")
    try:
        df_stat = pd.read_excel("output_laporan_harian.xlsx")
        df_stat["Tarikh"] = df_stat["Tarikh"].astype(str).str.zfill(6)

        st.metric("Jumlah Rekod", len(df_stat))

        kapal_all = pd.concat([df_stat["Vessel 1"], df_stat["Vessel 2"], df_stat["Vessel 3"]]).dropna()
        kapal_counts = kapal_all.value_counts()
        kapal_atas_20 = kapal_counts[kapal_counts >= 20]

        st.write("### 🚢 Kapal Muncul 20 Kali dan Ke Atas")
        st.dataframe(kapal_atas_20.reset_index().rename(columns={"index": "Nama Kapal", 0: "Bilangan"}), use_container_width=True)

    except Exception as e:
        st.error("❌ Gagal baca fail 'output_laporan_harian.xlsx'. Sila pastikan fail wujud dan format betul.")

# ====== LAYER 4: TOTAL SUSPICIOUS ACTIVITY ======
elif selected_tab == "Rekod Keseluruhan":
    st.subheader("🧾 Rekod Aktiviti Mencurigakan Keseluruhan")
    try:
        df_total = pd.read_excel("Total Suspicious Activity.xlsx")
        df_total.columns = [col.strip().lower() for col in df_total.columns]

        vessel_col = next((col for col in df_total.columns if "vessel" in col), None)
        date_col = next((col for col in df_total.columns if "date" in col or "tarikh" in col), None)

        if vessel_col is None or date_col is None:
            raise ValueError("Kolum 'Vessel Name' atau 'Date' tidak dijumpai dalam fail.")

        df_total[date_col] = pd.to_datetime(df_total[date_col], errors="coerce")
        col1, col2, col3 = st.columns([1, 1, 2])
        unique_dates = df_total[date_col].dropna().dt.strftime("%Y-%m-%d").unique().tolist()
        vessel_list = df_total[vessel_col].dropna().unique()

        selected_tsa_date = col1.selectbox("Tapis Ikut Tarikh", ["Semua"] + sorted(unique_dates))
        selected_tsa_vessel = col2.selectbox("Tapis Ikut Kapal", ["Semua"] + sorted(vessel_list))
        keyword_filter = col3.text_input("Cari Kata Kunci Dalam Fail atau Kapal")

        df_tsa_filtered = df_total.copy()
        if selected_tsa_date != "Semua":
            date_filter = pd.to_datetime(selected_tsa_date)
            df_tsa_filtered = df_tsa_filtered[df_tsa_filtered[date_col] == date_filter]
        if selected_tsa_vessel != "Semua":
            df_tsa_filtered = df_tsa_filtered[df_tsa_filtered[vessel_col] == selected_tsa_vessel]

        if keyword_filter:
            df_tsa_filtered = df_tsa_filtered[
                df_tsa_filtered.apply(lambda row: keyword_filter.lower() in str(row).lower(), axis=1)
            ]

        st.dataframe(df_tsa_filtered, use_container_width=True)

        st.download_button(
            label="⬇️ Muat Turun Data Penuh",
            data=df_tsa_filtered.to_csv(index=False).encode('utf-8'),
            file_name="total_suspicious_activity_filtered.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"❌ Gagal baca fail 'Total Suspicious Activity.xlsx': {e}")

# ====== LAYER 5: LAPORAN PENUH ======
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
