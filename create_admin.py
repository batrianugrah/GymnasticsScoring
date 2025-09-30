from app import app, db, User
import getpass

def create_first_admin():
    """
    Skrip untuk membuat pengguna admin pertama kali.
    """
    with app.app_context():
        # Periksa apakah sudah ada admin
        if User.query.filter_by(role='Admin').first():
            print("Pengguna Admin sudah ada.")
            return

        print("Membuat akun Admin pertama...")
        
        # Minta username dan password dari terminal
        username = input("Masukkan username untuk Admin: ")
        password = getpass.getpass("Masukkan password untuk Admin: ")
        confirm_password = getpass.getpass("Konfirmasi password: ")
        
        if password != confirm_password:
            print("Password tidak cocok. Proses dibatalkan.")
            return
            
        if User.query.filter_by(username=username).first():
            print(f"Username '{username}' sudah digunakan.")
            return

        # Buat objek user baru
        admin_user = User(username=username, role='Admin')
        admin_user.set_password(password)
        
        # Simpan ke database
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Pengguna Admin '{username}' berhasil dibuat!")

if __name__ == '__main__':
    create_first_admin()