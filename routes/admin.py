import os

from flask import *
from flask_login import *
from models import LoaiPhuongThuc
from sqlalchemy import exists
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
# Quản lý tổ hợp 
@admin_bp.route('to_hop_mon', methods=['GET', 'POST'])
@login_required
def quanlytohop():
    if request.method == 'POST':
        ten_th = request.form.get('ten_to_hop').upper()
        cac_mon = ",".join([m.strip() for m in request.form.get('cac_mon').split(',') if m.strip()])
        moi = ToHopMon(TenToHop=ten_th,
                    CacMon = cac_mon)
        db.session.add(moi)
        db.session.commit()
        flash('Thêm tổ hợp thành công!')
        return redirect(url_for('admin.quanlytohop'))
    ds_tohop = ToHopMon.query.all()
    return render_template('admin/quan_ly_to_hop.html', ds_tohop=ds_tohop)
@admin_bp.route('/to_hop_mon/sua/<int:id>', methods=['POST'])
@login_required
def sua_to_hop(id):
    th = ToHopMon.query.get(id)
    th.TenToHop = request.form.get('ten_to_hop')
    cac_mon_raw = request.form.get('cac_mon')
    th.CacMon = ",".join([m.strip() for m in cac_mon_raw.split(',') if m.strip()])
    db.session.commit()
    flash("Cập nhật thành công", "success")
    return redirect(url_for('admin.quanlytohop'))
@admin_bp.route('/to_hop_mon/xoa/<int:id>')
@login_required
def xoa_to_hop(id):
    th = ToHopMon.query.get_or_404(id)
    try:
        db.session.delete(th)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Không thể xóa vì tổ hợp này đang được sử dụng trong hồ sơ khác!", "danger")
    return redirect(url_for('admin.quanlytohop'))
@admin_bp.route('/gan-to-hop', methods=['GET', 'POST'])
@login_required
def gan_to_hop():
    if request.method == 'POST':
        ma_nganh = request.form.get('ma_nganh')
        cac_ma_to_hop = request.form.getlist('to_hop_ids') 
        nganh = Nganh.query.get(ma_nganh)
        nganh.ds_to_hop = [] 
        for th_id in cac_ma_to_hop:
            to_hop = ToHopMon.query.get(int(th_id))
            nganh.ds_to_hop.append(to_hop)
            
        db.session.commit()
        return redirect(url_for('admin.gan_to_hop'))

    ds_nganh = Nganh.query.all()
    ds_to_hop = ToHopMon.query.all()
    return render_template('admin/gan_to_hop.html', ds_nganh=ds_nganh, ds_to_hop=ds_to_hop)


@admin_bp.route('/api/get_to_hop/<ma_nganh>')
def get_to_hop_api(ma_nganh):
    nganh = Nganh.query.get(ma_nganh)
    if not nganh:
        return jsonify([])
    return jsonify([{
        'id': th.MaToHop,
        'ten': th.TenToHop,
        'cac_mon': th.CacMon
    } for th in nganh.ds_to_hop])

@admin_bp.route('/admin/duyet_thi_sinh', methods=['GET', 'POST'])
def duyet_thi_sinh():
    ds_nganh = Nganh.query.all()

    if request.method == 'POST':

        ma_nganh = request.form.get('ma_nganh')
        chi_tieu = int(request.form.get('chi_tieu'))
        loai_pt_raw = request.form.get('loai_pt').strip()
        print(loai_pt_raw)
        loai_pt = None
        for member in LoaiPhuongThuc: 
            if member.value == loai_pt_raw:
                loai_pt = member
                break
        if loai_pt is None:
            print(f"DEBUG: Khong tim thay {loai_pt_raw} trong Enum!")
            flash(f"Loại phương thức '{loai_pt_raw}' không hợp lệ!", "danger")
            return redirect(url_for('admin.duyet_thi_sinh'))

        # Lấy danh sách chờ duyệt theo ngành + phương thức
        danh_sach = PT_XetTuyen.query.filter_by(
            MaNganh=ma_nganh,
            LoaiPT=loai_pt,
            TrangThai=TrangThaiXT.CHO_DUYET
        ).order_by(PT_XetTuyen.Diem.desc()).all()

        count = 0

        for hs in danh_sach:
            if count >= chi_tieu:
                break
            da_trung_tuyen = PT_XetTuyen.query.filter(
                PT_XetTuyen.MaHSO == hs.MaHSO,
                PT_XetTuyen.TrangThai == TrangThaiXT.TRUNG_TUYEN
            ).first()

            if da_trung_tuyen:
                continue
            hs.TrangThai = TrangThaiXT.TRUNG_TUYEN
            ma_khoa = hs.nganh.MaKhoa if hs.nganh else "XX"
            stt = str(hs.MaHSO).zfill(3)
            ma_sv = f"D23DC{ma_khoa}{stt}"
            if not SinhVien.query.filter_by(MaHSO=hs.MaHSO).first():

                new_sv = SinhVien(
                    MaSV=ma_sv,
                    HoTen=hs.ho_so.HoTen,
                    NgaySinh=hs.ho_so.NgaySinh,
                    Email=hs.ho_so.Email,
                    ID_TaiKhoan=hs.ho_so.ID_TaiKhoan,
                    MaHSO=hs.MaHSO,
                    MaLop=None
                )
                db.session.add(new_sv)
            if hs.ho_so and hs.ho_so.tai_khoan:
                hs.ho_so.tai_khoan.vai_tro = VaiTro.SINHVIEN

            db.session.add(hs)
            count += 1
        db.session.commit()
        flash(f"Đã duyệt thành công {count} thí sinh!", "success")
        return redirect(url_for('admin.duyet_thi_sinh'))
    ds_tong_quat = PT_XetTuyen.query.all()

    return render_template(
        'admin/view_applications.html',
        ds_nganh=ds_nganh,
        ds_tong_quat=ds_tong_quat,
        datetime=datetime
    )

@admin_bp.route('/api/get_candidates')
def get_candidates():
    try:
        ma_nganh = request.args.get('ma_nganh')
        loai_pt_raw = request.args.get('loai_pt')
        loai_pt = next((m for m in LoaiPhuongThuc if m.value == loai_pt_raw), None)
        if not loai_pt:
            return jsonify({"pending": [], "passed": []})
        ds_pending = PT_XetTuyen.query.filter_by(
            MaNganh=ma_nganh, LoaiPT=loai_pt, TrangThai=TrangThaiXT.CHO_DUYET
        ).order_by(PT_XetTuyen.Diem.desc()).all()
        ds_passed = PT_XetTuyen.query.filter_by(
            MaNganh=ma_nganh, LoaiPT=loai_pt, TrangThai=TrangThaiXT.TRUNG_TUYEN
        ).order_by(PT_XetTuyen.Diem.desc()).all()
        def format_data(danh_sach, is_pending=True):
            res = []
            for hs in danh_sach:
                is_muted = False
                trang_thai_text = hs.TrangThai.value            
                if is_pending:
                    da_trung_tuyen_khac = PT_XetTuyen.query.filter(
                        PT_XetTuyen.MaHSO == hs.MaHSO,
                        PT_XetTuyen.TrangThai == TrangThaiXT.TRUNG_TUYEN
                    ).first()
                    if da_trung_tuyen_khac:
                        trang_thai_text = "Đã trúng tuyển ngành khác"
                        is_muted = True
                res.append({
                    "MaHSO": hs.MaHSO,
                    "HoTen": hs.ho_so.HoTen if hs.ho_so else "N/A",
                    "MaNganh": hs.MaNganh,
                    "Diem": float(hs.Diem),
                    "TrangThai": trang_thai_text,
                    "IsMuted": is_muted,
                    "MaPTXT": hs.MaPTXT
                })
            return res
        return jsonify({
            "pending": format_data(ds_pending, is_pending=True),
            "passed": format_data(ds_passed, is_pending=False)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
import os
from flask import send_from_directory, current_app
from urllib.parse import unquote # Thêm dòng này

@admin_bp.route('/admin/view-file/<path:filename>')
def view_file(filename):
    filename = unquote(filename)
    actual_filename = os.path.basename(filename)
    project_dir = os.path.dirname(current_app.root_path) 
    upload_path = os.path.join(project_dir, 'uploads')
    full_path = os.path.join(upload_path, actual_filename)
    if not os.path.exists(full_path):
        upload_path = os.path.join(current_app.root_path, 'uploads')
        full_path = os.path.join(upload_path, actual_filename)
    return send_from_directory(upload_path, actual_filename, as_attachment=False)

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

import pandas as pd
import io
from datetime import datetime
from flask import request, flash, redirect, url_for
from models import db, Khoa, Nganh, Lop, SinhVien, TaiKhoan, VaiTro 

@admin_bp.route('/import_students_minimal', methods=['POST'])
@login_required
def import_students_minimal():
    file = request.files.get('file_excel')
    if not file or file.filename == '':
        flash('Vui lòng chọn file CSV!', 'danger')
        return redirect(url_for('admin.create_student'))

    index = -1 
    try:
        raw_data = file.stream.read().decode("utf-8-sig")
        stream = io.StringIO(raw_data)
        df = pd.read_csv(stream, sep=None, engine='python')

        if df.empty:
            flash('File CSV không có dữ liệu!', 'warning')
            return redirect(url_for('admin.create_student'))
        df.columns = [str(c).strip() for c in df.columns]

        print(f"--- DEBUG: Danh sách cột hệ thống đọc được: {df.columns.tolist()}")
        if 'MaKhoa' not in df.columns:
            flash(f"Lỗi: Không tìm thấy cột 'MaKhoa'. File hiện có các cột: {', '.join(df.columns)}", 'danger')
            return redirect(url_for('admin.create_student'))

        success_count = 0
        for index, row in df.iterrows():
            mk = str(row['MaKhoa']).strip()
            mn = str(row['MaNganh']).strip()
            ml = str(row['MaLop']).strip()
            msv = str(row['MaSV']).strip()
            hoten = str(row['HoTen']).strip()
            email = str(row['Email']).strip()
            ngay_sinh_str = str(row['NgaySinh']).strip()
            khoa = db.session.get(Khoa, mk)
            if not khoa:
                khoa = Khoa(MaKhoa=mk, TenKhoa=f"Khoa {mk}")
                db.session.add(khoa)
            nganh = db.session.get(Nganh, mn)
            if not nganh:
                nganh = Nganh(MaNganh=mn, TenNganh=f"Ngành {mn}", MaKhoa=mk)
                db.session.add(nganh)
            lop = db.session.get(Lop, ml)
            if not lop:
                lop = Lop(MaLop=ml, TenLop=f"Lớp {ml}", MaNganh=mn)
                db.session.add(lop)
            db.session.flush()
            if not db.session.get(SinhVien, msv):
                new_user = TaiKhoan(
                    ten_dang_nhap=msv,
                    mat_khau=msv, 
                    vai_tro=VaiTro.SINHVIEN
                )
                db.session.add(new_user)
                db.session.flush()
                try:
                    ngay_sinh = pd.to_datetime(ngay_sinh_str, dayfirst=True).date()
                except:
                    ngay_sinh = datetime.now().date()
                new_sv = SinhVien(
                    MaSV=msv,
                    HoTen=hoten,
                    NgaySinh=ngay_sinh,
                    Email=email,
                    MaLop=ml,
                    ID_TaiKhoan=new_user.id
                )
                db.session.add(new_sv)
                success_count += 1
        db.session.commit()
        flash(f'Import thành công {success_count} sinh viên từ file CSV!', 'success')
    except Exception as e:
        db.session.rollback()
        error_msg = f"Lỗi tại dòng {index + 2}: {str(e)}" if index >= 0 else f"Lỗi: {str(e)}"
        flash(error_msg, 'danger')
        print(f"--- LOG LỖI CHI TIẾT ---\n{str(e)}")

    return redirect(url_for('admin.create_student'))

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



from sqlalchemy import or_, and_, exists

@admin_bp.route('/tin_nhan', defaults={'user_id': None}, methods=['GET', 'POST'])
@admin_bp.route('/tin_nhan/<int:user_id>', methods=['GET', 'POST'])
@login_required
def quan_ly_tin_nhan(user_id):
    if current_user.vai_tro != VaiTro.ADMIN:
        return redirect(url_for('index'))

    role_filter = request.args.get('role')

    # 1. Lấy danh sách người đã nhắn tin
    contact_query = TaiKhoan.query.filter(exists().where(
        or_(TinNhan.ID_NguoiGui == TaiKhoan.id, TinNhan.ID_NguoiNhan == TaiKhoan.id)
    ))

    if role_filter == 'thisinh':
        contact_query = contact_query.filter(TaiKhoan.vai_tro == VaiTro.THISINH)
    elif role_filter == 'sinhvien':
        contact_query = contact_query.filter(TaiKhoan.vai_tro == VaiTro.SINHVIEN)

    contacts_raw = contact_query.distinct().all()

    # 2. QUAN TRỌNG: Gán unread_count cho từng contact
    contacts = []
    for c in contacts_raw:
        # Đếm tin nhắn từ người này gửi lên hệ thống (None) mà chưa đọc
        c.unread_count = TinNhan.query.filter(
            TinNhan.ID_NguoiGui == c.id,
            TinNhan.ID_NguoiNhan == None,
            TinNhan.DaDoc == False
        ).count()
        contacts.append(c)

    current_chat = None
    messages = []

    if user_id:
        current_chat = TaiKhoan.query.get_or_404(user_id)

        # 3. Đánh dấu đã đọc khi Admin nhấn vào chat
        TinNhan.query.filter_by(
            ID_NguoiGui=user_id, 
            ID_NguoiNhan=None, 
            DaDoc=False
        ).update({"DaDoc": True})
        db.session.commit()

        if request.method == 'POST':
            noi_dung = request.form.get('message')
            if noi_dung and noi_dung.strip():
                new_msg = TinNhan(
                    ID_NguoiGui=current_user.id,
                    ID_NguoiNhan=user_id,
                    NoiDung=noi_dung.strip()
                )
                db.session.add(new_msg)
                db.session.commit()
                return redirect(url_for('admin.quan_ly_tin_nhan', user_id=user_id, role=role_filter))

        # 4. Lấy lịch sử chat
        messages = TinNhan.query.filter(
            or_(
                and_(TinNhan.ID_NguoiGui == user_id, TinNhan.ID_NguoiNhan == None),
                and_(TinNhan.ID_NguoiNhan == user_id)
            )
        ).order_by(TinNhan.ThoiGianGui.asc()).all()

    return render_template(
        'admin/tin_nhan.html',
        contacts=contacts,
        messages=messages,
        current_chat=current_chat,
        active_role=role_filter
    )