from flask import *
from flask_login import *
from extensions import db
from models import *
from datetime import date

student_bp = Blueprint('student', __name__)
@student_bp.route('/dashboard')
@login_required
def dashboard():
    student = SinhVien.query.filter_by(ID_TaiKhoan=current_user.id).first()
    print(student)
    return render_template('student/dashboard.html', student=student)

@student_bp.route('/profile')
@login_required
def view_profile():
    student = SinhVien.query.filter_by(ID_TaiKhoan=current_user.id).first()
    if not student:
        flash('Chưa cập nhật hồ sơ của bạn')
        return redirect(url_for('student.dashboard'))
    return render_template('student/profile.html', student=student)

@student_bp.route('/grades')
@login_required
def view_grades():
    student = SinhVien.query.filter_by(ID_TaiKhoan=current_user.id).first()

    if not student:
        flash('Chưa cập nhật hồ sơ của bạn')
        return redirect(url_for('student.dashboard'))
    
    graduation_info = TotNghiep.query.filter_by(MaSV=student.MaSV).first()
    return render_template('student/grades.html',
                           student=student,
                           gpa_info=graduation_info)
@student_bp.route('/notifications')
@login_required
def view_notifications():
    receipts = TB_NguoiNhan.query.filter_by(ID_TaiKhoan=current_user.id).all()
    
    notifications_list = []
    
    for r in receipts:
        content = ThongBao.query.get(r.MaTB)
        
        if content:
            notifications_list.append({
                'receipt': r,
                'content': content
            })
    notifications_list.sort(key=lambda x: x['content'].NgayGui, reverse=True)

    unread = TB_NguoiNhan.query.filter_by(ID_TaiKhoan=current_user.id, TrangThaiDoc=False).all()
    if unread:
        for u in unread:
            u.TrangThaiDoc = True
        db.session.commit()

    return render_template('student/notifications.html', notifications=notifications_list)

@student_bp.route('/report_job', methods=['GET','POST'])
@login_required
def report_job():
    student = SinhVien.query.filter_by(ID_TaiKhoan=current_user.id).first()
    job_info = ViecLamSinhVien.query.filter_by(MaSV=student.MaSV).first()

    if request.method == 'POST':
        ten_cty = request.form.get('ten_cty')
        chuc_vu = request.form.get('chuc_vu')
        dia_chi = request.form.get('dia_chi')
        ngay_bd_str = request.form.get('ngay_bat_dau')

        ngay_bat_dau = None
        if ngay_bd_str:
            ngay_bat_dau = datetime.strptime(ngay_bd_str, '%Y-%m-%d').date()
        if job_info:
            job_info.TenCongTy = ten_cty
            job_info.ChucVu = chuc_vu
            job_info.DiaChiCongTy = dia_chi
            job_info.ThoiGianBatDau = ngay_bat_dau
        else:
            new_job = ViecLamSinhVien(
                MaSV = student.MaSV,
                TenCongTy = ten_cty,
                ChucVu = chuc_vu,
                DiaChiCongTy = dia_chi,
                ThoiGianBatDau = ngay_bat_dau
            )
            db.session.add(new_job)
        db.session.commit()
        flash('Cập nhật thành công')
        return redirect(url_for('student.report_job'))
    return render_template('student/report_job.html', job=job_info)
