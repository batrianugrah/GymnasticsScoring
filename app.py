import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# Konfigurasi Dasar Aplikasi
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'gymnastics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Model Basis Data (Struktur Data Master & Skor) ---

class Daerah(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)

class Peserta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    daerah_id = db.Column(db.Integer, db.ForeignKey('daerah.id'), nullable=False)
    daerah = db.relationship('Daerah', backref=db.backref('peserta', lazy=True))

class Kategori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)

class Grup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)

class Alat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)

class Skor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    peserta_id = db.Column(db.Integer, db.ForeignKey('peserta.id'), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=False)
    grup_id = db.Column(db.Integer, db.ForeignKey('grup.id'), nullable=False)
    alat_id = db.Column(db.Integer, db.ForeignKey('alat.id'), nullable=False)
    
    nilai_d = db.Column(db.Float, nullable=False, default=0.0)
    nilai_e = db.Column(db.Float, nullable=False, default=0.0)
    nilai_a = db.Column(db.Float, nullable=False, default=0.0)
    penalti = db.Column(db.Float, nullable=False, default=0.0)
    
    total_nilai = db.Column(db.Float, nullable=False, default=0.0)
    waktu_input = db.Column(db.DateTime, server_default=func.now())
    sesi_pertandingan = db.Column(db.String(100), default="current") # Untuk memisahkan riwayat

    peserta = db.relationship('Peserta')
    kategori = db.relationship('Kategori')
    grup = db.relationship('Grup')
    alat = db.relationship('Alat')

# --- Halaman & Logika Aplikasi (Routing) ---

@app.route('/', methods=['GET', 'POST'])
def input_skor():
    """ Halaman utama untuk menginput skor. """
    if request.method == 'POST':
        # Ambil data dari form
        peserta_id = request.form.get('peserta')
        kategori_id = request.form.get('kategori')
        grup_id = request.form.get('grup')
        alat_id = request.form.get('alat')
        
        # Konversi nilai ke float, default 0 jika kosong
        try:
            nilai_d = float(request.form.get('nilai_d', 0))
            nilai_e = float(request.form.get('nilai_e', 0))
            nilai_a = float(request.form.get('nilai_a', 0))
            penalti = float(request.form.get('penalti', 0))
        except (ValueError, TypeError):
             return "Error: Pastikan semua nilai adalah angka.", 400

        # Hitung total nilai
        total = (nilai_d + nilai_e + nilai_a) - penalti
        
        # Buat objek skor baru dan simpan ke DB
        skor_baru = Skor(
            peserta_id=peserta_id,
            kategori_id=kategori_id,
            grup_id=grup_id,
            alat_id=alat_id,
            nilai_d=nilai_d,
            nilai_e=nilai_e,
            nilai_a=nilai_a,
            penalti=penalti,
            total_nilai=total
        )
        db.session.add(skor_baru)
        db.session.commit()
        
        return redirect(url_for('input_skor'))

    # Jika method GET, tampilkan form dengan data master
    master_data = {
        'peserta': Peserta.query.order_by(Peserta.nama).all(),
        'daerah': Daerah.query.order_by(Daerah.nama).all(),
        'kategori': Kategori.query.order_by(Kategori.nama).all(),
        'grup': Grup.query.order_by(Grup.nama).all(),
        'alat': Alat.query.order_by(Alat.nama).all()
    }
    
    # Ambil data skor saat ini untuk ranking sementara
    ranking_sementara = Skor.query.filter_by(sesi_pertandingan="current").order_by(Skor.total_nilai.desc()).all()
    
    return render_template('input_skor.html', data=master_data, ranking=ranking_sementara)

@app.route('/live')
def live_view():
    """ Halaman yang akan dilihat oleh penonton. """
    return render_template('live_view.html')

@app.route('/api/scores')
def api_scores():
    """ API endpoint untuk menyediakan data skor terbaru dalam format JSON. """
    skor_terkini = Skor.query.filter_by(sesi_pertandingan="current").order_by(Skor.total_nilai.desc()).all()
    
    # Ubah data menjadi format yang mudah dibaca oleh JavaScript
    output = []
    for i, s in enumerate(skor_terkini):
        output.append({
            'rank': i + 1,
            'nama_peserta': s.peserta.nama,
            'nama_daerah': s.peserta.daerah.nama,
            'kategori': s.kategori.nama,
            'grup': s.grup.nama,
            'alat': s.alat.nama,
            'nilai_d': f"{s.nilai_d:.3f}",
            'nilai_e': f"{s.nilai_e:.3f}",
            'nilai_a': f"{s.nilai_a:.3f}",
            'penalti': f"{s.penalti:.3f}",
            'total_nilai': f"{s.total_nilai:.3f}"
        })
    return jsonify(output)

@app.route('/reset', methods=['POST'])
def reset_skor():
    """ Fungsi untuk mereset skor pertandingan saat ini. """
    # Improvisasi: Arsipkan skor lama sebelum menghapus
    nama_sesi_baru = f"Sesi {func.strftime('%Y-%m-%d %H:%M:%S', func.now())}"
    Skor.query.filter_by(sesi_pertandingan="current").update({"sesi_pertandingan": nama_sesi_baru})
    db.session.commit()
    return redirect(url_for('input_skor'))

@app.route('/history')
def riwayat():
    """ Halaman untuk menampilkan riwayat skor dari sesi-sesi sebelumnya. """
    # Ambil semua nama sesi yang unik (selain "current")
    sesi_unik = db.session.query(Skor.sesi_pertandingan).filter(Skor.sesi_pertandingan != "current").distinct().all()
    
    # Buat dictionary untuk menampung skor per sesi
    riwayat_skor = {}
    for sesi in sesi_unik:
        nama_sesi = sesi[0]
        skor_sesi = Skor.query.filter_by(sesi_pertandingan=nama_sesi).order_by(Skor.total_nilai.desc()).all()
        riwayat_skor[nama_sesi] = skor_sesi
        
    return render_template('riwayat.html', riwayat=riwayat_skor)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Buat tabel jika belum ada
    app.run(debug=True, host='0.0.0.0')