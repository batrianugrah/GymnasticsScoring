import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# Konfigurasi Dasar
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'gymnastics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kunci-rahasia-yang-aman-untuk-flash-message'
db = SQLAlchemy(app)

# --- Model Basis Data ---
class Daerah(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)

class Kategori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)

class Grup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)

class Alat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)

class Peserta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    daerah_id = db.Column(db.Integer, db.ForeignKey('daerah.id'), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=False)
    grup_id = db.Column(db.Integer, db.ForeignKey('grup.id'), nullable=False)
    
    daerah = db.relationship('Daerah', backref=db.backref('peserta', lazy=True, cascade="all, delete-orphan"))
    kategori = db.relationship('Kategori', backref=db.backref('peserta', lazy=True))
    grup = db.relationship('Grup', backref=db.backref('peserta', lazy=True))
    
    __table_args__ = {'extend_existing': True}

class Skor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    peserta_id = db.Column(db.Integer, db.ForeignKey('peserta.id'), nullable=False)
    alat_id = db.Column(db.Integer, db.ForeignKey('alat.id'), nullable=False)
    nilai_d = db.Column(db.Float, nullable=False, default=0.0)
    nilai_e = db.Column(db.Float, nullable=False, default=0.0)
    nilai_a = db.Column(db.Float, nullable=False, default=0.0)
    penalti = db.Column(db.Float, nullable=False, default=0.0)
    total_nilai = db.Column(db.Float, nullable=False, default=0.0)
    waktu_input = db.Column(db.DateTime, server_default=func.now())
    sesi_pertandingan = db.Column(db.String(100), default="current")

    peserta = db.relationship('Peserta')
    alat = db.relationship('Alat')
    
    # Menambahkan relasi ke kategori dan grup untuk kemudahan akses di template
    @property
    def kategori(self):
        return self.peserta.kategori

    @property
    def grup(self):
        return self.peserta.grup


# --- Rute Publik dan Input Skor ---
@app.route('/', methods=['GET', 'POST'])
def input_skor():
    if request.method == 'POST':
        peserta_id = request.form.get('peserta')
        alat_id = request.form.get('alat')
        
        if not all([peserta_id, alat_id]):
            flash("Peserta dan Alat harus dipilih.", "danger")
            return redirect(url_for('input_skor'))
            
        try:
            nilai_d = float(request.form.get('nilai_d', 0))
            nilai_e = float(request.form.get('nilai_e', 0))
            nilai_a = float(request.form.get('nilai_a', 0))
            penalti = float(request.form.get('penalti', 0))
        except (ValueError, TypeError):
             flash("Nilai harus berupa angka.", "danger")
             return redirect(url_for('input_skor'))

        total = (nilai_d + nilai_e + nilai_a) - penalti
        skor_baru = Skor(
            peserta_id=peserta_id, alat_id=alat_id, nilai_d=nilai_d, nilai_e=nilai_e,
            nilai_a=nilai_a, penalti=penalti, total_nilai=total
        )
        db.session.add(skor_baru)
        db.session.commit()
        return redirect(url_for('input_skor'))

    master_data = {
        'kategori': Kategori.query.order_by(Kategori.nama).all(),
        'alat': Alat.query.order_by(Alat.nama).all()
    }
    ranking_sementara = Skor.query.filter_by(sesi_pertandingan="current").order_by(Skor.total_nilai.desc()).all()
    return render_template('input_skor.html', data=master_data, ranking=ranking_sementara)

@app.route('/edit_skor/<int:skor_id>', methods=['GET', 'POST'])
def edit_skor(skor_id):
    skor_to_edit = Skor.query.get_or_404(skor_id)
    if request.method == 'POST':
        try:
            skor_to_edit.nilai_d = float(request.form.get('nilai_d', 0))
            skor_to_edit.nilai_e = float(request.form.get('nilai_e', 0))
            skor_to_edit.nilai_a = float(request.form.get('nilai_a', 0))
            skor_to_edit.penalti = float(request.form.get('penalti', 0))
            skor_to_edit.total_nilai = (skor_to_edit.nilai_d + skor_to_edit.nilai_e + skor_to_edit.nilai_a) - skor_to_edit.penalti
            db.session.commit()
            flash('Skor berhasil diperbarui!', 'success')
            return redirect(url_for('input_skor'))
        except (ValueError, TypeError):
            flash('Input tidak valid. Pastikan semua nilai adalah angka.', 'danger')
            return redirect(url_for('edit_skor', skor_id=skor_id))
    return render_template('edit_skor.html', skor=skor_to_edit)

@app.route('/live')
def live_view():
    return render_template('live_view.html')

@app.route('/history')
def riwayat():
    sesi_unik = db.session.query(Skor.sesi_pertandingan).filter(Skor.sesi_pertandingan != "current").distinct().all()
    riwayat_skor = {}
    for sesi in sesi_unik:
        nama_sesi = sesi[0]
        skor_sesi = Skor.query.filter_by(sesi_pertandingan=nama_sesi).order_by(Skor.total_nilai.desc()).all()
        riwayat_skor[nama_sesi] = skor_sesi
    return render_template('riwayat.html', riwayat=riwayat_skor)

@app.route('/reset', methods=['POST'])
def reset_skor():
    nama_sesi_baru = f"Sesi {func.strftime('%Y-%m-%d %H:%M:%S', func.now())}"
    Skor.query.filter_by(sesi_pertandingan="current").update({"sesi_pertandingan": nama_sesi_baru})
    db.session.commit()
    flash('Sesi baru telah dimulai! Skor sebelumnya telah diarsipkan.', 'info')
    return redirect(url_for('input_skor'))


# --- API Endpoints ---
@app.route('/api/scores')
def api_scores():
    skor_terkini = Skor.query.filter_by(sesi_pertandingan="current").order_by(Skor.total_nilai.desc()).all()
    output = []
    for i, s in enumerate(skor_terkini):
        output.append({
            'rank': i + 1, 'nama_peserta': s.peserta.nama, 'nama_daerah': s.peserta.daerah.nama,
            'kategori': s.peserta.kategori.nama, 'grup': s.peserta.grup.nama, 'alat': s.alat.nama,
            'nilai_d': f"{s.nilai_d:.3f}", 'nilai_e': f"{s.nilai_e:.3f}", 'nilai_a': f"{s.nilai_a:.3f}",
            'penalti': f"{s.penalti:.3f}", 'total_nilai': f"{s.total_nilai:.3f}"
        })
    return jsonify(output)

@app.route('/api/grup_by_kategori/<int:kategori_id>')
def api_grup_by_kategori(kategori_id):
    peserta_in_kategori = Peserta.query.filter_by(kategori_id=kategori_id).all()
    grup_ids = {p.grup_id for p in peserta_in_kategori}
    if not grup_ids:
        return jsonify([])
    grups = Grup.query.filter(Grup.id.in_(grup_ids)).order_by(Grup.nama).all()
    grup_array = [{'id': g.id, 'nama': g.nama} for g in grups]
    return jsonify(grup_array)

@app.route('/api/peserta_by_grup/<int:kategori_id>/<int:grup_id>')
def api_peserta_by_grup(kategori_id, grup_id):
    pesertas = Peserta.query.filter_by(kategori_id=kategori_id, grup_id=grup_id).order_by(Peserta.nama).all()
    peserta_array = [{'id': p.id, 'nama': p.nama, 'daerah': p.daerah.nama} for p in pesertas]
    return jsonify(peserta_array)


# --- Area Admin ---
@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

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
    if master_type not in model_map: return "Tipe data tidak valid", 404
    config = model_map[master_type]
    Model = config['model']
    
    if request.method == 'POST':
        nama_baru = request.form.get('nama')
        if nama_baru:
            if not Model.query.filter_by(nama=nama_baru).first():
                db.session.add(Model(nama=nama_baru))
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
    if master_type not in model_map: return "Tipe data tidak valid", 404
    config = model_map[master_type]
    Model = config['model']
    item = Model.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f"{config['title']} '{item.nama}' berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_generic', master_type=master_type))

@app.route('/admin/manage/peserta', methods=['GET', 'POST'])
def admin_manage_peserta():
    if request.method == 'POST':
        nama_peserta = request.form.get('nama')
        daerah_id = request.form.get('daerah_id')
        kategori_id = request.form.get('kategori_id')
        grup_id = request.form.get('grup_id')
        if all([nama_peserta, daerah_id, kategori_id, grup_id]):
            db.session.add(Peserta(nama=nama_peserta, daerah_id=daerah_id, kategori_id=kategori_id, grup_id=grup_id))
            db.session.commit()
            flash(f"Peserta '{nama_peserta}' berhasil ditambahkan.", "success")
        else:
            flash("Semua field wajib diisi.", "danger")
        return redirect(url_for('admin_manage_peserta'))

    return render_template('admin_manage_peserta.html', 
        peserta_list=Peserta.query.order_by(Peserta.nama).all(), 
        daerah_list=Daerah.query.order_by(Daerah.nama).all(),
        kategori_list=Kategori.query.order_by(Kategori.nama).all(),
        grup_list=Grup.query.order_by(Grup.nama).all()
    )

@app.route('/admin/delete/peserta/<int:peserta_id>', methods=['POST'])
def admin_delete_peserta(peserta_id):
    peserta = Peserta.query.get_or_404(peserta_id)
    db.session.delete(peserta)
    db.session.commit()
    flash(f"Peserta '{peserta.nama}' berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_peserta'))
    
# --- Main execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')