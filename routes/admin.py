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
        .filter(PT_XetTuyen.TrangThai == TrangThaiXT.CHO_DUYET)\
        .order_by(HSO_XETTUYEN.HoTen.asc())\
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
    
    applications = query.order_by(HSO_XETTUYEN.HoTen.asc()).all()
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
    action = request.args.get('action')
    target_id = request.args.get('target_id')

    if action == 'get_nganh':
        nganhs = Nganh.query.filter_by(MaKhoa=target_id).all()
        return jsonify([{'id':n.MaNganh, 'name': n.TenNganh} for n in nganhs])
    
    if action == 'get_lops':
        lop = Lop.query.filter_by(MaNganh=target_id).all()
        return jsonify([{'id': n.MaLop, 'name': n.TenLop} for n in lop])

    ma_lop_filter = request.args.get('ma_lop')
    students = []
    if ma_lop_filter:
 
        sv_da_co_diem = db.session.query(TotNghiep.MaSV).all()
        list_ma_sv_da_co_diem = [r[0] for r in sv_da_co_diem]
        students = SinhVien.query.filter(
            SinhVien.MaLop == ma_lop_filter,
            ~SinhVien.MaSV.in_(list_ma_sv_da_co_diem)
        ).all()

    if request.method == 'POST':
        try:
            ma_sv = request.form.get('ma_sv')
            gpa_raw = request.form.get('gpa')
            if not gpa_raw:
                return jsonify({'status': 'error', 'message': 'Chưa nhập điểm'}), 400
            
            gpa = float(gpa_raw)

            if gpa >= 3.6: xeploai = XepLoaiSV.XUAT_SAC
            elif gpa >= 3.2: xeploai = XepLoaiSV.GIOI
            elif gpa >= 2.5: xeploai = XepLoaiSV.KHA
            elif gpa >= 2.0: xeploai = XepLoaiSV.TRUNG_BINH
            else: xeploai = XepLoaiSV.YEU

            ket_qua = db.session.get(TotNghiep, ma_sv)
            if ket_qua:
                ket_qua.GPA = gpa
                ket_qua.XepLoai = xeploai
            else:
                db.session.add(TotNghiep(MaSV=ma_sv, GPA=gpa, XepLoai=xeploai))
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'Đã lưu điểm cho {ma_sv}'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    khoas = Khoa.query.all()
    return render_template('admin/input_grade.html', khoas=khoas, students=students, ma_lop_filter=ma_lop_filter)

@admin_bp.route('/graduation_list')
@login_required
def graduation_list():
    ma_khoa = request.args.get('ma_khoa')
    ma_nganh = request.args.get('ma_nganh')
    ma_lop = request.args.get('ma_lop')
    xep_loai = request.args.get('xep_loai')

    students = []
    if ma_khoa or ma_nganh or ma_lop or xep_loai:
        query = db.session.query(SinhVien)
        if ma_lop:
            query = query.filter(SinhVien.MaLop == ma_lop)
        elif ma_nganh:
            query = query.join(Lop, SinhVien.MaLop == ma_lop)
        elif ma_khoa:
            query = query.join(Lop, SinhVien.MaLop == Lop.MaLop)\
                        .join(Nganh, Lop.MaNganh == Nganh.MaNganh)\
                        .filter(Nganh.MaKhoa == ma_khoa)
        
        if xep_loai and xep_loai != 'all':
            try:
                target_enum = XepLoaiSV[xep_loai]
                query = query.join(TotNghiep, SinhVien.MaSV == TotNghiep.MaSV)\
                                .filter(TotNghiep.XepLoai == target_enum)
            except KeyError:
                pass
        students = query.all()
    khoas = Khoa.query.all()
    return render_template('admin/graduation_list.html',
                           students = students,
                           khoas = khoas,
                           xep_loai_enum = XepLoaiSV)
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