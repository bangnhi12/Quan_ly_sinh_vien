from flask import Flask, redirect, url_for
from flask_login import current_user
from extensions import db, login_manager
from flask import redirect, url_for
from flask_login import current_user
from routes.auth import auth_bp
from routes.candidate import candidate_bp
from routes.admin import admin_bp
from routes.student import student_bp
from models import VaiTro
app = Flask(__name__)
app.config['SECRET_KEY'] = 'quanlysinhvien'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/quan_ly_sinh_vien_1'

db.init_app(app)
login_manager.init_app(app)
from models import TaiKhoan 
@login_manager.user_loader
def load_user(user_id):
    
    return TaiKhoan.query.get(int(user_id))
login_manager.login_view = 'auth.login'

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(candidate_bp, url_prefix='/candidate')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(student_bp, url_prefix='/student')
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.vai_tro == VaiTro.ADMIN:
            return redirect(url_for('admin.dashboard'))
        if current_user.vai_tro == VaiTro.SINHVIEN:
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('candidate.dashboard'))
    return redirect(url_for('auth.login'))

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
