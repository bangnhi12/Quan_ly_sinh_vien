from flask import *
from flask_login import *
from extensions import db
from models import *
from datetime import date, datetime
from sqlalchemy.orm import joinedload

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
        flash('Không tìm thấy hồ sơ sinh viên!', 'danger')
        return redirect(url_for('student.dashboard'))
    lop_info = Lop.query.filter_by(MaLop=student.MaLop).first()
    nganh_info = None
    khoa_info = None
    if lop_info:
        nganh_info = Nganh.query.filter_by(MaNganh=lop_info.MaNganh).first()
        if nganh_info:
            khoa_info = Khoa.query.filter_by(MaKhoa=nganh_info.MaKhoa).first()
    return render_template('student/profile.html', 
                           student=student, 
                           lop=lop_info, 
                           nganh=nganh_info, 
                           khoa=khoa_info)

def _convert_10_to_4_scale(score_10):
    if score_10 >= 8.5:
        return 4.0
    if score_10 >= 8.0:
        return 3.5
    if score_10 >= 7.0:
        return 3.0
    if score_10 >= 6.5:
        return 2.5
    if score_10 >= 5.5:
        return 2.0
    if score_10 >= 5.0:
        return 1.5
    if score_10 >= 4.0:
        return 1.0
    return 0.0

def _xep_loai_from_cpa(cpa):
    if cpa >= 3.6:
        return "Xuất sắc"
    if cpa >= 3.2:
        return "Giỏi"
    if cpa >= 2.5:
        return "Khá"
    if cpa >= 2.0:
        return "Trung bình"
    return "Yếu"

@student_bp.route('/grades')
@login_required
def view_grades():
    student = SinhVien.query.filter_by(ID_TaiKhoan=current_user.id).first()

    if not student:
        flash('Chưa cập nhật hồ sơ của bạn')
        return redirect(url_for('student.dashboard'))

    lop_info = Lop.query.get(student.MaLop) if student.MaLop else None
    nganh_info = Nganh.query.get(lop_info.MaNganh) if lop_info else None

    curriculum_subjects = []
    if nganh_info:
        curriculum_subjects = db.session.query(MonHoc)\
            .join(NganhMonHoc, NganhMonHoc.MaMH == MonHoc.MaMH)\
            .filter(NganhMonHoc.MaNganh == nganh_info.MaNganh)\
            .order_by(MonHoc.MaMH.asc())\
            .all()

    grades = KQ_HocTap.query.filter_by(MaSV=student.MaSV).all()
    grade_map = {g.MaMH: float(g.Diem) for g in grades}

    subject_results = []
    total_credits = sum(int(mon.SoTinChi) for mon in curriculum_subjects)
    graded_subjects = 0
    graded_credits = 0
    weighted_total = 0.0

    for mon in curriculum_subjects:
        score = grade_map.get(mon.MaMH)
        if score is not None:
            graded_subjects += 1
            graded_credits += int(mon.SoTinChi)
            weighted_total += _convert_10_to_4_scale(score) * int(mon.SoTinChi)

        subject_results.append({
            'MaMH': mon.MaMH,
            'TenMH': mon.TenMH,
            'SoTinChi': int(mon.SoTinChi),
            'Diem': score
        })

    cpa = round(weighted_total / graded_credits, 2) if graded_credits > 0 else None
    xep_loai = _xep_loai_from_cpa(cpa) if cpa is not None else '---'

    return render_template('student/grades.html',
                           student=student,
                           lop=lop_info,
                           nganh=nganh_info,
                           subject_results=subject_results,
                           cpa=cpa,
                           xep_loai=xep_loai,
                           total_subjects=len(curriculum_subjects),
                           graded_subjects=graded_subjects,
                           total_credits=total_credits)
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

    return render_template('student/notifications.html', notifications=notifications_list)

@student_bp.route('/notifications/<int:receipt_id>')
@login_required
def notification_detail(receipt_id):
    receipt = TB_NguoiNhan.query.filter_by(MaTBNN=receipt_id, ID_TaiKhoan=current_user.id).first_or_404()
    notification = ThongBao.query.get_or_404(receipt.MaTB)

    sender_name = "Hệ thống"
    if notification.MaAdmin:
        sender = QuanTri.query.get(notification.MaAdmin)
        if sender and sender.HoTen:
            sender_name = sender.HoTen

    if not receipt.TrangThaiDoc:
        receipt.TrangThaiDoc = True
        receipt.ThoiGianDoc = datetime.now()
        db.session.commit()

    return render_template(
        'student/notification_detail.html',
        receipt=receipt,
        notification=notification,
        sender_name=sender_name
    )

@student_bp.route('/report_job', methods=['GET','POST'])
@login_required
def report_job():
    student = SinhVien.query.filter_by(ID_TaiKhoan=current_user.id).first()

    if not student:
        flash('Hồ sơ sinh viên của bạn chưa tồn tại trên hệ thống. Vui lòng liên hệ Admin!', 'danger')
        return redirect(url_for('student.dashboard'))

    job_info = ViecLamSinhVien.query.filter_by(MaSV=student.MaSV).first()

    if request.method == 'POST':
        ten_cty = request.form.get('ten_cty')
        chuc_vu = request.form.get('chuc_vu')
        dia_chi = request.form.get('dia_chi')
        ngay_bd_str = request.form.get('ngay_bat_dau')

        ngay_bat_dau = None
        if ngay_bd_str:
            try:
                ngay_bat_dau = datetime.strptime(ngay_bd_str, '%Y-%m-%d').date()
            except ValueError:
                pass # Hoặc flash lỗi định dạng ngày tháng

        if job_info:
            # Cập nhật nếu đã có
            job_info.TenCongTy = ten_cty
            job_info.ChucVu = chuc_vu
            job_info.DiaChiCongTy = dia_chi
            job_info.ThoiGianBatDau = ngay_bat_dau
        else:
            # Thêm mới nếu chưa có
            new_job = ViecLamSinhVien(
                MaSV = student.MaSV,
                TenCongTy = ten_cty,
                ChucVu = chuc_vu,
                DiaChiCongTy = dia_chi,
                ThoiGianBatDau = ngay_bat_dau
            )
            db.session.add(new_job)
        
        db.session.commit()
        flash('Cập nhật thông tin việc làm thành công!', 'success')
        return redirect(url_for('student.report_job'))

    return render_template('student/report_job.html', student=student, job=job_info)
