from flask import *
from flask_login import *
from extensions import db
from models import *
from datetime import date, datetime
from sqlalchemy.exc import SQLAlchemyError

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
@login_required
def manage_khoa():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        

        if form_type == 'add':
            ma_khoa = request.form.get('ma_khoa').strip().upper()
            ten_khoa = request.form.get('ten_khoa').strip()
            try:
                db.session.add(Khoa(MaKhoa=ma_khoa, TenKhoa=ten_khoa))
                db.session.commit()
                flash(f'Đã thêm khoa {ten_khoa} thành công!', 'success')
            except:
                db.session.rollback()
                flash('Lỗi: Mã khoa đã tồn tại!', 'danger')

        elif form_type == 'edit':
            ma_khoa_old = request.form.get('ma_khoa_old')
            khoa = Khoa.query.get(ma_khoa_old)
            if khoa:
                khoa.TenKhoa = request.form.get('ten_khoa').strip()
                db.session.commit()
                flash('Cập nhật tên khoa thành công!', 'success')

        return redirect(url_for('admin.manage_khoa'))

    all_khoas = Khoa.query.all()
    return render_template('admin/manage_khoa.html', all_khoas=all_khoas)

@admin_bp.route('/delete_khoa/<string:ma_khoa>')
@login_required
def delete_khoa(ma_khoa):
    khoa = Khoa.query.get_or_404(ma_khoa)
    try:
        db.session.delete(khoa)
        db.session.commit()
        flash('Đã xóa khoa thành công!', 'success')
    except:
        db.session.rollback()
        flash('Không thể xóa vì khoa này đang có ngành và lớp trực thuộc!', 'danger')
    return redirect(url_for('admin.manage_khoa'))

@admin_bp.route('/manage_nganh', methods=['GET', 'POST'])
@login_required
def manage_nganh():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        

        if form_type == 'add':
            ma_nganh = request.form.get('ma_nganh').strip().upper()
            ten_nganh = request.form.get('ten_nganh').strip()
            ma_khoa = request.form.get('ma_khoa')
            try:
                db.session.add(Nganh(MaNganh=ma_nganh, TenNganh=ten_nganh, MaKhoa=ma_khoa))
                db.session.commit()
                flash(f'Đã thêm ngành {ten_nganh} thành công!', 'success')
            except:
                db.session.rollback()
                flash('Lỗi: Mã ngành đã tồn tại hoặc dữ liệu không hợp lệ!', 'danger')

        elif form_type == 'edit':
            ma_nganh_old = request.form.get('ma_nganh_old')
            nganh = Nganh.query.get(ma_nganh_old)
            if nganh:
                nganh.TenNganh = request.form.get('ten_nganh').strip()
                nganh.MaKhoa = request.form.get('ma_khoa')
                db.session.commit()
                flash('Cập nhật ngành thành công!', 'success')

        return redirect(url_for('admin.manage_nganh'))

    all_nganhs = Nganh.query.all()
    khoas = Khoa.query.all()
    return render_template('admin/manage_nganh.html', all_nganhs=all_nganhs, khoas=khoas)

@admin_bp.route('/delete_nganh/<string:ma_nganh>')
@login_required
def delete_nganh(ma_nganh):
    nganh = Nganh.query.get_or_404(ma_nganh)
    try:
        db.session.delete(nganh)
        db.session.commit()
        flash('Đã xóa ngành thành công!', 'success')
    except:
        db.session.rollback()
        flash('Không thể xóa vì ngành này đang có lớp trực thuộc!', 'danger')
    return redirect(url_for('admin.manage_nganh'))

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

def _xep_loai_from_gpa(gpa):
    if gpa >= 3.6:
        return XepLoaiSV.XUAT_SAC
    if gpa >= 3.2:
        return XepLoaiSV.GIOI
    if gpa >= 2.5:
        return XepLoaiSV.KHA
    if gpa >= 2.0:
        return XepLoaiSV.TRUNG_BINH
    return XepLoaiSV.YEU

def _get_major_subjects(ma_nganh):
    if not ma_nganh:
        return []
    return db.session.query(MonHoc)\
        .join(NganhMonHoc, NganhMonHoc.MaMH == MonHoc.MaMH)\
        .filter(NganhMonHoc.MaNganh == ma_nganh)\
        .order_by(MonHoc.MaMH.asc())\
        .all()

def _build_student_grade_summary(student):
    lop = Lop.query.get(student.MaLop) if student.MaLop else None
    ma_nganh = lop.MaNganh if lop else None
    subjects = _get_major_subjects(ma_nganh)

    scores_map = {}
    if subjects:
        subject_codes = [s.MaMH for s in subjects]
        grades = KQ_HocTap.query.filter(
            KQ_HocTap.MaSV == student.MaSV,
            KQ_HocTap.MaMH.in_(subject_codes)
        ).all()
        scores_map = {g.MaMH: float(g.Diem) for g in grades}

    total_credits = sum(int(s.SoTinChi) for s in subjects)
    earned_credits = 0
    graded_credits = 0
    weighted_total = 0.0
    graded_subjects = 0
    subject_items = []

    for subject in subjects:
        score = scores_map.get(subject.MaMH)
        if score is not None:
            graded_subjects += 1
            graded_credits += int(subject.SoTinChi)
            weighted_total += _convert_10_to_4_scale(score) * int(subject.SoTinChi)
            if score >= 4.0:
                earned_credits += int(subject.SoTinChi)

        subject_items.append({
            'MaMH': subject.MaMH,
            'TenMH': subject.TenMH,
            'SoTinChi': int(subject.SoTinChi),
            'Diem': score
        })

    cpa = round(weighted_total / graded_credits, 2) if graded_credits > 0 else None
    has_all_scores = subjects and graded_subjects == len(subjects)
    eligible_for_graduation = bool(subjects) and has_all_scores and earned_credits >= total_credits

    if not student.MaLop:
        status_text = 'Chưa có lớp'
    elif not subjects:
        status_text = 'Ngành chưa cấu hình môn học'
    elif eligible_for_graduation:
        status_text = 'Đủ điều kiện tốt nghiệp'
    elif graded_subjects < len(subjects):
        status_text = 'Chưa nhập đủ điểm tất cả môn'
    else:
        status_text = 'Chưa đạt đủ tín chỉ'

    return {
        'student': student,
        'subjects': subject_items,
        'cpa': cpa,
        'xep_loai': _xep_loai_from_gpa(cpa).value if cpa is not None else '---',
        'total_credits': total_credits,
        'earned_credits': earned_credits,
        'required_subjects': len(subjects),
        'graded_subjects': graded_subjects,
        'eligible_for_graduation': eligible_for_graduation,
        'status_text': status_text
    }

def _queue_graduation_notification(student, cpa, admin_profile):
    if not student.ID_TaiKhoan:
        return

    new_tb = ThongBao(
        NoiDung=f"Chúc mừng {student.HoTen}! Bạn đã đủ điều kiện xét tốt nghiệp. CPA hiện tại: {cpa:.2f}.",
        NgayGui=datetime.now(),
        MaAdmin=admin_profile.MaAdmin
    )
    db.session.add(new_tb)
    db.session.flush()

    db.session.add(TB_NguoiNhan(
        MaTB=new_tb.MaTB,
        ID_TaiKhoan=student.ID_TaiKhoan,
        TrangThaiDoc=False
    ))

@admin_bp.route('/input_grade', methods=['GET', 'POST'])
@login_required
def input_grade():
    
    action = request.args.get('action')
    target_id = request.args.get('target_id')

    if action == 'get_nganh':
        nganhs = Nganh.query.filter_by(MaKhoa=target_id).all()
        return jsonify([{'id':n.MaNganh, 'name': n.TenNganh} for n in nganhs])
    
    if action == 'get_lops':
        lop = Lop.query.filter_by(MaNganh=target_id).all()
        return jsonify([{'id': n.MaLop, 'name': n.TenLop} for n in lop])
    
    ma_khoa_filter = (request.args.get('ma_khoa') or request.form.get('ma_khoa_filter') or '').strip().upper()
    ma_nganh_filter = (request.args.get('ma_nganh') or request.form.get('ma_nganh_filter') or '').strip().upper()
    ma_lop_filter = (request.args.get('ma_lop') or request.form.get('ma_lop_filter') or '').strip().upper()

    has_filter = bool(ma_khoa_filter or ma_nganh_filter or ma_lop_filter)
    student_summaries = []
    filter_label = None

    if request.method == 'POST':
        ma_sv = (request.form.get('ma_sv') or '').strip().upper()
        student = SinhVien.query.get_or_404(ma_sv)

        lop = Lop.query.get(student.MaLop) if student.MaLop else None
        ma_nganh = lop.MaNganh if lop else None
        subjects = _get_major_subjects(ma_nganh)

        if not subjects:
            flash('Ngành của sinh viên chưa được cấu hình môn học!', 'danger')
            return redirect(url_for('admin.input_grade', ma_khoa=ma_khoa_filter, ma_nganh=ma_nganh_filter, ma_lop=ma_lop_filter))

        try:
            for subject in subjects:
                key = f"diem_{subject.MaMH}"
                raw_score = (request.form.get(key) or '').strip()

                if raw_score == '':
                    continue

                score = float(raw_score.replace(',', '.'))
                if score < 0 or score > 10:
                    raise ValueError(f'Điểm môn {subject.MaMH} phải trong khoảng 0 đến 10')

                grade = KQ_HocTap.query.filter_by(MaSV=ma_sv, MaMH=subject.MaMH).first()
                if grade:
                    grade.Diem = round(score, 2)
                else:
                    db.session.add(KQ_HocTap(MaSV=ma_sv, MaMH=subject.MaMH, Diem=round(score, 2)))

            db.session.flush()
            summary = _build_student_grade_summary(student)

            graduation = TotNghiep.query.get(student.MaSV)
            was_eligible_before = graduation is not None
            if summary['eligible_for_graduation'] and summary['cpa'] is not None:
                xep_loai = _xep_loai_from_gpa(summary['cpa'])
                if graduation:
                    graduation.GPA = summary['cpa']
                    graduation.XepLoai = xep_loai
                else:
                    db.session.add(TotNghiep(MaSV=student.MaSV, GPA=summary['cpa'], XepLoai=xep_loai))

                if not was_eligible_before:
                    admin_profile = QuanTri.query.filter_by(ID_TaiKhoan=current_user.id).first()
                    if not admin_profile:
                        admin_profile = QuanTri(HoTen=current_user.ten_dang_nhap, ID_TaiKhoan=current_user.id)
                        db.session.add(admin_profile)
                        db.session.flush()
                    _queue_graduation_notification(student, summary['cpa'], admin_profile)
            elif graduation:
                db.session.delete(graduation)

            db.session.commit()
            flash(
                f"Đã cập nhật điểm cho {student.MaSV}. CPA hiện tại: "
                f"{summary['cpa'] if summary['cpa'] is not None else '---'}",
                'success'
            )
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Không thể lưu điểm chi tiết môn học. Vui lòng thử lại.', 'danger')

        return redirect(url_for('admin.input_grade', ma_khoa=ma_khoa_filter, ma_nganh=ma_nganh_filter, ma_lop=ma_lop_filter))

    if has_filter:
        query = SinhVien.query.join(Lop, SinhVien.MaLop == Lop.MaLop).join(Nganh, Lop.MaNganh == Nganh.MaNganh)

        if ma_khoa_filter:
            query = query.filter(Nganh.MaKhoa == ma_khoa_filter)
        if ma_nganh_filter:
            query = query.filter(Lop.MaNganh == ma_nganh_filter)
        if ma_lop_filter:
            query = query.filter(SinhVien.MaLop == ma_lop_filter)

        students = query.order_by(SinhVien.MaSV.asc()).all()
        student_summaries = [_build_student_grade_summary(s) for s in students]

        if ma_lop_filter:
            lop = Lop.query.get(ma_lop_filter)
            filter_label = f"Lớp: {lop.TenLop if lop else ma_lop_filter}"
        elif ma_nganh_filter:
            nganh = Nganh.query.get(ma_nganh_filter)
            filter_label = f"Ngành: {nganh.TenNganh if nganh else ma_nganh_filter}"
        elif ma_khoa_filter:
            khoa = Khoa.query.get(ma_khoa_filter)
            filter_label = f"Khoa: {khoa.TenKhoa if khoa else ma_khoa_filter}"

    khoas = Khoa.query.all()
    return render_template(
        'admin/input_grade.html',
        khoas=khoas,
        students=student_summaries,
        ma_khoa_filter=ma_khoa_filter,
        ma_nganh_filter=ma_nganh_filter,
        ma_lop_filter=ma_lop_filter,
        has_filter=has_filter,
        filter_label=filter_label
    )

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
    if current_user.vai_tro != VaiTro.ADMIN:
        flash('Bạn không có quyền gửi thông báo hệ thống!', 'danger')
        return redirect(url_for('admin.dashboard'))

    nguoi_nhan = (request.form.get('vai_tro') or '').strip().upper()
    noi_dung = (request.form.get('noi_dung') or '').strip()
    if not noi_dung:
        flash('Nội dung thông báo không được để trống', 'danger')
        return redirect(url_for('admin.dashboard'))

    if nguoi_nhan not in ['THISINH', 'SINHVIEN']:
        flash('Đối tượng nhận không hợp lệ!', 'danger')
        return redirect(url_for('admin.dashboard'))

    admin_profile = QuanTri.query.filter_by(ID_TaiKhoan=current_user.id).first()
    created_admin_profile = False
    if not admin_profile:
        try:
            admin_profile = QuanTri(HoTen=current_user.ten_dang_nhap, ID_TaiKhoan=current_user.id)
            db.session.add(admin_profile)
            db.session.flush()
            created_admin_profile = True
        except SQLAlchemyError:
            db.session.rollback()
            flash('Không thể khởi tạo hồ sơ quản trị để gửi thông báo.', 'danger')
            return redirect(url_for('admin.dashboard'))

    target_role = VaiTro.THISINH if nguoi_nhan == 'THISINH' else VaiTro.SINHVIEN
    recipients = TaiKhoan.query.filter_by(vai_tro=target_role).all()
    if not recipients:
        if created_admin_profile:
            db.session.commit()
        flash('Không có tài khoản phù hợp để nhận thông báo.', 'warning')
        return redirect(url_for('admin.dashboard'))

    try:
        new_tb = ThongBao(
            NoiDung=noi_dung,
            NgayGui=datetime.now(),
            MaAdmin=admin_profile.MaAdmin
        )
        db.session.add(new_tb)
        db.session.flush()

        for user in recipients:
            receipt = TB_NguoiNhan(
                MaTB=new_tb.MaTB,
                ID_TaiKhoan=user.id,
                TrangThaiDoc=False,
            )
            db.session.add(receipt)
        db.session.commit()
        flash('Đã gửi thông báo thành công!', 'success')
    except SQLAlchemyError as e:
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

@admin_bp.route('/create_student', methods=['GET', 'POST'])
@login_required
def create_student():

    action = request.args.get('action')
    target_id = request.args.get('target_id')

    if action == 'get_nganh':
        nganhs = Nganh.query.filter_by(MaKhoa=target_id).all()
        return jsonify([{'id': n.MaNganh, 'name': n.TenNganh} for n in nganhs])
    
    if action == 'get_lops':
        lops = Lop.query.filter_by(MaNganh=target_id).all()
        return jsonify([{'id': l.MaLop, 'name': l.TenLop} for l in lops])
    
    if request.method == 'POST':
        ma_sv = request.form.get('ma_sv')
        ho_ten = request.form.get('ho_ten')
        email = request.form.get('email')
        ngay_sinh = datetime.strptime(request.form.get('ngay_sinh'), '%Y-%m-%d').date()
        ma_lop = request.form.get('ma_lop')

        ten_dang_nhap = ma_sv
        mat_khau = ma_sv
        try:
            new_user = TaiKhoan(
                ten_dang_nhap = ten_dang_nhap,
                mat_khau = mat_khau,
                vai_tro = VaiTro.SINHVIEN 
            )
            db.session.add(new_user)
            db.session.flush()

            new_sv = SinhVien(
                MaSV = ma_sv,
                HoTen = ho_ten,
                NgaySinh = ngay_sinh,
                Email = email,
                MaLop = ma_lop,
                ID_TaiKhoan = new_user.id
            )
            db.session.add(new_sv)
            db.session.commit()
            flash('Đã tạo thành công sinh viên')
            return redirect(url_for('admin.create_student'))
        except Exception as e:
            db.session.rollback()
            flash("Lỗi: {str(e)}")
    khoas = Khoa.query.all()
    return render_template('admin/create_student.html', khoas=khoas)

@admin_bp.route('/manage_students', methods=['GET', 'POST'])
@login_required
def manage_students():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'edit':
            ma_sv = request.form.get('ma_sv')
            ho_ten = request.form.get('ho_ten')
            email = request.form.get('email')
            ngay_sinh_raw = request.form.get('ngay_sinh')
            ma_lop = request.form.get('ma_lop')

            student = SinhVien.query.get_or_404(ma_sv)
            lop = Lop.query.get(ma_lop)
            if not lop:
                flash('Lớp không tồn tại!', 'danger')
                return redirect(url_for('admin.manage_students'))

            email_exists = SinhVien.query.filter(
                SinhVien.Email == email,
                SinhVien.MaSV != ma_sv
            ).first()
            if email_exists:
                flash('Email đã được sử dụng bởi sinh viên khác!', 'danger')
                return redirect(url_for('admin.manage_students'))

            try:
                ngay_sinh = datetime.strptime(ngay_sinh_raw, '%Y-%m-%d').date()
                student.HoTen = ho_ten
                student.Email = email
                student.NgaySinh = ngay_sinh
                student.MaLop = ma_lop
                db.session.commit()
                flash(f'Đã cập nhật thông tin sinh viên {ma_sv}', 'success')
            except ValueError:
                flash('Ngày sinh không hợp lệ!', 'danger')
            except SQLAlchemyError:
                db.session.rollback()
                flash('Không thể cập nhật sinh viên. Vui lòng thử lại.', 'danger')

        return redirect(url_for('admin.manage_students'))

    students = SinhVien.query.order_by(SinhVien.MaSV.asc()).all()
    all_lops = Lop.query.order_by(Lop.MaLop.asc()).all()
    lop_map = {lop.MaLop: lop.TenLop for lop in all_lops}
    return render_template(
        'admin/manage_students.html',
        students=students,
        all_lops=all_lops,
        lop_map=lop_map
    )

@admin_bp.route('/delete_student/<string:ma_sv>')
@login_required
def delete_student(ma_sv):
    student = SinhVien.query.get_or_404(ma_sv)
    tai_khoan = TaiKhoan.query.get(student.ID_TaiKhoan) if student.ID_TaiKhoan else None

    try:
        KQ_HocTap.query.filter_by(MaSV=student.MaSV).delete(synchronize_session=False)
        TotNghiep.query.filter_by(MaSV=student.MaSV).delete(synchronize_session=False)
        ViecLamSinhVien.query.filter_by(MaSV=student.MaSV).delete(synchronize_session=False)

        if tai_khoan:
            TB_NguoiNhan.query.filter_by(ID_TaiKhoan=tai_khoan.id).delete(synchronize_session=False)

        db.session.delete(student)
        db.session.flush()

        if tai_khoan:
            db.session.delete(tai_khoan)

        db.session.commit()
        flash(f'Đã xóa sinh viên {ma_sv}', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Không thể xóa sinh viên này vì còn dữ liệu liên quan!', 'danger')

    return redirect(url_for('admin.manage_students'))

@admin_bp.route('/manage_subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    selected_nganh = (request.args.get('ma_nganh') or '').strip().upper()

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        selected_nganh = (request.form.get('ma_nganh_filter') or selected_nganh).strip().upper()

        if form_type == 'add':
            ma_nganh = (request.form.get('ma_nganh') or '').strip().upper()
            ma_mh = (request.form.get('ma_mh') or '').strip().upper()
            ten_mh = (request.form.get('ten_mh') or '').strip()
            so_tin_chi_raw = (request.form.get('so_tin_chi') or '').strip()
            selected_nganh = ma_nganh or selected_nganh

            if not ma_nganh or not ma_mh or not ten_mh or not so_tin_chi_raw:
                flash('Vui lòng nhập đầy đủ thông tin môn học!', 'danger')
                return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

            nganh = Nganh.query.get(ma_nganh)
            if not nganh:
                flash('Ngành không tồn tại!', 'danger')
                return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

            try:
                so_tin_chi = int(so_tin_chi_raw)
                if so_tin_chi <= 0:
                    raise ValueError
            except ValueError:
                flash('Số tín chỉ phải là số nguyên dương!', 'danger')
                return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

            mon_hoc = MonHoc.query.get(ma_mh)
            if mon_hoc and (mon_hoc.TenMH != ten_mh or mon_hoc.SoTinChi != so_tin_chi):
                flash('Mã môn đã tồn tại với tên môn hoặc số tín chỉ khác. Vui lòng kiểm tra lại.', 'danger')
                return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

            try:
                if not mon_hoc:
                    mon_hoc = MonHoc(MaMH=ma_mh, TenMH=ten_mh, SoTinChi=so_tin_chi)
                    db.session.add(mon_hoc)

                exist_link = NganhMonHoc.query.filter_by(MaNganh=ma_nganh, MaMH=ma_mh).first()
                if exist_link:
                    flash('Môn học đã tồn tại trong ngành này!', 'warning')
                else:
                    db.session.add(NganhMonHoc(MaNganh=ma_nganh, MaMH=ma_mh))
                    db.session.commit()
                    flash(f'Đã thêm môn {ma_mh} cho ngành {ma_nganh}', 'success')
            except SQLAlchemyError:
                db.session.rollback()
                flash('Không thể thêm môn học. Vui lòng thử lại.', 'danger')

        elif form_type == 'edit':
            ma_mh = (request.form.get('ma_mh') or '').strip().upper()
            ten_mh = (request.form.get('ten_mh') or '').strip()
            so_tin_chi_raw = (request.form.get('so_tin_chi') or '').strip()

            if not ma_mh or not ten_mh or not so_tin_chi_raw:
                flash('Thiếu thông tin để cập nhật môn học!', 'danger')
                return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

            try:
                so_tin_chi = int(so_tin_chi_raw)
                if so_tin_chi <= 0:
                    raise ValueError
            except ValueError:
                flash('Số tín chỉ phải là số nguyên dương!', 'danger')
                return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

            mon_hoc = MonHoc.query.get(ma_mh)
            if not mon_hoc:
                flash('Môn học không tồn tại!', 'danger')
                return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

            try:
                mon_hoc.TenMH = ten_mh
                mon_hoc.SoTinChi = so_tin_chi
                db.session.commit()
                flash(f'Đã cập nhật môn học {ma_mh}', 'success')
            except SQLAlchemyError:
                db.session.rollback()
                flash('Không thể cập nhật môn học.', 'danger')

        return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

    nganhs = Nganh.query.order_by(Nganh.TenNganh.asc()).all()
    selected_nganh_obj = Nganh.query.get(selected_nganh) if selected_nganh else None

    subjects = []
    if selected_nganh:
        subjects = db.session.query(MonHoc)\
            .join(NganhMonHoc, NganhMonHoc.MaMH == MonHoc.MaMH)\
            .filter(NganhMonHoc.MaNganh == selected_nganh)\
            .order_by(MonHoc.MaMH.asc())\
            .all()

    return render_template(
        'admin/manage_subjects.html',
        nganhs=nganhs,
        selected_nganh=selected_nganh,
        selected_nganh_obj=selected_nganh_obj,
        subjects=subjects
    )

@admin_bp.route('/manage_subjects/remove/<string:ma_nganh>/<string:ma_mh>')
@login_required
def remove_subject_from_major(ma_nganh, ma_mh):
    selected_nganh = (request.args.get('ma_nganh') or ma_nganh).strip().upper()
    link = NganhMonHoc.query.filter_by(MaNganh=ma_nganh, MaMH=ma_mh).first()

    if not link:
        flash('Không tìm thấy liên kết môn học - ngành cần xóa!', 'danger')
        return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

    try:
        db.session.delete(link)
        db.session.commit()
        flash(f'Đã gỡ môn {ma_mh} khỏi ngành {ma_nganh}', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Không thể gỡ môn học khỏi ngành.', 'danger')

    return redirect(url_for('admin.manage_subjects', ma_nganh=selected_nganh))

@admin_bp.route('/manage_lops', methods = ['GET', 'POST'])
@login_required
def manage_lops():
    if request.args.get('action') == 'get_nganh':
        ma_khoa = request.args.get('ma_khoa')
        nganhs = Nganh.query.filter_by(MaKhoa=ma_khoa).all()
        return jsonify([{'id': n.MaNganh, 'name': n.TenNganh} for n in nganhs])
    
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'add':
            ma_lop = request.form.get('ma_lop').strip().upper()
            ten_lop = request.form.get('ten_lop').strip()
            ma_nganh = request.form.get('ma_nganh')

            try:
                db.session.add(Lop(MaLop=ma_lop, TenLop=ten_lop, MaNganh=ma_nganh))
                db.session.commit()
                flash('Đã thêm lớp')
            except:
                db.session.rollback()
                flash('Lỗi')

        elif form_type =='edit':
            ma_lop_old = request.form.get('ma_lop_old')
            lop = Lop.query.get(ma_lop_old)
            if lop: 
                lop.TenLop = request.form.get('ten_lop').strip()
                lop.MaNganh = request.form.get('ma_nganh')
                db.session.commit()
                flash('Cập nhật thành công')

    return render_template('admin/manage_lops.html',
                        khoas = Khoa.query.all(),
                        all_lops = Lop.query.all())


@admin_bp.route('/delete_lop/<string:ma_lop>')
@login_required
def delete_lop(ma_lop):
    lop = Lop.query.get_or_404(ma_lop)
    try:
        db.session.delete(lop)
        db.session.commit()
        flash('Đã xóa lớp thành công')
    except:
        db.session.rollback()
        flash('Không thể xóa vì có sinh viên đang học')
    return redirect(url_for('admin.manage_lops'))

@admin_bp.route('/manage_view')
@login_required
def manage_view():
    level = request.args.get('level', 'khoa') 
    parent_id = request.args.get('parent_id')
    
    data = []
    title = ""
    back_url = None

    if level == 'khoa':
        data = Khoa.query.all()
        title = "DANH SÁCH KHOA"
    
    elif level == 'nganh':
        data = Nganh.query.filter_by(MaKhoa=parent_id).all()
        title = f"NGÀNH THUỘC KHOA: {parent_id}"
        back_url = url_for('admin.manage_view', level='khoa')
        
    elif level == 'lop':
        data = Lop.query.filter_by(MaNganh=parent_id).all()
        title = f"LỚP THUỘC NGÀNH: {parent_id}"

        nganh = Nganh.query.get(parent_id)
        back_url = url_for('admin.manage_view', level='nganh', parent_id=nganh.MaKhoa)
        
    elif level == 'sv':
        data = SinhVien.query.filter_by(MaLop=parent_id).all()
        title = f"SINH VIÊN LỚP: {parent_id}"
        lop = Lop.query.get(parent_id)
        back_url = url_for('admin.manage_view', level='lop', parent_id=lop.MaNganh)

    return render_template('admin/manage_view.html', 
                           data=data, level=level, title=title, 
                           back_url=back_url, parent_id=parent_id)
