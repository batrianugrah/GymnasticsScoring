# export_data.py

import pandas as pd
from app import app, Event, Daerah, Kategori, Grup, Alat, Peserta

def export_all_data():
    """
    Membaca semua data master dari database dan menyimpannya ke file Excel.
    """
    output_filename = 'backup_data.xlsx'

    with app.app_context():
        print("Memulai proses ekspor data...")

        # Buat writer Excel untuk menyimpan beberapa sheet
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            # 1. Ekspor Data Peserta (paling penting)
            print("Mengekspor data Peserta...")
            peserta_query = Peserta.query.all()
            if peserta_query:
                peserta_data = [{
                    'Nama Peserta': p.nama,
                    'Nama Daerah': p.daerah.nama,
                    'Nama Kategori': p.kategori.nama,
                    'Nama Grup': p.grup.nama,
                    'Nama Event': p.event.nama
                } for p in peserta_query]
                df_peserta = pd.DataFrame(peserta_data)
                df_peserta.to_excel(writer, sheet_name='Peserta', index=False)

            # 2. Ekspor data master lainnya
            print("Mengekspor data master lainnya...")
            pd.DataFrame([{'nama': d.nama} for d in Daerah.query.all()]).to_excel(writer, sheet_name='Daerah', index=False)
            pd.DataFrame([{'nama': k.nama} for k in Kategori.query.all()]).to_excel(writer, sheet_name='Kategori', index=False)
            pd.DataFrame([{'nama': g.nama} for g in Grup.query.all()]).to_excel(writer, sheet_name='Grup', index=False)
            pd.DataFrame([{'nama': a.nama} for a in Alat.query.all()]).to_excel(writer, sheet_name='Alat', index=False)
            pd.DataFrame([{'nama': e.nama, 'tanggal': e.tanggal} for e in Event.query.all()]).to_excel(writer, sheet_name='Event', index=False)

        print(f"\n✅ Ekspor Selesai! Data Anda telah disimpan di '{output_filename}'")

if __name__ == '__main__':
    export_all_data()