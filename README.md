
# 📊 STS Dashboard – Suspicious Tracking System

Dashboard ini dibina untuk bantu pemantauan dan analisis aktiviti mencurigakan berdasarkan data harian vessel (kapal) yang direkodkan.

## 🔍 Tujuan Utama
- Pantau pergerakan vessel yang mencurigakan
- Kenal pasti MMSI pelik atau kerap ulang ke kawasan sama
- Deteksi kapal yang tidak aktifkan AIS

## 🧠 Fungsi Utama
- ✅ Senarai vessel dicurigai dari data harian
- 📈 Graf bilangan kemunculan kapal
- 🗂️ Maklumat MMSI, LOID dan nama kapal
- 🔍 Filter & carian kapal tertentu
- 📊 Paparan visual mudah (bar chart)

## 🗃️ Struktur Data
Dashboard ini tidak gunakan database SQL. Ia dibina berdasarkan fail Excel sebagai sumber data utama.

### Fail Input:
- `Total Suspicious Activity.xlsx` – Data utama kapal
- `output_laporan_harian.xlsx` – Output analisis
- `01_Jun_2025/` – Laporan harian asal (.xlsx/.docx/.pdf)

## ⚙️ Teknologi Digunakan
| Komponen     | Teknologi                  |
|--------------|-----------------------------|
| Backend      | Python + Pandas             |
| Frontend     | Streamlit (interactive UI)  |
| Data Format  | Excel `.xlsx`, `.csv`       |
| Hosting (optional) | Streamlit Cloud / Local |

## 📁 Struktur Projek
```
sts_dashboard/
├── app.py
├── extract_docx.py
├── requirements.txt
├── Total Suspicious Activity.xlsx
├── output_laporan_harian.xlsx
├── 01_Jun_2025/
```

## ⚠️ Nota Tambahan
- Fail `.zip` besar dikecualikan dari repo melalui `.gitignore`
- Pastikan data sensitif tidak dikongsi secara awam

---
📌 Dibangunkan oleh MDSC Team | Last update: 13/07/2025
