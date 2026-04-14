from flask import *
from flask_login import *
from extensions import db
from models import *

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        existing_user = TaiKhoan.query.filter_by(ten_dang_nhap=name).first()
        if existing_user:
            flash('Tên đăng nhập đã tồn tại')
            return redirect(url_for('auth.register'))
        new_tk = TaiKhoan(ten_dang_nhap=name, mat_khau=password, vai_tro=VaiTro.THISINH)

        db.session.add(new_tk)
        db.session.commit()

        flash('Đăng ký thành công!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = TaiKhoan.query.filter_by(ten_dang_nhap=username, mat_khau=password).first()
        if user:
            login_user(user)
            if user.vai_tro == VaiTro.ADMIN:
                return redirect(url_for('admin.dashboard'))
            elif user.vai_tro == VaiTro.SINHVIEN:
                return redirect(url_for('student.dashboard'))
            else:
                return redirect(url_for('candidate.dashboard'))
            
        flash('Tài khoản hoặc mật khẩu không chính xác!')
    return render_template('auth/login.html')

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_pw = request.form.get('old_password')
        new_pw = request.form.get('new_password')

        if current_user.mat_khau == old_pw:
            current_user.mat_khau = new_pw
            db.session.commit()
            flash('Đổi mật khẩu thành công')
            return redirect(url_for('candidate.dashboard'))
        else:
            flash('Mật khẩu cũ không đúng! Nhập lại')
    return render_template('auth/change_password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đăng xuất thành công')
    return redirect(url_for('auth.login'))

