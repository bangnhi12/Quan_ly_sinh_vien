from flask import *
from flask_login import *
from extensions import db
from models import *
from datetime import date

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    count_thisinh = HSO_XETTUYEN.query.count()
    count_sinhvien = SinhVien.query.count()
    count_cho_duyet = PT_XetTuyen.query.filter_by(TrangThai=TrangThaiXT.CHO_DUYET).count()

    latest_applications = db.session.query(PT_XetTuyen, HSO_XETTUYEN.HoTen)\
        .join(HSO_XETTUYEN, PT_XetTuyen.MaHSO == HSO_XETTUYEN.MaHSO)\
        .order_by(PT_XetTuyen.MaPTXT.desc())\
        .limit(5).all()

    return render_template('admin/dashboard.html', 
                           count_thisinh=count_thisinh,
                           count_sinhvien=count_sinhvien,
                           count_cho_duyet=count_cho_duyet,
                           latest_applications=latest_applications)

@admin_bp.route('/manage_khoa', methods=['GET', 'POST'])
def manage_khoa():
    if request.method == 'POST':
        ma_khoa = request.form.get('ma_khoa').upper()
        ten_khoa = request.form.get('ten_khoa').capitalize()

        ex = Khoa.query.get(ma_khoa)
        if ex:
            flash('Mã Khoa đã tồn tại')
        else:
            new_khoa = Khoa(
                MaKhoa = ma_khoa,
                TenKhoa = ten_khoa
            )
            db.session.add(new_khoa)
            db.session.commit()
            flash('Thêm khoa mới thành công')
    ds_khoa = Khoa.query.all()
    return render_template('admin/manage_khoa.html', ds_khoa=ds_khoa)
    
@admin_bp.route('/manage_nganh', methods=['GET', 'POST'])
def manage_nganh():
    if request.method == 'POST':
        ma_nganh = request.form.get('ma_nganh').upper()
        ten_nganh = request.form.get('ten_nganh').capitalize()
        ma_khoa = request.form.get('ma_khoa')

        new_nganh = Nganh(
            MaNganh = ma_nganh,
            TenNganh = ten_nganh,
            MaKhoa = ma_khoa
        )
        db.session.add(new_nganh)
        db.session.commit()
        flash('Đã thêm ngành thành công')
    ds_nganh = Nganh.query.all()
    ds_khoa = Khoa.query.all()
    return render_template('admin/manage_nganh.html',ds_nganh=ds_nganh,ds_khoa=ds_khoa)

from sqlalchemy import inspect # Thêm cái này ở đầu file để kiểm tra tồn tại

@admin_bp.route('/delete/<string:type>/<string:id>')
@login_required
def delete_item(type, id):
    try:
        if type == 'khoa':
            has_nganh = Nganh.query.filter_by(MaKhoa=id).first()
            if has_nganh:
                flash(f'Không thể xóa Khoa {id} vì vẫn còn Ngành học bên trong. Hãy xóa các Ngành trước!', 'danger')
                return redirect(request.referrer)
            Khoa.query.filter_by(MaKhoa=id).delete()
        elif type == 'nganh':
            has_lop = Lop.query.filter_by(MaNganh=id).first()
            if has_lop:
                flash(f'Không thể xóa Ngành {id} vì đã có Lớp học đăng ký ngành này!', 'danger')
                return redirect(request.referrer)
            Nganh.query.filter_by(MaNganh=id).delete()
        db.session.commit()
        flash('Đã xóa dữ liệu thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi xóa: {e}")
        flash('Lỗi hệ thống: Không thể xóa dữ liệu này.', 'danger')

    return redirect(request.referrer)

@admin_bp.route('/review_applications')
@login_required
def view_all_applications():
    filter_status = request.args.get('status')

    query = db.session.query(PT_XetTuyen, HSO_XETTUYEN.HoTen, Nganh.TenNganh)\
            .join(HSO_XETTUYEN, PT_XetTuyen.MaHSO == HSO_XETTUYEN.MaHSO)\
            .join(Nganh, PT_XetTuyen.MaNganh == Nganh.MaNganh)
    
    if filter_status:
        query = query.filter(PT_XetTuyen.TrangThai == filter_status)
    
    applications = query.order_by(PT_XetTuyen.MaPTXT.desc()).all()
    return render_template('admin/view_applications.html', applications=applications)


@admin_bp.route('/approve/<string:ma_ptxt>/<string:action>')
@login_required
def approve_admission(ma_ptxt, action):
    pt = db.get_or_404(PT_XetTuyen, ma_ptxt)

    if action == 'accept':
        pt.TrangThai = TrangThaiXT.TRUNG_TUYEN
    elif action == 'reject':
        pt.TrangThai = TrangThaiXT.TU_CHOI

    db.session.commit()
    return redirect(url_for('admin.view_all_applications'))

@admin_bp.route('/input_grade', methods=['GET', 'POST'])
@login_required
def input_grade():
    if request.method == 'POST':
        ma_sv = request.form.get('ma_sv')
        gpa = float(request.form.get('gpa'))

        if gpa >= 3.6:
            xeploai = XepLoaiSV.XUAT_SAC
        elif gpa >= 3.2:
            xeploai = XepLoaiSV.GIOI
        elif gpa >= 2.5:
            xeploai = XepLoaiSV.KHA
        elif gpa >= 2.0:
            xeploai = XepLoaiSV.TRUNG_BINH
        else:
            xeploai = XepLoaiSV.YEU
        
        tn = TotNghiep.query.filter_by(MaSV=ma_sv).first()
        try:
            if tn:
                tn.GPA = gpa
                tn.XepLoai = xeploai
            else:
                new_tn = TotNghiep(MaSV=ma_sv, GPA=gpa, XepLoai = xeploai)
                db.session.add(new_tn)
            db.session.commit()
            flash('Đã cập nhật điểm GPA cho sinh viên thành công!')
        except Exception as e:
            db.session.rollback()
            flash('GPA nằm trong khoảng 0.0 đến 4.0')

        return redirect(url_for('admin.input_grade'))
    dssv = SinhVien.query.all()
    return render_template('admin/input_grade.html', dssv=dssv)

@admin_bp.route('/graduation_list')
@login_required
def graduation_list():
    results = db.session.query(TotNghiep, SinhVien)\
                .join(SinhVien, TotNghiep.MaSV == SinhVien.MaSV)\
                .all()
    return render_template('admin/graduation_list.html', results=results)

@admin_bp.route('/send-notification', methods=['POST'])
@login_required
def send_notification():  
    nguoi_nhan = request.form.get('vai_tro')
    noi_dung = request.form.get('noi_dung')
    if not noi_dung:
        flash('Nội dung thông báo không được để trống')
        return redirect(url_for('admin.send_notification'))
    try:
        new_tb = ThongBao(
            NoiDung = noi_dung,
            NgayGui = datetime.now(),
            MaAdmin = current_user.quan_tri.MaAdmin
        )
        db.session.add(new_tb)
        db.session.flush()
        target_role = VaiTro.THISINH if nguoi_nhan == 'THISINH' else VaiTro.SINHVIEN
        recipients = TaiKhoan.query.filter_by(vai_tro=target_role).all()

        for user in recipients:
            receipt = TB_NguoiNhan(
                MaTB = new_tb.MaTB,
                ID_TaiKhoan = user.id,
                TrangThaiDoc = 0,
            )
            db.session.add(receipt)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi hệ thống: {str(e)}', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/student_jobs')
@login_required
def view_student_jobs():
    all_jobs = db.session.query(ViecLamSinhVien, SinhVien)\
                .join(SinhVien, ViecLamSinhVien.MaSV == SinhVien.MaSV)\
                .order_by(ViecLamSinhVien.NgayCapNhat.desc())\
                .all()
    
    return render_template('admin/student_jobs.html', all_jobs=all_jobs)