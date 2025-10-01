import os
import io
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from dateutil.parser import parse as parse_date
from werkzeug.utils import secure_filename
from weasyprint import HTML
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- Konfigurasi Dasar ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'gymnastics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kunci-rahasia-final-yang-sangat-aman-untuk-proyek-ini'
db = SQLAlchemy(app)

# --- Konfigurasi Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Akan kita buat nanti
login_manager.login_message = "Anda harus login untuk mengakses halaman ini."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Model Basis Data ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)

class Daerah(db.Model): id = db.Column(db.Integer, primary_key=True); nama = db.Column(db.String(100), unique=True, nullable=False)
class Kategori(db.Model): id = db.Column(db.Integer, primary_key=True); nama = db.Column(db.String(100), unique=True, nullable=False)
class Grup(db.Model): id = db.Column(db.Integer, primary_key=True); nama = db.Column(db.String(100), unique=True, nullable=False)
class Alat(db.Model): id = db.Column(db.Integer, primary_key=True); nama = db.Column(db.String(100), unique=True, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Peserta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
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
    sesi_pertandingan = db.Column(db.String(100), default="current")
    event = db.relationship('Event', backref=db.backref('skor', lazy=True, cascade="all, delete"))
    peserta = db.relationship('Peserta', backref=db.backref('skor', lazy=True, cascade="all, delete"))
    alat = db.relationship('Alat')

# --- Rute Utama & Global ---
@app.route('/')
def select_event():
    events = Event.query.order_by(Event.tanggal.desc()).all()
    return render_template('event_selection.html', events=events)

@app.route('/history')
def riwayat():
    events = Event.query.order_by(Event.tanggal.desc()).all()
    riwayat_data = {}
    for event in events:
        scores_in_event = Skor.query.filter_by(event_id=event.id).all()
        if not scores_in_event: continue
        participant_summary = {}
        for skor in scores_in_event:
            pid = skor.peserta_id
            if pid not in participant_summary:
                participant_summary[pid] = {"peserta": skor.peserta, "skor_alat": {}, "total_skor": 0.0}
            participant_summary[pid]["skor_alat"][skor.alat.nama] = skor.total_nilai
            participant_summary[pid]["total_skor"] += skor.total_nilai
        final_grouping = {}
        for summary in participant_summary.values():
            key = f"{summary['peserta'].kategori.nama} - {summary['peserta'].grup.nama}"
            if key not in final_grouping: final_grouping[key] = []
            final_grouping[key].append(summary)
        for key in final_grouping:
            final_grouping[key] = sorted(final_grouping[key], key=lambda x: x['total_skor'], reverse=True)
        riwayat_data[event] = final_grouping
    return render_template('riwayat.html', riwayat=riwayat_data)

@app.route('/peserta/<int:peserta_id>')
def profil_peserta(peserta_id):
    peserta = Peserta.query.get_or_404(peserta_id)
    skor_list_historis = Skor.query.filter_by(peserta_id=peserta.id).join(Event).order_by(Event.tanggal.desc()).all()
    skor_event_terdaftar = [s for s in skor_list_historis if s.event_id == peserta.event_id]
    total_all_around = sum(s.total_nilai for s in skor_event_terdaftar)
    return render_template('profil_peserta.html', peserta=peserta, skor_list=skor_list_historis, total_all_around=total_all_around)

# --- Rute Spesifik Event ---
@app.route('/event/<int:event_id>/input', methods=['GET', 'POST'])
def input_skor(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        peserta_id = request.form.get('peserta'); alat_id = request.form.get('alat')
        if not all([peserta_id, alat_id]):
            flash("Peserta dan Alat harus dipilih.", "danger"); return redirect(url_for('input_skor', event_id=event.id))
        try:
            nilai_d = float(request.form.get('nilai_d', 0)); nilai_e = float(request.form.get('nilai_e', 0))
            nilai_a = float(request.form.get('nilai_a', 0)); penalti = float(request.form.get('penalti', 0))
        except (ValueError, TypeError):
             flash("Nilai harus berupa angka.", "danger"); return redirect(url_for('input_skor', event_id=event.id))
        total = (nilai_d + nilai_e + nilai_a) - penalti
        skor_baru = Skor(event_id=event.id, peserta_id=peserta_id, alat_id=alat_id, nilai_d=nilai_d, nilai_e=nilai_e, nilai_a=nilai_a, penalti=penalti, total_nilai=total)
        db.session.add(skor_baru); db.session.commit()
        return redirect(url_for('input_skor', event_id=event.id))
    master_data = {'kategori': Kategori.query.order_by(Kategori.nama).all(),'grup': Grup.query.order_by(Grup.nama).all(),'alat': Alat.query.order_by(Alat.nama).all()}
    ranking_sementara = Skor.query.filter_by(event_id=event.id, sesi_pertandingan='current').order_by(Skor.total_nilai.desc()).all()
    return render_template('input_skor.html', data=master_data, ranking=ranking_sementara, event=event)

@app.route('/event/<int:event_id>/live')
def live_view(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('live_view.html', event=event)

@app.route('/event/<int:event_id>/peringkat')
def peringkat(event_id):
    event = Event.query.get_or_404(event_id)
    all_scores = Skor.query.filter_by(event_id=event.id).join(Peserta).join(Alat).all()
    peringkat_data = {}
    for skor in all_scores:
        key = f"{skor.peserta.kategori.nama} - {skor.peserta.grup.nama} - {skor.alat.nama}"
        if key not in peringkat_data: peringkat_data[key] = []
        peringkat_data[key].append(skor)
    for key in peringkat_data:
        peringkat_data[key] = sorted(peringkat_data[key], key=lambda x: x.total_nilai, reverse=True)
    return render_template('peringkat.html', peringkat_data=peringkat_data, event=event)

@app.route('/edit_skor/<int:skor_id>', methods=['GET', 'POST'])
def edit_skor(skor_id):
    skor_to_edit = Skor.query.get_or_404(skor_id)
    event_id = skor_to_edit.event_id # Dapatkan event_id dari skor yang diedit
    if request.method == 'POST':
        try:
            skor_to_edit.nilai_d = float(request.form.get('nilai_d', 0)); skor_to_edit.nilai_e = float(request.form.get('nilai_e', 0))
            skor_to_edit.nilai_a = float(request.form.get('nilai_a', 0)); skor_to_edit.penalti = float(request.form.get('penalti', 0))
            skor_to_edit.total_nilai = (skor_to_edit.nilai_d + skor_to_edit.nilai_e + skor_to_edit.nilai_a) - skor_to_edit.penalti
            db.session.commit(); flash('Skor berhasil diperbarui!', 'success')
            return redirect(url_for('input_skor', event_id=event_id))
        except (ValueError, TypeError):
            flash('Input tidak valid.', 'danger'); return redirect(url_for('edit_skor', skor_id=skor_id))
    return render_template('edit_skor.html', skor=skor_to_edit)

@app.route('/archive_scores/<int:event_id>', methods=['POST'])
def archive_scores(event_id):
    archive_session_name = f"arsip-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    Skor.query.filter_by(event_id=event_id, sesi_pertandingan='current').update({"sesi_pertandingan": archive_session_name})
    db.session.commit(); flash("Skor 'live' telah diarsipkan.", "success")
    return redirect(url_for('input_skor', event_id=event_id))

# --- API Endpoints ---
@app.route('/api/event/<int:event_id>/scores')
def api_scores(event_id):
    live_scores = Skor.query.filter_by(event_id=event_id, sesi_pertandingan='current').all()
    participant_summary = {}
    for skor in live_scores:
        pid = skor.peserta_id
        if pid not in participant_summary:
            participant_summary[pid] = {"peserta": {"id": skor.peserta.id, "nama": skor.peserta.nama, "daerah": skor.peserta.daerah.nama},"skor_alat": {},"total_skor": 0.0}
        participant_summary[pid]["skor_alat"][skor.alat.nama] = skor.total_nilai
        participant_summary[pid]["total_skor"] += skor.total_nilai
    final_grouping = {}
    for summary in participant_summary.values():
        peserta_obj = Peserta.query.get(summary['peserta']['id'])
        key = f"{peserta_obj.kategori.nama} - {peserta_obj.grup.nama}"
        if key not in final_grouping: final_grouping[key] = []
        final_grouping[key].append(summary)
    for key in final_grouping:
        final_grouping[key] = sorted(final_grouping[key], key=lambda x: x['total_skor'], reverse=True)
    return jsonify(final_grouping)

@app.route('/api/event/<int:event_id>/peserta_by_filters')
def api_peserta_by_filters(event_id):
    kategori_id = request.args.get('kategori_id'); grup_id = request.args.get('grup_id'); alat_id = request.args.get('alat_id')
    if not all([kategori_id, grup_id, alat_id]): return jsonify([])
    pesertas_in_grup = Peserta.query.filter_by(event_id=event_id, kategori_id=kategori_id, grup_id=grup_id).all()
    scored_peserta_ids = {skor.peserta_id for skor in Skor.query.filter_by(event_id=event_id, alat_id=alat_id, sesi_pertandingan='current').all()}
    peserta_array = [{'id': p.id, 'nama': p.nama, 'daerah': p.daerah.nama,'scored': p.id in scored_peserta_ids} for p in pesertas_in_grup]
    return jsonify(sorted(peserta_array, key=lambda x: x['nama']))

# --- Area Admin ---
@app.route('/admin')
def admin_dashboard(): return render_template('admin_dashboard.html')

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
    # Nonaktifkan semua event lain terlebih dahulu
    Event.query.update({Event.is_active: False})
    # Aktifkan event yang dipilih
    event_to_activate = Event.query.get_or_404(event_id)
    event_to_activate.is_active = True
    db.session.commit()
    flash(f"Event '{event_to_activate.nama}' sekarang aktif.", "success")
    return redirect(url_for('admin_manage_event'))

@app.route('/admin/event/delete/<int:event_id>', methods=['POST'])
def admin_delete_event(event_id):
    event = Event.query.get_or_404(event_id); db.session.delete(event); db.session.commit()
    flash(f"Event '{event.nama}' dan semua data terkait berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_event'))

def get_model_map():
    return {'daerah': {'model': Daerah, 'title': 'Daerah'},'kategori': {'model': Kategori, 'title': 'Kategori'},'grup': {'model': Grup, 'title': 'Grup'},'alat': {'model': Alat, 'title': 'Alat'}}
@app.route('/admin/manage/<master_type>', methods=['GET', 'POST'])
def admin_manage_generic(master_type):
    model_map = get_model_map();
    if master_type not in model_map: return "Tipe data tidak valid", 404
    config = model_map[master_type]; Model = config['model']
    if request.method == 'POST':
        nama_baru = request.form.get('nama')
        if nama_baru:
            if not Model.query.filter_by(nama=nama_baru).first():
                db.session.add(Model(nama=nama_baru)); db.session.commit(); flash(f"{config['title']} '{nama_baru}' berhasil ditambahkan.", "success")
            else: flash(f"{config['title']} '{nama_baru}' sudah ada.", "warning")
        else: flash("Nama tidak boleh kosong.", "danger")
        return redirect(url_for('admin_manage_generic', master_type=master_type))
    return render_template('admin_manage_generic.html', items=Model.query.order_by(Model.nama).all(), config=config, master_type=master_type)
@app.route('/admin/delete/<master_type>/<int:item_id>', methods=['POST'])
def admin_delete_generic(master_type, item_id):
    model_map = get_model_map();
    if master_type not in model_map: return "Tipe data tidak valid", 404
    config = model_map[master_type]; Model = config['model']
    item = Model.query.get_or_404(item_id); db.session.delete(item); db.session.commit()
    flash(f"{config['title']} '{item.nama}' berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_generic', master_type=master_type))

@app.route('/admin/manage/peserta', methods=['GET', 'POST'])
def admin_manage_peserta():
    if request.method == 'POST':
        nama = request.form.get('nama'); daerah_id = request.form.get('daerah_id'); kategori_id = request.form.get('kategori_id')
        grup_id = request.form.get('grup_id'); event_id = request.form.get('event_id')
        if all([nama, daerah_id, kategori_id, grup_id, event_id]):
            db.session.add(Peserta(nama=nama, daerah_id=daerah_id, kategori_id=kategori_id, grup_id=grup_id, event_id=event_id))
            db.session.commit(); flash(f"Peserta '{nama}' berhasil ditambahkan.", "success")
        else: flash("Semua field wajib diisi.", "danger")
        return redirect(url_for('admin_manage_peserta'))
    sort_by = request.args.get('sort_by', 'nama'); page = request.args.get('page', 1, type=int)
    query = Peserta.query
    if sort_by == 'daerah': query = query.join(Daerah).order_by(Daerah.nama)
    elif sort_by == 'kategori': query = query.join(Kategori).order_by(Kategori.nama)
    elif sort_by == 'grup': query = query.join(Grup).order_by(Grup.nama)
    elif sort_by == 'event': query = query.join(Event).order_by(Event.nama)
    else: query = query.order_by(Peserta.nama)
    pagination = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('admin_manage_peserta.html', peserta_list=pagination.items, pagination=pagination,
        daerah_list=Daerah.query.order_by(Daerah.nama).all(), kategori_list=Kategori.query.order_by(Kategori.nama).all(),
        grup_list=Grup.query.order_by(Grup.nama).all(), event_list=Event.query.order_by(Event.nama).all(), current_sort=sort_by)
@app.route('/admin/edit/peserta/<int:peserta_id>', methods=['GET', 'POST'])
def admin_edit_peserta(peserta_id):
    peserta_to_edit = Peserta.query.get_or_404(peserta_id)
    if request.method == 'POST':
        peserta_to_edit.nama = request.form.get('nama'); peserta_to_edit.daerah_id = request.form.get('daerah_id')
        peserta_to_edit.kategori_id = request.form.get('kategori_id'); peserta_to_edit.grup_id = request.form.get('grup_id')
        peserta_to_edit.event_id = request.form.get('event_id')
        db.session.commit(); flash(f"Data peserta '{peserta_to_edit.nama}' berhasil diperbarui.", "success")
        return redirect(url_for('admin_manage_peserta'))
    return render_template('admin_edit_peserta.html', peserta=peserta_to_edit,
        daerah_list=Daerah.query.order_by(Daerah.nama).all(), kategori_list=Kategori.query.order_by(Kategori.nama).all(),
        grup_list=Grup.query.order_by(Grup.nama).all(), event_list=Event.query.order_by(Event.nama).all())
@app.route('/admin/delete/peserta/<int:peserta_id>', methods=['POST'])
def admin_delete_peserta(peserta_id):
    peserta = Peserta.query.get_or_404(peserta_id); db.session.delete(peserta); db.session.commit()
    flash(f"Peserta '{peserta.nama}' berhasil dihapus.", "success")
    return redirect(url_for('admin_manage_peserta'))

@app.route('/admin/import_peserta', methods=['POST'])
def admin_import_peserta():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.xlsx'):
        flash("File tidak valid. Harap unggah file .xlsx.", "danger"); return redirect(url_for('admin_manage_peserta'))
    try:
        df = pd.read_excel(file)
        daerah_map = {d.nama: d.id for d in Daerah.query.all()}; kategori_map = {k.nama: k.id for k in Kategori.query.all()}
        grup_map = {g.nama: g.id for g in Grup.query.all()}; event_map = {e.nama: e.id for e in Event.query.all()}
        errors, success_count = [], 0
        for index, row in df.iterrows():
            try:
                db.session.add(Peserta(nama=row['Nama Peserta'], daerah_id=daerah_map[row['Nama Daerah']],
                    kategori_id=kategori_map[row['Nama Kategori']], grup_id=grup_map[row['Nama Grup']], event_id=event_map[row['Nama Event']]))
                success_count += 1
            except KeyError as e: errors.append(f"Baris {index+2}: Data '{e.args[0]}' tidak ditemukan.")
            except Exception as e: errors.append(f"Baris {index+2}: Error - {e}")
        if errors:
            flash("Sebagian data gagal diimpor:", "warning")
            for error in errors: flash(error, "danger")
        if success_count > 0:
            db.session.commit(); flash(f"{success_count} peserta berhasil diimpor.", "success")
    except Exception as e: flash(f"Error saat memproses file: {e}", "danger")
    return redirect(url_for('admin_manage_peserta'))

@app.route('/export/event/<int:event_id>/<format>')
def export_event(event_id, format):
    event = Event.query.get_or_404(event_id)
    # Lakukan agregasi data seperti di fungsi riwayat()
    scores_in_event = Skor.query.filter_by(event_id=event.id).all()
    participant_summary = {}
    for skor in scores_in_event:
        pid = skor.peserta_id
        if pid not in participant_summary: participant_summary[pid] = {"peserta": skor.peserta, "skor_alat": {}, "total_skor": 0.0}
        participant_summary[pid]["skor_alat"][skor.alat.nama] = skor.total_nilai
        participant_summary[pid]["total_skor"] += skor.total_nilai
    final_grouping = {}
    for summary in participant_summary.values():
        key = f"{summary['peserta'].kategori.nama} - {summary['peserta'].grup.nama}"
        if key not in final_grouping: final_grouping[key] = []
        final_grouping[key].append(summary)
    for key in final_grouping:
        final_grouping[key] = sorted(final_grouping[key], key=lambda x: x['total_skor'], reverse=True)
    
    if format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for group_key, summaries in final_grouping.items():
                sheet_name = group_key[:31] # Nama sheet excel maks 31 karakter
                data_to_export = []
                for summary in summaries:
                    row_data = {
                        'Peringkat': len(data_to_export) + 1,
                        'Nama Peserta': summary['peserta'].nama,
                        'Daerah': summary['peserta'].daerah.nama,
                        'Total Skor': summary['total_skor']
                    }
                    for alat, nilai in summary['skor_alat'].items(): row_data[alat] = nilai
                    data_to_export.append(row_data)
                pd.DataFrame(data_to_export).to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return send_file(output, download_name=f'hasil_{event.nama}.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    elif format == 'pdf':
        rendered_html = render_template('laporan_pdf.html', riwayat={event: final_grouping})
        pdf = HTML(string=rendered_html).write_pdf()
        return send_file(io.BytesIO(pdf), download_name=f'hasil_{event.nama}.pdf', as_attachment=True, mimetype='application/pdf')
    
    return "Format tidak valid.", 400

# --- Main execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
