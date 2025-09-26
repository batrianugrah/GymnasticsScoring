from app import app, db, Daerah, Peserta, Kategori, Grup, Alat
from sqlalchemy.exc import IntegrityError

# Data Master
DAERAH_SUMBAR = [
    "Agam", "Dharmasraya", "Kepulauan Mentawai", "Lima Puluh Kota", "Padang Pariaman",
    "Pasaman", "Pasaman Barat", "Pesisir Selatan", "Sijunjung", "Solok",
    "Solok Selatan", "Tanah Datar", "Bukittinggi", "Padang", "Padang Panjang",
    "Pariaman", "Payakumbuh", "Sawahlunto", "Solok"  # Duplikat "Solok"
]
KATEGORI_LIST = ["Artistik Putra", "Artistik Putri", "Ritmik", "Aerobik Gymnastic", "Senam Trampolin"]
GRUP_LIST = ["Pra Junior", "Junior", "Senior", "NG I", "NG II", "NG III", "AG 1", "AG 2"]
ALAT_LIST = [
    "Free Hand", "Floor Exercise", "Vaulting Table", "Pommel Horse", "Rings", 
    "Parallel Bars", "Horizontal Bar", "Uneven Bars", "Balance Beam",
    "Rope", "Hoop", "Ball", "Clubs", "Ribbon"
]
PESERTA_CONTOH = [
    {"nama": "Budi Santoso", "daerah": "Padang"},
    {"nama": "Citra Lestari", "daerah": "Bukittinggi"},
    {"nama": "Doni Firmansyah", "daerah": "Payakumbuh"},
    {"nama": "Eka Putri", "daerah": "Solok"},
]

def insert_unique(model, nama):
    """Insert data only if it doesn't already exist."""
    if not db.session.query(model).filter_by(nama=nama).first():
        db.session.add(model(nama=nama))

def insert_master_data():
    print("🗂️ Memasukkan data master...")

    for nama_daerah in set(DAERAH_SUMBAR):  # Hindari duplikat
        insert_unique(Daerah, nama_daerah)

    for nama_kategori in KATEGORI_LIST:
        insert_unique(Kategori, nama_kategori)

    for nama_grup in GRUP_LIST:
        insert_unique(Grup, nama_grup)

    for nama_alat in ALAT_LIST:
        insert_unique(Alat, nama_alat)

    try:
        db.session.commit()
        print("✅ Data master berhasil dimasukkan.")
    except IntegrityError as e:
        db.session.rollback()
        print("❌ Gagal memasukkan data master:", e)

def insert_peserta_data():
    print("👥 Memasukkan data peserta...")

    for p in PESERTA_CONTOH:
        daerah_obj = Daerah.query.filter_by(nama=p['daerah']).first()
        if daerah_obj:
            if not db.session.query(Peserta).filter_by(nama=p['nama'], daerah_id=daerah_obj.id).first():
                db.session.add(Peserta(nama=p['nama'], daerah_id=daerah_obj.id))
        else:
            print(f"⚠️ Daerah '{p['daerah']}' tidak ditemukan untuk peserta '{p['nama']}'.")

    try:
        db.session.commit()
        print("✅ Data peserta berhasil dimasukkan.")
    except IntegrityError as e:
        db.session.rollback()
        print("❌ Gagal memasukkan data peserta:", e)

def setup_database():
    with app.app_context():
        print("🔄 Menginisialisasi ulang basis data...")
        db.drop_all()
        db.create_all()

        insert_master_data()
        insert_peserta_data()

        print("="*30)
        print("🎉 Setup basis data selesai!")
        print("="*30)

if __name__ == '__main__':
    setup_database()
