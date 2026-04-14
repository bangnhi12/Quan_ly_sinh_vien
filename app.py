from flask import Flask
from extensions import db, login_manager
from routes.auth import auth_bp
from routes.candidate import candidate_bp
from routes.admin import admin_bp
from routes.student import student_bp
app = Flask(__name__)
app.config['SECRET_KEY'] = 'quanlysinhvien'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/quan_ly_sinh_vien'

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
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
