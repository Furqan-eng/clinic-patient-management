# 💊 Clinic Patient Management

A desktop GUI application built with **Python (Tkinter)** and **MySQL** to manage patient records for a small clinic.  
This system supports full **CRUD operations**, search and filter features, and allows exporting patient data to **PDF (landscape format)** with a clean, modern interface.

---

## 🚀 Features
- ✅ Add, edit, and delete patient records  
- 🔍 Search patients by name or doctor  
- 🗓️ Filter by visit date  
- 🧾 Export all patient data to PDF (landscape)  
- 🎨 Modern GUI built using **Tkinter** and **ttk**  

---

## 🗄️ Database Structure
**Database:** `db_klinik`  
**Table:** `tb_pasien`

| Column | Type | Description |
|--------|------|-------------|
| id_pasien | INT (PK, AI) | Unique patient ID |
| nama | VARCHAR(100) | Full name |
| umur | INT | Age |
| jenis_kelamin | VARCHAR(10) | Gender (L/P) |
| keluhan | VARCHAR(255) | Main complaint |
| dokter | VARCHAR(100) | Responsible doctor |
| tanggal_kunjungan | DATE | Visit date |

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Furqan-eng/clinic-patient-management.git
