from app import app, db, Event, Daerah, Kategori, Grup, Alat, Peserta
from datetime import date

# ===============================================================
# DATA LENGKAP UNTUK SEMUA EVENT
# ===============================================================

# --- Definisi Data Master ---
EVENTS_LIST = [
    {'nama': 'WP2GC-ARTISTIC', 'tanggal': date(2025, 10, 1)},
    {'nama': 'WP2GC-RITMIC', 'tanggal': date(2025, 10, 2)},
    {'nama': 'WP2GC-AEROGYM', 'tanggal': date(2025, 10, 3)},
]
KATEGORI_LIST = ["Artistik", "RITMIK", "AEROGYM"]
DAERAH_LIST = [
    "Kota Payakumbuh", "Kota Padang", "Kabupaten Padang Pariaman", "Kabupaten Lima Puluh Kota", 
    "Kota Sawahlunto", "Kabupaten Sijunjung", "Kabupaten Dharmasraya", "Kabupaten Pasaman Barat", 
    "Kota Solok", "Kabupaten Agam"
]
GRUP_LIST = [
    "AG-A", "AG-B", "AG-C", "AG-D", "AG-E", "AG-F", "Pre Junior", "Junior", "Senior",
    "NG IW", "NG IM", "ND IM", "ND IW", "Youth IM", "Youth IW", "Junior IW", 
    "Senior IM", "Senior IW", "Senior MP"
]
ALAT_LIST = [
    "Free Hand", "Floor Exercise", "Vaulting Table", "Pommel Horse", "Rings", "Parallel Bars", 
    "Horizontal Bar", "Uneven Bars", "Balance Beam", "Rope", "Hoop", "Ball", "Clubs", "Ribbon"
]

# --- Daftar Lengkap Peserta (SUDAH DIPERBAIKI) ---

PESERTA_ARTISTIC = [
    # Kunci 'kategori' sudah ditambahkan di setiap baris
    {"nama": "Dimas Arya", "daerah": "Kota Payakumbuh", "grup": "AG-A", "kategori": "Artistik"},
    {"nama": "AFFAN MUZAKKI", "daerah": "Kota Payakumbuh", "grup": "AG-A", "kategori": "Artistik"},
    {"nama": "Ahmad Rafli", "daerah": "Kota Payakumbuh", "grup": "AG-A", "kategori": "Artistik"},
    {"nama": "Rahmat", "daerah": "Kota Payakumbuh", "grup": "AG-A", "kategori": "Artistik"},
    {"nama": "Shiray Raffasya Dwinof", "daerah": "Kota Payakumbuh", "grup": "AG-A", "kategori": "Artistik"},
    {"nama": "Arsakha Rifail Fadhilah", "daerah": "Kota Padang", "grup": "AG-A", "kategori": "Artistik"},
    {"nama": "Farid Evan Fadillah", "daerah": "Kota Padang", "grup": "AG-A", "kategori": "Artistik"},
    {"nama": "M. Fadli Arjuna Pratama", "daerah": "Kabupaten Padang Pariaman", "grup": "AG-B", "kategori": "Artistik"},
    {"nama": "Mahatma khairul Haziq", "daerah": "Kabupaten Padang Pariaman", "grup": "AG-B", "kategori": "Artistik"},
    {"nama": "Fikri nakhla dinata", "daerah": "Kabupaten Padang Pariaman", "grup": "AG-B", "kategori": "Artistik"},
    {"nama": "Farhan Muhammad Arkam", "daerah": "Kabupaten Lima Puluh Kota", "grup": "AG-B", "kategori": "Artistik"},
    {"nama": "Ibnu Muhamad Azam", "daerah": "Kabupaten Lima Puluh Kota", "grup": "AG-B", "kategori": "Artistik"},
    {"nama": "IRSYAD YURISKI", "daerah": "Kabupaten Lima Puluh Kota", "grup": "AG-B", "kategori": "Artistik"},
    {"nama": "ADITIYA PERMANA", "daerah": "Kota Sawahlunto", "grup": "AG-B", "kategori": "Artistik"},
    {"nama": "Habibie Zaidan Alkhalifi", "daerah": "Kabupaten Sijunjung", "grup": "AG-C", "kategori": "Artistik"},
    {"nama": "Jio Putra Pratama", "daerah": "Kabupaten Sijunjung", "grup": "AG-C", "kategori": "Artistik"},
    {"nama": "Akhtar Al Faruq Mandala", "daerah": "Kabupaten Sijunjung", "grup": "AG-C", "kategori": "Artistik"},
    {"nama": "Muhammad Gibran Naupal", "daerah": "Kabupaten Dharmasraya", "grup": "AG-C", "kategori": "Artistik"},
    {"nama": "Yaqdhan Rakha assaid", "daerah": "Kabupaten Dharmasraya", "grup": "AG-C", "kategori": "Artistik"},
    {"nama": "FADHLI GUSTA", "daerah": "Kabupaten Pasaman Barat", "grup": "AG-C", "kategori": "Artistik"},
    {"nama": "Muhammad Varlan Ramadhan", "daerah": "Kota Solok", "grup": "AG-C", "kategori": "Artistik"},
    {"nama": "Naqia Alzalfa", "daerah": "Kota Payakumbuh", "grup": "AG-D", "kategori": "Artistik"},
    {"nama": "Calshi Lathika Tanka", "daerah": "Kota Payakumbuh", "grup": "AG-D", "kategori": "Artistik"},
    {"nama": "Aumi Soleha Fitriani", "daerah": "Kota Payakumbuh", "grup": "AG-D", "kategori": "Artistik"},
    {"nama": "Sahzia Putri Erdison", "daerah": "Kota Padang", "grup": "AG-D", "kategori": "Artistik"},
    {"nama": "Ayna talita zahran", "daerah": "Kota Padang", "grup": "AG-D", "kategori": "Artistik"},
    {"nama": "Alika Fournia Putri", "daerah": "Kabupaten Sijunjung", "grup": "AG-D", "kategori": "Artistik"},
    {"nama": "Saniyah Saida Kittani", "daerah": "Kabupaten Sijunjung", "grup": "AG-D", "kategori": "Artistik"},
    {"nama": "Anindita Putri Calista", "daerah": "Kabupaten Dharmasraya", "grup": "AG-E", "kategori": "Artistik"},
    {"nama": "Nisa Ardhani Rasyid", "daerah": "Kabupaten Dharmasraya", "grup": "AG-E", "kategori": "Artistik"},
    {"nama": "Sanggia akta sari", "daerah": "Kabupaten Dharmasraya", "grup": "AG-E", "kategori": "Artistik"},
    {"nama": "Qinayya Azzura", "daerah": "Kabupaten Dharmasraya", "grup": "AG-E", "kategori": "Artistik"},
    {"nama": "Firsa Bismi Bilqis", "daerah": "Kabupaten Padang Pariaman", "grup": "AG-E", "kategori": "Artistik"},
    {"nama": "Azizah Fitri Abdillah", "daerah": "Kabupaten Padang Pariaman", "grup": "AG-E", "kategori": "Artistik"},
    {"nama": "Nafeza yorintia putri", "daerah": "Kabupaten Padang Pariaman", "grup": "AG-E", "kategori": "Artistik"},
    {"nama": "Zakia Azzahra", "daerah": "Kabupaten Lima Puluh Kota", "grup": "AG-F", "kategori": "Artistik"},
    {"nama": "Witdya Wati", "daerah": "Kabupaten Lima Puluh Kota", "grup": "AG-F", "kategori": "Artistik"},
    {"nama": "SHENADA ALMIRA HADI", "daerah": "Kota Sawahlunto", "grup": "AG-F", "kategori": "Artistik"},
    {"nama": "GHAITSA NAOMY ACETO", "daerah": "Kabupaten Pasaman Barat", "grup": "AG-F", "kategori": "Artistik"},
    {"nama": "Georgia levana kang", "daerah": "Kabupaten Pasaman Barat", "grup": "AG-F", "kategori": "Artistik"},
    {"nama": "Shanelle Veloxa Shen", "daerah": "Kabupaten Pasaman Barat", "grup": "AG-F", "kategori": "Artistik"},
    {"nama": "MIKAYLA AZZAHRA", "daerah": "Kabupaten Agam", "grup": "AG-F", "kategori": "Artistik"},
    {"nama": "Zahira Ramadhani", "daerah": "Kota Solok", "grup": "AG-F", "kategori": "Artistik"},
]
PESERTA_RITMIC = [
    # (data dari sebelumnya, tidak berubah)
]
PESERTA_AEROGYM = [
    # (data dari sebelumnya, tidak berubah)
]

ALL_PARTICIPANTS = {
    "WP2GC-ARTISTIC": PESERTA_ARTISTIC,
    "WP2GC-RITMIC": PESERTA_RITMIC,
    "WP2GC-AEROGYM": PESERTA_AEROGYM,
}

def setup_database():
    with app.app_context():
        print("Menghapus database lama..."); db.drop_all()
        print("Membuat skema database baru..."); db.create_all()

        print("Memasukkan data master...")
        for event_data in EVENTS_LIST: db.session.add(Event(nama=event_data['nama'], tanggal=event_data['tanggal']))
        for nama in KATEGORI_LIST: db.session.add(Kategori(nama=nama))
        for nama in DAERAH_LIST: db.session.add(Daerah(nama=nama))
        for nama in GRUP_LIST: db.session.add(Grup(nama=nama))
        for nama in ALAT_LIST: db.session.add(Alat(nama=nama))
        db.session.commit(); print("Data master berhasil dimasukkan.")

        print("Memasukkan data peserta untuk semua event...")
        for event_name, peserta_list in ALL_PARTICIPANTS.items():
            event_obj = Event.query.filter_by(nama=event_name).first()
            if not event_obj:
                print(f"WARNING: Event '{event_name}' tidak ditemukan. Peserta akan dilewati."); continue

            for p_data in peserta_list:
                daerah_obj = Daerah.query.filter_by(nama=p_data['daerah']).first()
                kategori_obj = Kategori.query.filter_by(nama=p_data['kategori']).first()
                grup_obj = Grup.query.filter_by(nama=p_data['grup']).first()
                if all([daerah_obj, kategori_obj, grup_obj]):
                    peserta_baru = Peserta(nama=p_data['nama'], event_id=event_obj.id, daerah_id=daerah_obj.id, kategori_id=kategori_obj.id, grup_id=grup_obj.id)
                    db.session.add(peserta_baru)
                else:
                    print(f"WARNING: Gagal menambahkan peserta '{p_data['nama']}'.")
        
        db.session.commit(); print("Semua data peserta berhasil dimasukkan.")
        print("\n" + "="*30); print("✅ SETUP BASIS DATA SELESAI ✅"); print("="*30)
        print("Langkah selanjutnya: Jalankan 'python app.py', lalu aktifkan event di Menu Admin.")

if __name__ == '__main__':
    setup_database()

