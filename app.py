import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from dateutil.parser import parse as parse_date

# --- Konfigurasi Dasar ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'gymnastics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kunci-rahasia-untuk-proyek-ini'
db = SQLAlchemy(app)


# --- MODEL DATABASE (DENGAN MANAJEMEN EVENT) ---

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

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
    # -- MODIFIKASI: Tambah event_id --
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    daerah_id = db.Column(db.Integer, db.ForeignKey('daerah.id'), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=False)
    grup_id = db.Column(db.Integer, db.ForeignKey('grup.id'), nullable=False)
    
    event = db.relationship('Event', backref=db.backref('peserta', lazy=True, cascade="all, delete"))
    daerah = db.relationship('Daerah', backref=db.backref('peserta', lazy=True))
    kategori = db.relationship('Kategori', backref=db.backref('peserta', lazy=True))
    grup = db.relationship('Grup', backref=db.backref('peserta', lazy=True))
    __table_args__ = {'extend_existing': True}

class Skor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    peserta_id = db.Column(db.Integer, db.ForeignKey('peserta.id'), nullable=False)
    alat_id = db.Column(db.Integer, db.ForeignKey('alat.id'), nullable=False)
    nilai_d = db.Column(db.Float, nullable=False, default=0.0)
    nilai_e = db.Column(db.Float, nullable=False, default=0.0)
    nilai_a = db.Column(db.Float, nullable=False, default=0.0)
    penalti = db.Column(db.Float, nullable=False, default=0.0)
    total_nilai = db.Column(db.Float, nullable=False, default=0.0)

    # --- TAMBAHKAN KEMBALI BARIS INI ---
    sesi_pertandingan = db.Column(db.String(100), default="current")

    event = db.relationship('Event', backref=db.backref('skor', lazy=True, cascade="all, delete"))
    peserta = db.relationship('Peserta', backref=db.backref('skor', lazy=True, cascade="all, delete"))
    alat = db.relationship('Alat')

# --- Helper Function ---
def get_active_event():
    return Event.query.filter_by(is_active=True).first()


# --- Rute Publik dan Input Skor ---

@app.route('/', methods=['GET', 'POST'])
def input_skor():
    active_event = get_active_event()
    if not active_event:
        flash("Tidak ada event yang aktif. Silakan aktifkan satu event di menu Admin.", "warning")
        return render_template('no_event.html')

    if request.method == 'POST':
        peserta_id = request.form.get('peserta'); alat_id = request.form.get('alat')
        if not all([peserta_id, alat_id]):
            flash("Peserta dan Alat harus dipilih.", "danger"); return redirect(url_for('input_skor'))
        try:
            nilai_d = float(request.form.get('nilai_d', 0)); nilai_e = float(request.form.get('nilai_e', 0))
            nilai_a = float(request.form.get('nilai_a', 0)); penalti = float(request.form.get('penalti', 0))
        except (ValueError, TypeError):
             flash("Nilai harus berupa angka.", "danger"); return redirect(url_for('input_skor'))
        total = (nilai_d + nilai_e + nilai_a) - penalti
        skor_baru = Skor(event_id=active_event.id, peserta_id=peserta_id, alat_id=alat_id, nilai_d=nilai_d, nilai_e=nilai_e, nilai_a=nilai_a, penalti=penalti, total_nilai=total)
        db.session.add(skor_baru); db.session.commit()
        return redirect(url_for('input_skor'))

    kategori_ids = db.session.query(Peserta.kategori_id).filter(Peserta.event_id == active_event.id).distinct().all()
    kategori_list = Kategori.query.filter(Kategori.id.in_([k[0] for k in kategori_ids])).all()
    master_data = { 'kategori': kategori_list, 'alat': Alat.query.order_by(Alat.nama).all() }
    # ranking_sementara = Skor.query.filter_by(event_id=active_event.id).order_by(Skor.total_nilai.desc()).all()
    ranking_sementara = Skor.query.filter_by(event_id=active_event.id, sesi_pertandingan='current').order_by(Skor.total_nilai.desc()).all()
    return render_template('input_skor.html', data=master_data, ranking=ranking_sementara, active_event=active_event)

# Tambahkan atau ganti dengan fungsi ini di app.py

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

    # Saat GET request, tampilkan form edit
    return render_template('edit_skor.html', skor=skor_to_edit)

@app.route('/live')
def live_view():
    active_event = get_active_event()
    return render_template('live_view.html', active_event=active_event)

@app.route('/history')
def riwayat():
    events = Event.query.order_by(Event.tanggal.desc()).all()
    riwayat_skor = {event: Skor.query.filter_by(event_id=event.id).order_by(Skor.total_nilai.desc()).all() for event in events if Skor.query.filter_by(event_id=event.id).first()}
    return render_template('riwayat.html', riwayat=riwayat_skor)

# Tambahkan dua fungsi ini di app.py

@app.route('/peringkat')
def peringkat():
    active_event = get_active_event()
    if not active_event:
        # Jika tidak ada event aktif, arahkan ke halaman utama yang akan menampilkan pesan
        return redirect(url_for('input_skor'))

    # Ambil semua skor untuk event yang aktif
    all_scores = Skor.query.filter_by(event_id=active_event.id).join(Peserta).join(Alat).all()

    # Logika untuk mengelompokkan skor
    peringkat_data = {}
    for skor in all_scores:
        # Buat kunci unik berdasarkan kombinasi Kategori, Grup, dan Alat
        key = f"{skor.peserta.kategori.nama} - {skor.peserta.grup.nama} - {skor.alat.nama}"
        
        if key not in peringkat_data:
            peringkat_data[key] = []
        
        peringkat_data[key].append(skor)

    # Urutkan skor di dalam setiap grup dari yang tertinggi ke terendah
    for key in peringkat_data:
        peringkat_data[key] = sorted(peringkat_data[key], key=lambda x: x.total_nilai, reverse=True)

    return render_template('peringkat.html', peringkat_data=peringkat_data, event=active_event)

@app.route('/peserta/<int:peserta_id>')
def profil_peserta(peserta_id):
    peserta = Peserta.query.get_or_404(peserta_id)
    # Ambil semua skor milik peserta ini dari semua event, diurutkan dari event terbaru
    skor_peserta = Skor.query.filter_by(peserta_id=peserta.id)\
        .join(Event).order_by(Event.tanggal.desc()).all()
    
    return render_template('profil_peserta.html', peserta=peserta, skor_list=skor_peserta)

# --- API Endpoints ---
@app.route('/api/scores')
def api_scores():
    active_event = get_active_event()
    if not active_event: return jsonify([])
    # skor_terkini = Skor.query.filter_by(event_id=active_event.id).order_by(Skor.total_nilai.desc()).all()
    skor_terkini = Skor.query.filter_by(event_id=active_event.id, sesi_pertandingan='current').order_by(Skor.total_nilai.desc()).all()
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
    active_event = get_active_event()
    if not active_event: return jsonify([])
    peserta_in_kategori = Peserta.query.filter_by(event_id=active_event.id, kategori_id=kategori_id).all()
    grup_ids = {p.grup_id for p in peserta_in_kategori}
    if not grup_ids: return jsonify([])
    grups = Grup.query.filter(Grup.id.in_(grup_ids)).order_by(Grup.nama).all()
    return jsonify([{'id': g.id, 'nama': g.nama} for g in grups])

@app.route('/api/peserta_by_grup/<int:kategori_id>/<int:grup_id>')
def api_peserta_by_grup(kategori_id, grup_id):
    active_event = get_active_event()
    if not active_event: return jsonify([])
    pesertas = Peserta.query.filter_by(event_id=active_event.id, kategori_id=kategori_id, grup_id=grup_id).order_by(Peserta.nama).all()
    return jsonify([{'id': p.id, 'nama': p.nama, 'daerah': p.daerah.nama} for p in pesertas])


# --- Area Admin ---
@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# --- TAMBAHAN: Rute untuk Manajemen Event ---
@app.route('/admin/manage/event', methods=['GET', 'POST'])
def admin_manage_event():
    if request.method == 'POST':
        nama_event = request.form.get('nama'); tanggal_str = request.form.get('tanggal')
        if nama_event and tanggal_str:
            try:
                db.session.add(Event(nama=nama_event, tanggal=parse_date(tanggal_str).date()))
                db.session.commit(); flash(f"Event '{nama_event}' berhasil ditambahkan.", "success")
            except ValueError: flash("Format tanggal tidak valid.", "danger")
        else: flash("Nama dan Tanggal Event tidak boleh kosong.", "danger")
        return redirect(url_for('admin_manage_event'))
    return render_template('admin_manage_event.html', events=Event.query.order_by(Event.tanggal.desc()).all())

@app.route('/admin/event/activate/<int:event_id>', methods=['POST'])
def admin_activate_event(event_id):
    Event.query.update({Event.is_active: False})
    event_to_activate = Event.query.get_or_404(event_id)
    event_to_activate.is_active = True; db.session.commit()
    flash(f"Event '{event_to_activate.nama}' sekarang aktif.", "success")
    return redirect(url_for('admin_manage_event'))

@app.route('/admin/event/delete/<int:event_id>', methods=['POST'])
def admin_delete_event(event_id):
    event = Event.query.get_or_404(event_id); db.session.delete(event); db.session.commit()
    flash(f"Event '{event.nama}' dan semua data terkait berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_event'))


# --- Rute Admin Generik (Tidak Berubah) ---
def get_model_map():
    return {'daerah': {'model': Daerah, 'title': 'Daerah'},'kategori': {'model': Kategori, 'title': 'Kategori'},'grup': {'model': Grup, 'title': 'Grup'},'alat': {'model': Alat, 'title': 'Alat'}}
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
                db.session.add(Model(nama=nama_baru)); db.session.commit()
                flash(f"{config['title']} '{nama_baru}' berhasil ditambahkan.", "success")
            else: flash(f"{config['title']} '{nama_baru}' sudah ada.", "warning")
        else: flash("Nama tidak boleh kosong.", "danger")
        return redirect(url_for('admin_manage_generic', master_type=master_type))
    items = Model.query.order_by(Model.nama).all()
    return render_template('admin_manage_generic.html', items=items, config=config, master_type=master_type)
@app.route('/admin/delete/<master_type>/<int:item_id>', methods=['POST'])
def admin_delete_generic(master_type, item_id):
    model_map = get_model_map()
    if master_type not in model_map: return "Tipe data tidak valid", 404
    config = model_map[master_type]; Model = config['model']
    item = Model.query.get_or_404(item_id); nama_item = item.nama
    db.session.delete(item); db.session.commit()
    flash(f"{config['title']} '{nama_item}' berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_generic', master_type=master_type))

# --- MODIFIKASI: Rute Admin Peserta dengan Event ---
@app.route('/admin/manage/peserta', methods=['GET', 'POST'])
def admin_manage_peserta():
    if request.method == 'POST':
        nama = request.form.get('nama'); daerah_id = request.form.get('daerah_id')
        kategori_id = request.form.get('kategori_id'); grup_id = request.form.get('grup_id')
        event_id = request.form.get('event_id') # Tambahan
        if all([nama, daerah_id, kategori_id, grup_id, event_id]):
            db.session.add(Peserta(nama=nama, daerah_id=daerah_id, kategori_id=kategori_id, grup_id=grup_id, event_id=event_id))
            db.session.commit(); flash(f"Peserta '{nama}' berhasil ditambahkan.", "success")
        else: flash("Semua field wajib diisi.", "danger")
        return redirect(url_for('admin_manage_peserta'))
    return render_template('admin_manage_peserta.html', 
        peserta_list=Peserta.query.order_by(Peserta.nama).all(), 
        daerah_list=Daerah.query.order_by(Daerah.nama).all(),
        kategori_list=Kategori.query.order_by(Kategori.nama).all(), 
        grup_list=Grup.query.order_by(Grup.nama).all(),
        event_list=Event.query.order_by(Event.nama).all()) # Kirim list event
@app.route('/admin/delete/peserta/<int:peserta_id>', methods=['POST'])
def admin_delete_peserta(peserta_id):
    peserta = Peserta.query.get_or_404(peserta_id); db.session.delete(peserta); db.session.commit()
    flash(f"Peserta '{peserta.nama}' berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_peserta'))

@app.route('/reset', methods=['POST'])
def reset_skor():
    flash('Fitur ini telah digantikan. Silakan aktifkan event baru dari Menu Admin.', 'info')
    return redirect(url_for('admin_manage_event'))

# Tambahkan fungsi ini di app.py

from datetime import datetime

@app.route('/archive_scores', methods=['POST'])
def archive_scores():
    active_event = get_active_event()
    if not active_event:
        flash("Tidak ada event aktif.", "danger")
        return redirect(url_for('input_skor'))

    # Buat penanda unik untuk sesi yang diarsipkan
    archive_session_name = f"arsip-{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Cari semua skor yang 'current' di event aktif dan update statusnya
    Skor.query.filter_by(event_id=active_event.id, sesi_pertandingan='current').update({
        "sesi_pertandingan": archive_session_name
    })

    db.session.commit()
    flash("Skor 'live' telah diarsipkan. Papan skor siap untuk kategori berikutnya.", "success")
    return redirect(url_for('input_skor'))
    
# --- Main execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')