from pathlib import Path
import pandas as pd

# === SET FOLDER ===
base_folder = Path("01_Jun_2025")  # ubah ikut nama folder sebenar

data = []

# Loop setiap hari (subfolder: 010625, 020625, dll)
for subfolder in base_folder.iterdir():
    if subfolder.is_dir():
        for file in subfolder.glob("*.docx"):
            file_name = file.stem  # contoh: 01.Illegal STS Report - HERA & INTAN - 010625
            parts = file_name.split(" - ")
            if len(parts) >= 3:
                vessels = parts[1].strip()
                date = parts[2].strip()
                data.append({
                    "Tarikh": date,
                    "Kapal Terlibat": vessels,
                    "Nama Fail": file.name,
                    "Folder": subfolder.name
                })

# Convert ke DataFrame
df_reports = pd.DataFrame(data)

# === Tambah line ni dulu untuk semak ===
print(df_reports.head())       # tunjuk 5 baris pertama
print(df_reports.columns)      # tunjuk senarai nama kolum

# Pisahkan Vessel 1, Vessel 2, Vessel 3 (jika ada)
vessel_split = df_reports['Kapal Terlibat'].str.split('&')
df_reports['Vessel 1'] = vessel_split.str[0].str.strip()
df_reports['Vessel 2'] = vessel_split.str[1].str.strip() if vessel_split.str.len().gt(1).any() else None
df_reports['Vessel 3'] = vessel_split.str[2].str.strip() if vessel_split.str.len().gt(2).any() else None

# Simpan ke Excel
df_reports.to_excel("output_laporan_harian.xlsx", index=False)
print("✅ Berjaya simpan sebagai: output_laporan_harian.xlsx")