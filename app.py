import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# --- Konfigurasi Dasar (Tidak Berubah) ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'gymnastics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kunci-rahasia-untuk-flash-message' # Diperlukan untuk flash message
db = SQLAlchemy(app)

# --- Model Basis Data (Tidak Berubah) ---
class Daerah(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)

class Peserta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    daerah_id = db.Column(db.Integer, db.ForeignKey('daerah.id'), nullable=False)
    daerah = db.relationship('Daerah', backref=db.backref('peserta', lazy=True, cascade="all, delete-orphan"))

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
    sesi_pertandingan = db.Column(db.String(100), default="current")
    peserta = db.relationship('Peserta')
    kategori = db.relationship('Kategori')
    grup = db.relationship('Grup')
    alat = db.relationship('Alat')


# --- Halaman & Logika Publik (Tidak banyak berubah) ---

@app.route('/', methods=['GET', 'POST'])
def input_skor():
    if request.method == 'POST':
        # (Logika POST tidak berubah)
        peserta_id = request.form.get('peserta')
        kategori_id = request.form.get('kategori')
        grup_id = request.form.get('grup')
        alat_id = request.form.get('alat')
        try:
            nilai_d = float(request.form.get('nilai_d', 0))
            nilai_e = float(request.form.get('nilai_e', 0))
            nilai_a = float(request.form.get('nilai_a', 0))
            penalti = float(request.form.get('penalti', 0))
        except (ValueError, TypeError):
             return "Error: Pastikan semua nilai adalah angka.", 400
        total = (nilai_d + nilai_e + nilai_a) - penalti
        skor_baru = Skor(
            peserta_id=peserta_id, kategori_id=kategori_id, grup_id=grup_id,
            alat_id=alat_id, nilai_d=nilai_d, nilai_e=nilai_e, nilai_a=nilai_a,
            penalti=penalti, total_nilai=total
        )
        db.session.add(skor_baru)
        db.session.commit()
        return redirect(url_for('input_skor'))

    master_data = {
        'peserta': Peserta.query.order_by(Peserta.nama).all(),
        'daerah': Daerah.query.order_by(Daerah.nama).all(),
        'kategori': Kategori.query.order_by(Kategori.nama).all(),
        'grup': Grup.query.order_by(Grup.nama).all(),
        'alat': Alat.query.order_by(Alat.nama).all()
    }
    ranking_sementara = Skor.query.filter_by(sesi_pertandingan="current").order_by(Skor.total_nilai.desc()).all()
    return render_template('input_skor.html', data=master_data, ranking=ranking_sementara)

@app.route('/live')
def live_view():
    return render_template('live_view.html')

@app.route('/api/scores')
def api_scores():
    # (Fungsi API tidak berubah)
    skor_terkini = Skor.query.filter_by(sesi_pertandingan="current").order_by(Skor.total_nilai.desc()).all()
    output = []
    for i, s in enumerate(skor_terkini):
        output.append({
            'rank': i + 1, 'nama_peserta': s.peserta.nama, 'nama_daerah': s.peserta.daerah.nama,
            'kategori': s.kategori.nama, 'grup': s.grup.nama, 'alat': s.alat.nama,
            'nilai_d': f"{s.nilai_d:.3f}", 'nilai_e': f"{s.nilai_e:.3f}", 'nilai_a': f"{s.nilai_a:.3f}",
            'penalti': f"{s.penalti:.3f}", 'total_nilai': f"{s.total_nilai:.3f}"
        })
    return jsonify(output)

@app.route('/reset', methods=['POST'])
def reset_skor():
    # (Fungsi reset tidak berubah)
    nama_sesi_baru = f"Sesi {func.strftime('%Y-%m-%d %H:%M:%S', func.now())}"
    Skor.query.filter_by(sesi_pertandingan="current").update({"sesi_pertandingan": nama_sesi_baru})
    db.session.commit()
    return redirect(url_for('input_skor'))

@app.route('/history')
def riwayat():
    # (Fungsi riwayat tidak berubah)
    sesi_unik = db.session.query(Skor.sesi_pertandingan).filter(Skor.sesi_pertandingan != "current").distinct().all()
    riwayat_skor = {}
    for sesi in sesi_unik:
        nama_sesi = sesi[0]
        skor_sesi = Skor.query.filter_by(sesi_pertandingan=nama_sesi).order_by(Skor.total_nilai.desc()).all()
        riwayat_skor[nama_sesi] = skor_sesi
    return render_template('riwayat.html', riwayat=riwayat_skor)

# =====================================================================
# --- AREA ADMIN - BAGIAN BARU ---
# =====================================================================

@app.route('/admin')
def admin_dashboard():
    """ Halaman utama untuk admin. """
    return render_template('admin_dashboard.html')

# --- Fungsi Generik untuk Mengelola Data Master Sederhana ---
def get_model_map():
    return {
        'daerah': {'model': Daerah, 'title': 'Daerah'},
        'kategori': {'model': Kategori, 'title': 'Kategori'},
        'grup': {'model': Grup, 'title': 'Grup'},
        'alat': {'model': Alat, 'title': 'Alat'}
    }

@app.route('/admin/manage/<master_type>', methods=['GET', 'POST'])
def admin_manage_generic(master_type):
    model_map = get_model_map()
    if master_type not in model_map:
        return "Tipe data tidak valid", 404

    config = model_map[master_type]
    Model = config['model']
    
    if request.method == 'POST':
        nama_baru = request.form.get('nama')
        if nama_baru:
            # Cek duplikasi
            if not Model.query.filter_by(nama=nama_baru).first():
                item_baru = Model(nama=nama_baru)
                db.session.add(item_baru)
                db.session.commit()
                flash(f"{config['title']} '{nama_baru}' berhasil ditambahkan.", "success")
            else:
                flash(f"{config['title']} '{nama_baru}' sudah ada.", "warning")
        else:
            flash("Nama tidak boleh kosong.", "danger")
        return redirect(url_for('admin_manage_generic', master_type=master_type))

    items = Model.query.order_by(Model.nama).all()
    return render_template('admin_manage_generic.html', items=items, config=config, master_type=master_type)

@app.route('/admin/delete/<master_type>/<int:item_id>', methods=['POST'])
def admin_delete_generic(master_type, item_id):
    model_map = get_model_map()
    if master_type not in model_map:
        return "Tipe data tidak valid", 404
        
    config = model_map[master_type]
    Model = config['model']
    
    item = Model.query.get_or_404(item_id)
    nama_item = item.nama
    db.session.delete(item)
    db.session.commit()
    flash(f"{config['title']} '{nama_item}' berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_generic', master_type=master_type))

# --- Fungsi Spesifik untuk Mengelola Data Peserta ---
@app.route('/admin/manage/peserta', methods=['GET', 'POST'])
def admin_manage_peserta():
    if request.method == 'POST':
        nama_peserta = request.form.get('nama')
        daerah_id = request.form.get('daerah_id')
        
        if nama_peserta and daerah_id:
            peserta_baru = Peserta(nama=nama_peserta, daerah_id=daerah_id)
            db.session.add(peserta_baru)
            db.session.commit()
            flash(f"Peserta '{nama_peserta}' berhasil ditambahkan.", "success")
        else:
            flash("Nama peserta dan daerah tidak boleh kosong.", "danger")
        return redirect(url_for('admin_manage_peserta'))

    peserta_list = Peserta.query.order_by(Peserta.nama).all()
    daerah_list = Daerah.query.order_by(Daerah.nama).all()
    return render_template('admin_manage_peserta.html', peserta_list=peserta_list, daerah_list=daerah_list)

@app.route('/admin/delete/peserta/<int:peserta_id>', methods=['POST'])
def admin_delete_peserta(peserta_id):
    peserta = Peserta.query.get_or_404(peserta_id)
    nama_peserta = peserta.nama
    db.session.delete(peserta)
    db.session.commit()
    flash(f"Peserta '{nama_peserta}' berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_peserta'))
    

# --- Main execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')