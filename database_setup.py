from app import app, db, Event, Daerah, Kategori, Grup, Alat, Peserta
from datetime import date

# ===============================================================
# DATA CONTOH UNTUK PENGISIAN DATABASE
# Anda bisa mengubah atau menambah data di sini sesuai kebutuhan
# ===============================================================

DAERAH_SUMBAR = [
    "Agam", "Dharmasraya", "Kepulauan Mentawai", "Lima Puluh Kota", 
    "Padang Pariaman", "Pasaman", "Pasaman Barat", "Pesisir Selatan", 
    "Sijunjung", "Solok", "Solok Selatan", "Tanah Datar", "Bukittinggi", 
    "Padang", "Padang Panjang", "Pariaman", "Payakumbuh", "Sawahlunto", " Kota Solok"
]
KATEGORI_LIST = ["Artistik Putra", "Artistik Putri", "Ritmik", "Aerobik Gymnastic"]
GRUP_LIST = ["Pra Junior", "Junior", "Senior", "AG 1", "AG 2"]
ALAT_LIST = [
    "Free Hand", "Floor Exercise", "Vaulting Table", "Pommel Horse", 
    "Rings", "Parallel Bars", "Horizontal Bar", "Uneven Bars", 
    "Balance Beam", "Rope", "Hoop", "Ball", "Clubs", "Ribbon"
]

# Data Contoh Event
EVENTS_CONTOH = [
    {'nama': 'Pekan Olahraga Provinsi (PORPROV) 2025', 'tanggal': date(2025, 11, 10)},
    {'nama': 'Kejuaraan Daerah Junior 2025', 'tanggal': date(2025, 7, 22)},
]

# Data Contoh Peserta yang sudah terhubung ke Event, Kategori, dan Grup
PESERTA_CONTOH = [
    # Peserta untuk PORPROV 2025
    {"nama": "Budi Santoso", "event": "Pekan Olahraga Provinsi (PORPROV) 2025", "daerah": "Padang", "kategori": "Artistik Putra", "grup": "Senior"},
    {"nama": "Andi Wijaya", "event": "Pekan Olahraga Provinsi (PORPROV) 2025", "daerah": "Padang", "kategori": "Artistik Putra", "grup": "Senior"},
    {"nama": "P2", "event": "Pekan Olahraga Provinsi (PORPROV) 2025", "daerah": "Agam", "kategori": "Artistik Putra", "grup": "Senior"},
    {"nama": "P3", "event": "Pekan Olahraga Provinsi (PORPROV) 2025", "daerah": "Bukittinggi", "kategori": "Artistik Putra", "grup": "Senior"},
    {"nama": "Citra Lestari", "event": "Pekan Olahraga Provinsi (PORPROV) 2025", "daerah": "Bukittinggi", "kategori": "Artistik Putri", "grup": "Senior"},
    {"nama": "Citra Lestari2", "event": "Pekan Olahraga Provinsi (PORPROV) 2025", "daerah": "Padang", "kategori": "Artistik Putri", "grup": "Senior"},
    {"nama": "Citra Lestari3", "event": "Pekan Olahraga Provinsi (PORPROV) 2025", "daerah": "Agam", "kategori": "Artistik Putri", "grup": "Senior"},
    {"nama": "Dewi Anggraini", "event": "Pekan Olahraga Provinsi (PORPROV) 2025", "daerah": "Payakumbuh", "kategori": "Ritmik", "grup": "Senior"},
    
    # Peserta untuk Kejuaraan Daerah Junior 2025
    {"nama": "Rian Pratama", "event": "Kejuaraan Daerah Junior 2025", "daerah": "Solok", "kategori": "Artistik Putra", "grup": "Junior"},
    {"nama": "Rian Pratama2", "event": "Kejuaraan Daerah Junior 2025", "daerah": "Padang", "kategori": "Artistik Putra", "grup": "Junior"},
    {"nama": "Rian Pratama3", "event": "Kejuaraan Daerah Junior 2025", "daerah": "Agam", "kategori": "Artistik Putra", "grup": "Junior"},
    {"nama": "Rian Pratama4", "event": "Kejuaraan Daerah Junior 2025", "daerah": "Payakumbuh", "kategori": "Artistik Putra", "grup": "Junior"},
    {"nama": "Fitriani", "event": "Kejuaraan Daerah Junior 2025", "daerah": "Pariaman", "kategori": "Ritmik", "grup": "Junior"},
    {"nama": "Fitriani2", "event": "Kejuaraan Daerah Junior 2025", "daerah": "Padang", "kategori": "Ritmik", "grup": "Junior"},
    {"nama": "Fitriani3", "event": "Kejuaraan Daerah Junior 2025", "daerah": "Bukittinggi", "kategori": "Ritmik", "grup": "Junior"},
    {"nama": "Sari Indah", "event": "Kejuaraan Daerah Junior 2025", "daerah": "Agam", "kategori": "Ritmik", "grup": "Junior"},
]

def setup_database():
    with app.app_context():
        # Hapus semua tabel yang ada dan buat kembali dari awal
        print("Menghapus database lama...")
        db.drop_all()
        print("Membuat skema database baru...")
        db.create_all()

        # --- Pengisian Data Master Independen ---
        print("Memasukkan data master (Daerah, Kategori, Grup, Alat, Event)...")
        for nama_daerah in DAERAH_SUMBAR: db.session.add(Daerah(nama=nama_daerah))
        for nama_kategori in KATEGORI_LIST: db.session.add(Kategori(nama=nama_kategori))
        for nama_grup in GRUP_LIST: db.session.add(Grup(nama=nama_grup))
        for nama_alat in ALAT_LIST: db.session.add(Alat(nama=nama_alat))
        for event in EVENTS_CONTOH: db.session.add(Event(nama=event['nama'], tanggal=event['tanggal']))
        
        # Commit agar data master punya ID sebelum membuat data Peserta
        db.session.commit()
        print("Data master berhasil dimasukkan.")

        # --- Pengisian Data Peserta (Dependen) ---
        print("Memasukkan data peserta contoh...")
        for p_data in PESERTA_CONTOH:
            # Cari objek dari nama untuk mendapatkan ID-nya
            event_obj = Event.query.filter_by(nama=p_data['event']).first()
            daerah_obj = Daerah.query.filter_by(nama=p_data['daerah']).first()
            kategori_obj = Kategori.query.filter_by(nama=p_data['kategori']).first()
            grup_obj = Grup.query.filter_by(nama=p_data['grup']).first()

            if all([event_obj, daerah_obj, kategori_obj, grup_obj]):
                peserta_baru = Peserta(
                    nama=p_data['nama'],
                    event_id=event_obj.id,
                    daerah_id=daerah_obj.id,
                    kategori_id=kategori_obj.id,
                    grup_id=grup_obj.id
                )
                db.session.add(peserta_baru)
            else:
                print(f"WARNING: Gagal menambahkan peserta '{p_data['nama']}' karena salah satu data master tidak ditemukan.")
        
        # Commit data peserta
        db.session.commit()
        print("Data peserta berhasil dimasukkan.")

        print("\n" + "="*30)
        print("✅ SETUP BASIS DATA SELESAI ✅")
        print("="*30)
        print("Langkah selanjutnya: Jalankan 'python app.py', buka Menu Admin,")
        print("lalu aktifkan salah satu event untuk memulai.")

if __name__ == '__main__':
    setup_database()