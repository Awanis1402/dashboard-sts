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
        "Statistik Ringkas",
        "Rekod Keseluruhan",
        "Laporan Penuh"])

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
        df_mmsi = pd.read_excel("Total Suspicious Activity.xlsx")

        # Format Tarikh
        if "Tarikh" in df_stat.columns:
            df_stat["Tarikh"] = df_stat["Tarikh"].astype(str).str.zfill(6)

        # Gabung semua kapal dari Vessel 1, 2, 3
        kapal_all = pd.concat([
            df_stat["Vessel 1"],
            df_stat["Vessel 2"],
            df_stat["Vessel 3"]
        ]).dropna().reset_index(drop=True).rename("Nama Kapal")
        kapal_df = kapal_all.to_frame()

        # Kira bilangan setiap kapal
        kapal_counts = kapal_df["Nama Kapal"].value_counts()
        kapal_top10 = kapal_counts.head(10).sort_values()

        # Cari kolum nama kapal dalam fail MMSI
        df_mmsi.columns = df_mmsi.columns.str.strip()
        kolum_padanan = next((c for c in df_mmsi.columns if "kapal" in c.lower() or "vessel" in c.lower()), None)
        if kolum_padanan:
            df_mmsi = df_mmsi.rename(columns={kolum_padanan: "Nama Kapal"})

        # Merge dengan MMSI
        kapal_df = kapal_df.merge(df_mmsi[["Nama Kapal", "MMSI"]].drop_duplicates(), on="Nama Kapal", how="left")
        kapal_df["LOID"] = kapal_df["MMSI"].apply(lambda x: f"LOID{x[-4:]}" if pd.notnull(x) and isinstance(x, str) else "-")

        # Papar jumlah
        st.metric("Jumlah Kapal Terlibat", kapal_df["Nama Kapal"].nunique())

       # Carta bar
        df_top = kapal_df["Nama Kapal"].value_counts().head(10).reset_index()
        df_top.columns = ["Nama Kapal", "Bilangan"]
        df_top = df_top.merge(df_mmsi[["Nama Kapal", "MMSI"]].drop_duplicates(), on="Nama Kapal", how="left")

        st.write("### 📊 Carta Top 10 Kapal Paling Kerap Muncul")
        fig = px.bar(
            df_top.sort_values("Bilangan"),
            x="Bilangan",
            y="Nama Kapal",
            orientation='h',
            text="Bilangan",
            hover_data={"Nama Kapal": False, "MMSI": True, "Bilangan": True}
        )

        fig.update_layout(
            plot_bgcolor='#f0f2f6',
            paper_bgcolor='#f0f2f6',
            xaxis_title="Bilangan",
            yaxis_title="Nama Kapal",
            font=dict(color="black"),  # semua teks
            xaxis=dict(
                title_font=dict(size=14, color="black"),
                tickfont=dict(color="black")
            ),
            yaxis=dict(
                title_font=dict(size=14, color="black"),
                tickfont=dict(color="black")
            )        
        )

        st.plotly_chart(fig, use_container_width=True)

        # Search / Filter
        col1, col2 = st.columns([1, 2])
        kapal_list = kapal_df["Nama Kapal"].dropna().unique().tolist()
        kapal_list.sort()
        selected_box = col1.selectbox("🚢 Tapis Kapal", ["Semua"] + kapal_list)
        keyword = col2.text_input("🔍 Cari Nama Kapal")

        # Tapis ikut search / selectbox
        if selected_box != "Semua":
            hasil = kapal_df[kapal_df["Nama Kapal"] == selected_box]
        elif keyword:
            hasil = kapal_df[kapal_df["Nama Kapal"].str.contains(keyword, case=False)]
        else:
            hasil = kapal_df.copy()
  
        if not hasil.empty:
            st.write(f"### 📋 Senarai Hasil Carian ({hasil['Nama Kapal'].nunique()} kapal)")
    
            # Kira jumlah & susun ikut bilangan desc
            table = (
                hasil.groupby(["Nama Kapal", "MMSI", "LOID"])
                .size()
                .reset_index(name="Bilangan")
                .sort_values("Bilangan", ascending=False)
                .reset_index(drop=True)
            )

            # Tambah no susunan dari 1
            table.index = table.index + 1
            table.reset_index(inplace=True)
            table = table.rename(columns={"index": "No"})

            st.dataframe(table, use_container_width=True)
        else:
            st.warning("Tiada kapal dijumpai.")

    except Exception as e:
        st.error(f"❌ Gagal baca data atau proses analisis: {e}")

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
