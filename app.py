import tkinter as tk
from tkinter import ttk, messagebox, StringVar, filedialog
from tkcalendar import DateEntry
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors

# =========================================
#  KONFIGURASI DATABASE
# =========================================
# Pastikan server MySQL Anda berjalan di localhost:3306
# dengan user 'root' dan password '' (kosong).
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
}
DB_NAME = "db_klinik"


# =========================================
#  FUNGSI KONEKSI & INISIALISASI DB
# =========================================
def get_connection():
    """Mencoba terhubung ke server MySQL dan membuat database jika belum ada."""
    try:
        # 1. Hubungkan ke server MySQL
        con = mysql.connector.connect(**DB_CONFIG)
        cur = con.cursor()
        # 2. Buat database jika belum ada
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4")
        cur.close()
        con.close()

        # 3. Hubungkan ke database 'db_klinik'
        DB_CONFIG['database'] = DB_NAME
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        messagebox.showerror(
            "Koneksi Database Gagal",
            f"Tidak dapat terhubung ke MySQL.\nPastikan server MySQL berjalan.\n\nError: {e}"
        )
        root.quit() # Keluar dari aplikasi jika DB gagal
        return None

def ensure_table():
    """Membuat tabel 'tb_pasien' jika belum ada."""
    con = get_connection()
    if not con:
        return
    
    try:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tb_pasien (
                id_pasien INT AUTO_INCREMENT PRIMARY KEY,
                nama VARCHAR(100) NOT NULL,
                umur INT NOT NULL,
                jenis_kelamin VARCHAR(10) NOT NULL,
                keluhan VARCHAR(255) NOT NULL,
                dokter VARCHAR(100) NOT NULL,
                tanggal_kunjungan DATE NOT NULL
            )
        """)
        con.commit()
    except Error as e:
        messagebox.showerror("Inisialisasi Tabel Gagal", f"Gagal membuat tabel tb_pasien:\n{e}")
    finally:
        try:
            cur.close(); con.close()
        except:
            pass

# =========================================
#  FUNGSI LOGIKA (CRUD & FITUR)
# =========================================

def validate_input():
    """Memvalidasi form input sebelum insert/update."""
    nama = sv_nama.get().strip()
    umur = sv_umur.get().strip()
    jk = sv_jk.get()
    keluhan = sv_keluhan.get().strip()
    dokter = sv_dokter.get().strip()
    
    if not (nama and umur and jk and keluhan and dokter):
        messagebox.showwarning("Input Tidak Lengkap", "Semua kolom wajib diisi.")
        return False
    
    if not umur.isdigit():
        messagebox.showwarning("Input Tidak Valid", "Kolom 'Umur' harus berupa angka.")
        return False
        
    return True

def clear_form(*_):
    """Membersihkan semua input di form dan tree selection."""
    sv_id.set("")
    sv_nama.set("")
    sv_umur.set("")
    sv_jk.set("")
    sv_keluhan.set("")
    sv_dokter.set("")
    cal_tanggal.set_date(datetime.now().date())
    
    # Hapus seleksi di treeview
    if tree.selection():
        tree.selection_remove(tree.selection()[0])
        
    status.set("Form dibersihkan. Siap untuk input baru.")

def on_tree_select(event):
    """Mengisi form saat data di tabel di-klik."""
    selected_item = tree.focus()
    if not selected_item:
        return
        
    # Ambil nilai dari baris yang dipilih
    vals = tree.item(selected_item, 'values')
    if not vals:
        return

    clear_form() # Bersihkan form dulu
    
    # Set nilai ke StringVars
    sv_id.set(vals[0])
    sv_nama.set(vals[1])
    sv_umur.set(vals[2])
    
    # Konversi L/P ke Laki-laki/Perempuan untuk ComboBox
    jk_val = "Laki-laki" if str(vals[3]).upper() == 'L' else "Perempuan"
    sv_jk.set(jk_val)
    
    sv_keluhan.set(vals[4])
    sv_dokter.set(vals[5])
    
    # Set tanggal di DateEntry
    try:
        tgl = datetime.strptime(str(vals[6]), "%Y-%m-%d").date()
        cal_tanggal.set_date(tgl)
    except Exception:
        cal_tanggal.set_date(datetime.now().date())
        
    status.set(f"Data '{vals[1]}' dipilih. Siap untuk di-update atau di-hapus.")

def refresh_table():
    """Memuat/memperbarui data di tabel berdasarkan filter dan pencarian."""
    # 1. Bersihkan tabel
    for item in tree.get_children():
        tree.delete(item)
        
    con = get_connection()
    if not con:
        return
        
    try:
        cur = con.cursor()
        
        # 2. Bangun query SQL dinamis berdasarkan filter
        base_query = "SELECT * FROM tb_pasien"
        conditions = []
        params = []
        
        # Filter Pencarian
        keyword = sv_search_keyword.get().strip()
        search_by = sv_search_by.get()
        if keyword:
            if search_by == "nama":
                conditions.append("nama LIKE %s")
            elif search_by == "dokter":
                conditions.append("dokter LIKE %s")
            params.append(f"%{keyword}%")
            
        # Filter Tanggal
        if var_filter_enabled.get():
            try:
                filter_date = cal_filter.get_date()
                conditions.append("tanggal_kunjungan = %s")
                params.append(filter_date.strftime("%Y-%m-%d"))
            except Exception:
                pass # Abaikan jika tanggal filter tidak valid
        
        # 3. Gabungkan query
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            
        base_query += " ORDER BY tanggal_kunjungan DESC, nama ASC"
        
        # 4. Eksekusi query
        cur.execute(base_query, tuple(params))
        rows = cur.fetchall()
        
        # 5. Isi tabel dengan data
        for i, row in enumerate(rows):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.insert("", "end", values=row, tags=(tag,))
            
        lbl_count.configure(text=f"Total: {len(rows)} Pasien")
        status.set("Data berhasil dimuat ulang.")
        
    except Error as e:
        messagebox.showerror("Gagal Memuat Data", f"Error: {e}")
    finally:
        try:
            cur.close(); con.close()
        except:
            pass

def reset_filters():
    """Membersihkan form filter dan pencarian."""
    sv_search_keyword.set("")
    sv_search_by.set("nama")
    var_filter_enabled.set(False)
    cal_filter.set_date(datetime.now().date())
    refresh_table() # Muat ulang semua data
    status.set("Filter dan pencarian direset.")

def insert_data(*_):
    """Menyimpan data baru (Create) dengan CEK DUPLIKAT."""
    if not validate_input():
        return
        
    con = get_connection()
    if not con:
        return
        
    try:
        cur = con.cursor()
        
        # Ambil nilai dari form
        nama_val = sv_nama.get().strip()
        umur_val = int(sv_umur.get().strip())
        jk_val = 'L' if sv_jk.get() == "Laki-laki" else 'P'
        keluhan_val = sv_keluhan.get().strip()
        dokter_val = sv_dokter.get().strip()
        tgl_val = cal_tanggal.get_date().strftime("%Y-%m-%d")

        # =========================================
        #           PENGECEKAN DUPLIKAT
        # =========================================
        # Aturan: Duplikat jika NAMA, DOKTER, dan TGL KUNJUNGAN sama.
        check_query = """
            SELECT COUNT(*) FROM tb_pasien 
            WHERE nama = %s AND dokter = %s AND tanggal_kunjungan = %s
        """
        cur.execute(check_query, (nama_val, dokter_val, tgl_val))
        count = cur.fetchone()[0]
        
        if count > 0:
            messagebox.showerror("Data Duplikat", 
                                 f"Pasien '{nama_val}' sudah terdaftar\n"
                                 f"pada tanggal {tgl_val} dengan {dokter_val}.\n\n"
                                 "Data tidak disimpan.")
            status.set("Gagal: Data kunjungan sudah ada.")
            return # Hentikan proses insert
        # =========================================
        #         AKHIR PENGECEKAN DUPLIKAT
        # =========================================

        # Lanjutkan proses INSERT jika tidak duplikat
        query = """
            INSERT INTO tb_pasien (nama, umur, jenis_kelamin, keluhan, dokter, tanggal_kunjungan) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            nama_val,
            umur_val,
            jk_val,
            keluhan_val,
            dokter_val,
            tgl_val
        )
        
        cur.execute(query, params)
        con.commit()
        
        messagebox.showinfo("Sukses", f"Data pasien '{nama_val}' berhasil disimpan.")
        status.set(f"Data '{nama_val}' berhasil disimpan.")
        clear_form()
        refresh_table()
        
    except Error as e:
        messagebox.showerror("Gagal Menyimpan Data", f"Error: {e}")
    finally:
        try:
            cur.close(); con.close()
        except:
            pass

def update_data(*_):
    """Memperbarui data yang ada (Update) - TANPA Cek Duplikat."""
    pasien_id = sv_id.get()
    
    if not pasien_id:
        messagebox.showwarning("Data Belum Dipilih", "Pilih data dari tabel yang ingin di-update.")
        return

    if not validate_input():
        return
        
    con = get_connection()
    if not con:
        return
        
    try:
        cur = con.cursor()
        query = """
            UPDATE tb_pasien 
            SET nama=%s, umur=%s, jenis_kelamin=%s, keluhan=%s, dokter=%s, tanggal_kunjungan=%s 
            WHERE id_pasien=%s
        """
        
        jk_val = 'L' if sv_jk.get() == "Laki-laki" else 'P'
        tgl_val = cal_tanggal.get_date().strftime("%Y-%m-%d")
        
        params = (
            sv_nama.get().strip(),
            int(sv_umur.get().strip()),
            jk_val,
            sv_keluhan.get().strip(),
            sv_dokter.get().strip(),
            tgl_val,
            pasien_id
        )
        
        cur.execute(query, params)
        con.commit()
        
        if cur.rowcount == 0:
            messagebox.showwarning("Update Gagal", "Data tidak ditemukan (mungkin sudah dihapus).")
        else:
            messagebox.showinfo("Sukses", f"Data pasien '{sv_nama.get()}' berhasil di-update.")
            status.set(f"Data '{sv_nama.get()}' berhasil di-update.")
            
        clear_form()
        refresh_table()
        
    except Error as e:
        messagebox.showerror("Gagal Update Data", f"Error: {e}")
    finally:
        try:
            cur.close(); con.close()
        except:
            pass

def delete_data(*_):
    """Menghapus data yang dipilih (Delete)."""
    pasien_id = sv_id.get()
    nama = sv_nama.get()
    
    if not pasien_id:
        messagebox.showwarning("Data Belum Dipilih", "Pilih data dari tabel yang ingin di-hapus.")
        return

    if not messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus data:\n\nID: {pasien_id}\nNama: {nama}"):
        return
        
    con = get_connection()
    if not con:
        return
        
    try:
        cur = con.cursor()
        query = "DELETE FROM tb_pasien WHERE id_pasien = %s"
        
        cur.execute(query, (pasien_id,))
        con.commit()
        
        if cur.rowcount == 0:
            messagebox.showwarning("Hapus Gagal", "Data tidak ditemukan.")
        else:
            messagebox.showinfo("Sukses", f"Data pasien '{nama}' berhasil dihapus.")
            status.set(f"Data '{nama}' berhasil dihapus.")
            
        clear_form()
        refresh_table()
        
    except Error as e:
        messagebox.showerror("Gagal Hapus Data", f"Error: {e}")
    finally:
        try:
            cur.close(); con.close()
        except:
            pass

def export_pdf():
    """Mengekspor data yang saat ini ada di tabel ke file PDF."""
    
    # 1. Dapatkan data dari tabel (Treeview)
    data_list = []
    for item in tree.get_children():
        data_list.append(tree.item(item, 'values'))
        
    if not data_list:
        messagebox.showinfo("Ekspor Gagal", "Tidak ada data untuk diekspor.")
        return
        
    # 2. Minta lokasi penyimpanan file
    default_name = f"LaporanPasien_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=default_name,
        filetypes=[("PDF Document", "*.pdf")]
    )
    
    if not filepath:
        return # Pengguna membatalkan dialog
        
    try:
        # 3. Buat kanvas PDF
        from reportlab.lib.pagesizes import landscape
        c = canvas.Canvas(filepath, pagesize=landscape(A4))
        width, height = landscape(A4)
        margin = 2 * cm
        y = height - margin
        line_height = 0.8 * cm
        
        # 4. Judul
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y, "Laporan Data Pasien - Klinik Mini")
        y -= 0.5 * cm
        c.setFont("Helvetica", 10)
        c.drawString(margin, y, f"Dicetak pada: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        y -= 1.5 * cm
        
        # 5. Header Tabel
        headers = ["ID", "Nama", "Umur", "JK", "Keluhan", "Dokter", "Tgl. Kunjungan"]
        col_widths = [1*cm, 4*cm, 1.5*cm, 1*cm, 5.5*cm, 4*cm, 3*cm]
        c.setFont("Helvetica-Bold", 10)
        
        x = margin
        for i, header in enumerate(headers):
            c.drawString(x, y, header)
            c.rect(x-2, y - 5, col_widths[i], line_height, stroke=1, fill=0)
            x += col_widths[i]
        y -= line_height
        
        # 6. Isi Tabel
        c.setFont("Helvetica", 9)
        for row in data_list:
            # Cek jika butuh halaman baru
            if y < margin + line_height:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica-Bold", 10)
                x = margin
                for i, header in enumerate(headers):
                    c.drawString(x, y, header)
                    c.rect(x-2, y - 5, col_widths[i], line_height, stroke=1, fill=0)
                    x += col_widths[i]
                y -= line_height
                c.setFont("Helvetica", 9)
            
            # Tulis data
            x = margin
            for i, item in enumerate(row):
                # Batasi teks (misal keluhan) agar tidak tumpah
                text = str(item)
                if len(text) > 30 and i == 4: # Kolom keluhan
                    text = text[:30] + "..."
                c.drawString(x, y + 2, text)
                x += col_widths[i]
            y -= line_height

        # 7. Simpan file PDF
        c.save()
        messagebox.showinfo("Ekspor Sukses", f"Data berhasil disimpan ke:\n{filepath}")
        status.set("Laporan PDF berhasil disimpan.")
        
    except ImportError:
         messagebox.showerror(
             "ReportLab belum terpasang",
             "Silakan install terlebih dahulu:\n\npython -m pip install reportlab"
         )
    except Exception as e:
        messagebox.showerror("Ekspor PDF Gagal", f"Terjadi kesalahan:\n{e}")


# =========================================
#  SETUP GUI (TKINTER)
# =========================================

root = tk.Tk()
root.title("🏥 Manajemen Pasien Klinik Mini")
root.geometry("1150x780")
root.minsize(1024, 700)

# --- Konfigurasi Tema & Style ---
style = ttk.Style()
try:
    style.theme_use("clam") # 'clam', 'alt', 'default', 'vista' (win)
except tk.TclError:
    style.theme_use("default")

# Warna tema pastel
BG_COLOR = "#F0F8FF"  # Latar belakang utama (AliceBlue)
LBL_BG_COLOR = "#E6F3FF" # Latar belakang LabelFrame
FRAME_BG_COLOR = "#FFFFFF" # Latar belakang Frame
ACCENT_COLOR = "#B0E0E6" # Aksen (PowderBlue)
ALT_ROW_COLOR = "#FDFDFD"
TEXT_COLOR = "#222222"

style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 10))
style.configure("TFrame", background=BG_COLOR)
style.configure("TLabel", background=BG_COLOR)
style.configure("TButton", padding=6, font=("Segoe UI", 10, "bold"), background="#FFFFFF")
style.configure("TEntry", padding=5, fieldbackground="#FFFFFF")
style.configure("TCombobox", padding=5, fieldbackground="#FFFFFF")
style.configure("TLabelframe", background=LBL_BG_COLOR, padding=10, relief="solid", borderwidth=1)
style.configure("TLabelframe.Label", background=LBL_BG_COLOR, foreground="#00569E", font=("Segoe UI", 12, "bold"))

# Style Treeview
style.configure("Treeview", rowheight=30, background="white", fieldbackground="white")
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), padding=5, background="#E0F0FF")
style.map("Treeview", background=[("selected", ACCENT_COLOR)], foreground=[("selected", TEXT_COLOR)])

# Efek hover pada tombol
style.map("TButton",
    background=[('active', ACCENT_COLOR), ('!disabled', '#FFFFFF')],
    foreground=[('active', TEXT_COLOR)]
)

root.configure(bg=BG_COLOR)

# --- Variabel Kontrol (StringVar, dll) ---
sv_id = StringVar()
sv_nama = StringVar()
sv_umur = StringVar()
sv_jk = StringVar()
sv_keluhan = StringVar()
sv_dokter = StringVar()

sv_search_keyword = StringVar()
sv_search_by = StringVar(value="nama")
var_filter_enabled = tk.BooleanVar(value=False)

status = StringVar(value="Selamat datang! Siap beroperasi.")

# --- Layout Utama ---
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1) # Baris untuk tabel

# --- Frame 1: Form Input Data ---
frm_form = ttk.LabelFrame(root, text="📝 Form Input Pasien", padding=(15, 10))
frm_form.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
frm_form.columnconfigure((1, 3, 5), weight=1)

# Baris 1: ID, Nama, Umur
ttk.Label(frm_form, text="ID Pasien").grid(row=0, column=0, padx=5, pady=8, sticky="w")
ent_id = ttk.Entry(frm_form, textvariable=sv_id, state="readonly", width=10)
ent_id.grid(row=0, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frm_form, text="Nama Lengkap").grid(row=0, column=2, padx=(15, 5), pady=8, sticky="w")
ent_nama = ttk.Entry(frm_form, textvariable=sv_nama, width=35)
ent_nama.grid(row=0, column=3, padx=5, pady=8, sticky="ew")

ttk.Label(frm_form, text="Umur").grid(row=0, column=4, padx=(15, 5), pady=8, sticky="w")
ent_umur = ttk.Entry(frm_form, textvariable=sv_umur, width=10)
ent_umur.grid(row=0, column=5, padx=5, pady=8, sticky="w")

# Baris 2: Jenis Kelamin, Keluhan
ttk.Label(frm_form, text="Jenis Kelamin").grid(row=1, column=0, padx=5, pady=8, sticky="w")
cmb_jk = ttk.Combobox(frm_form, textvariable=sv_jk, values=["Laki-laki", "Perempuan"], state="readonly", width=18)
cmb_jk.grid(row=1, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frm_form, text="Keluhan").grid(row=1, column=2, padx=(15, 5), pady=8, sticky="w")
ent_keluhan = ttk.Entry(frm_form, textvariable=sv_keluhan, width=35)
ent_keluhan.grid(row=1, column=3, padx=5, pady=8, sticky="ew")

# Baris 3: Dokter, Tanggal Kunjungan
ttk.Label(frm_form, text="Dokter").grid(row=2, column=0, padx=5, pady=8, sticky="w")
ent_dokter = ttk.Entry(frm_form, textvariable=sv_dokter, width=20)
ent_dokter.grid(row=2, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frm_form, text="Tgl. Kunjungan").grid(row=2, column=2, padx=(15, 5), pady=8, sticky="w")
cal_tanggal = DateEntry(frm_form, width=33, background='darkblue',
                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
cal_tanggal.grid(row=2, column=3, padx=5, pady=8, sticky="ew")

# Frame untuk Tombol CRUD
frm_buttons = ttk.Frame(frm_form, style="TLabelframe") # Pakai style TLabelframe agar bg-nya sama
frm_buttons.grid(row=0, column=6, rowspan=3, sticky="ns", padx=(20, 5))

btn_insert = ttk.Button(frm_buttons, text="➕ Tambah", command=insert_data, width=12)
btn_insert.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")
btn_update = ttk.Button(frm_buttons, text="✏️ Update", command=update_data, width=12)
btn_update.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
btn_delete = ttk.Button(frm_buttons, text="🗑️ Hapus", command=delete_data, width=12)
btn_delete.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
btn_clear = ttk.Button(frm_buttons, text="🧹 Clear Form", command=clear_form, width=12)
btn_clear.grid(row=3, column=0, padx=5, pady=(5, 0), sticky="ew")


# --- Frame 2: Filter dan Pencarian ---
frm_controls = ttk.LabelFrame(root, text="🔍 Pencarian & Filter Data", padding=(15, 10))
frm_controls.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

ttk.Label(frm_controls, text="Cari:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ent_search = ttk.Entry(frm_controls, textvariable=sv_search_keyword, width=30)
ent_search.grid(row=0, column=1, padx=5, pady=5, sticky="w")

ttk.Label(frm_controls, text="berdasarkan:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
cmb_search_by = ttk.Combobox(frm_controls, textvariable=sv_search_by, values=["nama", "dokter"], state="readonly", width=15)
cmb_search_by.grid(row=0, column=3, padx=5, pady=5, sticky="w")

chk_filter = ttk.Checkbutton(frm_controls, text="Filter Tgl. Kunjungan:", variable=var_filter_enabled)
chk_filter.grid(row=0, column=4, padx=(20, 5), pady=5, sticky="w")
cal_filter = DateEntry(frm_controls, width=15, date_pattern='yyyy-mm-dd')
cal_filter.grid(row=0, column=5, padx=5, pady=5, sticky="w")

btn_search = ttk.Button(frm_controls, text="🔎 Terapkan", command=refresh_table)
btn_search.grid(row=0, column=6, padx=(10, 5), pady=5)
btn_reset = ttk.Button(frm_controls, text="Reset", command=reset_filters)
btn_reset.grid(row=0, column=7, padx=5, pady=5)

# Tombol Export PDF di pojok kanan
frm_controls.columnconfigure(8, weight=1) # Spacer
btn_pdf = ttk.Button(frm_controls, text="🖨️ Export ke PDF", command=export_pdf)
btn_pdf.grid(row=0, column=9, padx=5, pady=5, sticky="e")


# --- Frame 3: Tabel Data (Treeview) ---
frm_table = ttk.Frame(root, relief="solid", borderwidth=1)
frm_table.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
frm_table.columnconfigure(0, weight=1)
frm_table.rowconfigure(0, weight=1)

# Kolom
cols = ("id_pasien", "nama", "umur", "jenis_kelamin", "keluhan", "dokter", "tanggal_kunjungan")
tree = ttk.Treeview(frm_table, columns=cols, show="headings", selectmode="browse")

# Scrollbar
scroll_y = ttk.Scrollbar(frm_table, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frm_table, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")
tree.grid(row=0, column=0, sticky="nsew")

# Definisi Heading
tree.heading("id_pasien", text="ID")
tree.heading("nama", text="Nama Pasien")
tree.heading("umur", text="Umur")
tree.heading("jenis_kelamin", text="L/P")
tree.heading("keluhan", text="Keluhan")
tree.heading("dokter", text="Dokter")
tree.heading("tanggal_kunjungan", text="Tgl. Kunjungan")

# Definisi Lebar Kolom
tree.column("id_pasien", width=40, anchor="center", stretch=False)
tree.column("nama", width=200, anchor="w")
tree.column("umur", width=50, anchor="center")
tree.column("jenis_kelamin", width=40, anchor="center")
tree.column("keluhan", width=350, anchor="w")
tree.column("dokter", width=200, anchor="w")
tree.column("tanggal_kunjungan", width=120, anchor="center")

# Zebra-striping
tree.tag_configure("evenrow", background="#FFFFFF")
tree.tag_configure("oddrow", background="#F0F6FF")

# Bind event
tree.bind("<<TreeviewSelect>>", on_tree_select)
ent_search.bind("<Return>", lambda e: refresh_table())


# --- Frame 4: Status Bar ---
frm_status = ttk.Frame(root, relief="sunken", padding=(5, 8))
frm_status.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
lbl_status = ttk.Label(frm_status, textvariable=status, anchor="w")
lbl_status.grid(row=0, column=0, sticky="w")

lbl_count = ttk.Label(frm_status, text="Total: 0 Pasien", anchor="e")
lbl_count.grid(row=0, column=1, sticky="e")
frm_status.columnconfigure(1, weight=1)


# --- Shortcut Keyboard ---
root.bind("<Control-n>", clear_form)
root.bind("<Control-N>", clear_form)
root.bind("<Control-s>", insert_data)
root.bind("<Control-S>", insert_data)
root.bind("<Control-u>", update_data)
root.bind("<Control-U>", update_data)
root.bind("<Delete>", delete_data)


# =========================================
#  INISIALISASI & MAIN LOOP
# =========================================
if __name__ == "__main__":
    ensure_table()  # Pastikan tabel sudah ada
    refresh_table() # Muat data saat aplikasi pertama kali dibuka
    root.mainloop() # Jalankan aplikasi