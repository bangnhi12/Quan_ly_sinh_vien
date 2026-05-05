"""
Module Quản lý Môn học
- Thêm/sửa/xóa môn học
- Import Excel
- Tìm kiếm, lọc, phân trang
- Soft delete
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from extensions import db
from models import MonHoc, Nganh, NganhMonHoc
from datetime import datetime
import pandas as pd
from sqlalchemy import or_, and_

# Tạo Blueprint
admin_mon_bp = Blueprint('admin_mon', __name__, url_prefix='/admin/monhoc')

# ==================== DANH SÁCH MÔN HỌC ====================
@admin_mon_bp.route('/list', methods=['GET', 'POST'])
@login_required
def list_mon():
    """Hiển thị danh sách môn học với tìm kiếm, lọc, phân trang"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    hoc_ky = request.args.get('hoc_ky', '', type=str)
    trang_thai = request.args.get('trang_thai', '', type=str)
    
    # Base query
    query = MonHoc.query
    
    # Tìm kiếm
    if search:
        query = query.filter(or_(
            MonHoc.MaMon.contains(search),
            MonHoc.TenMon.contains(search)
        ))
    
    # Lọc theo học kỳ
    if hoc_ky:
        query = query.filter(MonHoc.HocKy == int(hoc_ky))
    
    # Lọc theo trạng thái
    if trang_thai:
        trang_thai_bool = trang_thai == 'active'
        query = query.filter(MonHoc.TrangThai == trang_thai_bool)
    
    # Sắp xếp
    query = query.order_by(MonHoc.MaMon)
    
    # Phân trang
    pagination = query.paginate(page=page, per_page=10)
    mon_hocs = pagination.items
    
    # Lấy danh sách học kỳ duy nhất để hiển thị trong filter
    hoc_kys = db.session.query(MonHoc.HocKy).distinct().filter(MonHoc.HocKy != None).all()
    hoc_kys = [hk[0] for hk in hoc_kys if hk[0] is not None]
    
    return render_template('admin/monhoc_list.html',
                         mon_hocs=mon_hocs,
                         pagination=pagination,
                         search=search,
                         hoc_ky=hoc_ky,
                         trang_thai=trang_thai,
                         hoc_kys=hoc_kys)

# ==================== THÊM MÔN HỌC ====================
@admin_mon_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_mon():
    """Thêm môn học mới"""
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            ma_mon = request.form.get('ma_mon', '').strip().upper()
            ten_mon = request.form.get('ten_mon', '').strip()
            so_tin_chi = request.form.get('so_tin_chi', type=int)
            hoc_ky = request.form.get('hoc_ky', type=int)
            mo_ta = request.form.get('mo_ta', '').strip()
            
            # Validate
            if not ma_mon or not ten_mon or not so_tin_chi:
                flash('Vui lòng nhập đầy đủ thông tin bắt buộc!', 'danger')
                return redirect(url_for('admin_mon.add_mon'))
            
            if so_tin_chi <= 0:
                flash('Số tín chỉ phải lớn hơn 0!', 'danger')
                return redirect(url_for('admin_mon.add_mon'))
            
            # Kiểm tra mã môn đã tồn tại
            existing = MonHoc.query.filter_by(MaMon=ma_mon).first()
            if existing:
                flash(f'Mã môn "{ma_mon}" đã tồn tại!', 'danger')
                return redirect(url_for('admin_mon.add_mon'))
            
            # Tạo môn học mới
            mon_hoc = MonHoc(
                MaMon=ma_mon,
                TenMon=ten_mon,
                SoTinChi=so_tin_chi,
                HocKy=hoc_ky if hoc_ky else None,
                MoTa=mo_ta if mo_ta else None,
                TrangThai=True
            )
            
            db.session.add(mon_hoc)
            db.session.commit()
            
            flash(f'Thêm môn học "{ten_mon}" thành công!', 'success')
            return redirect(url_for('admin_mon.list_mon'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')
            return redirect(url_for('admin_mon.add_mon'))
    
    return render_template('admin/monhoc_add.html')

# ==================== CHỈNH SỬA MÔN HỌC ====================
@admin_mon_bp.route('/edit/<string:ma_mon>', methods=['GET', 'POST'])
@login_required
def edit_mon(ma_mon):
    """Chỉnh sửa thông tin môn học"""
    mon_hoc = MonHoc.query.get_or_404(ma_mon)
    
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            ten_mon = request.form.get('ten_mon', '').strip()
            so_tin_chi = request.form.get('so_tin_chi', type=int)
            hoc_ky = request.form.get('hoc_ky', type=int)
            mo_ta = request.form.get('mo_ta', '').strip()
            trang_thai = request.form.get('trang_thai') == 'on'
            
            # Validate
            if not ten_mon or not so_tin_chi:
                flash('Vui lòng nhập đầy đủ thông tin!', 'danger')
                return redirect(url_for('admin_mon.edit_mon', ma_mon=ma_mon))
            
            if so_tin_chi <= 0:
                flash('Số tín chỉ phải lớn hơn 0!', 'danger')
                return redirect(url_for('admin_mon.edit_mon', ma_mon=ma_mon))
            
            # Cập nhật
            mon_hoc.TenMon = ten_mon
            mon_hoc.SoTinChi = so_tin_chi
            mon_hoc.HocKy = hoc_ky if hoc_ky else None
            mon_hoc.MoTa = mo_ta if mo_ta else None
            mon_hoc.TrangThai = trang_thai
            mon_hoc.NgayCapNhat = datetime.now()
            
            db.session.commit()
            flash('Cập nhật môn học thành công!', 'success')
            return redirect(url_for('admin_mon.list_mon'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')
            return redirect(url_for('admin_mon.edit_mon', ma_mon=ma_mon))
    
    return render_template('admin/monhoc_edit.html', mon_hoc=mon_hoc)

# ==================== XÓA MÔN HỌC (SOFT DELETE) ====================
@admin_mon_bp.route('/delete/<string:ma_mon>', methods=['POST'])
@login_required
def delete_mon(ma_mon):
    """Xóa mềm môn học (chỉ cập nhật trạng thái)"""
    mon_hoc = MonHoc.query.get_or_404(ma_mon)
    
    try:
        # Xóa mềm: chỉ set TrangThai = False
        mon_hoc.TrangThai = False
        mon_hoc.NgayCapNhat = datetime.now()
        db.session.commit()
        
        flash(f'Đã vô hiệu hóa môn học "{mon_hoc.TenMon}"!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi: {str(e)}', 'danger')
    
    return redirect(url_for('admin_mon.list_mon'))

# ==================== PHỤC HỒI MÔN HỌC ====================
@admin_mon_bp.route('/restore/<string:ma_mon>', methods=['POST'])
@login_required
def restore_mon(ma_mon):
    """Phục hồi môn học bị vô hiệu hóa"""
    mon_hoc = MonHoc.query.get_or_404(ma_mon)
    
    try:
        mon_hoc.TrangThai = True
        mon_hoc.NgayCapNhat = datetime.now()
        db.session.commit()
        
        flash(f'Đã kích hoạt lại môn học "{mon_hoc.TenMon}"!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi: {str(e)}', 'danger')
    
    return redirect(url_for('admin_mon.list_mon'))

# ==================== IMPORT EXCEL ====================
@admin_mon_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_excel():
    """Import danh sách môn học từ file Excel"""
    if request.method == 'POST':
        try:
            # Kiểm tra file upload
            if 'file' not in request.files:
                flash('Vui lòng chọn file!', 'danger')
                return redirect(url_for('admin_mon.import_excel'))
            
            file = request.files['file']
            if file.filename == '':
                flash('Vui lòng chọn file!', 'danger')
                return redirect(url_for('admin_mon.import_excel'))
            
            # Kiểm tra định dạng file
            if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
                flash('Chỉ hỗ trợ file .xlsx, .xls hoặc .csv!', 'danger')
                return redirect(url_for('admin_mon.import_excel'))
            
            # Đọc file Excel
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
            except Exception as e:
                flash(f'Lỗi đọc file: {str(e)}', 'danger')
                return redirect(url_for('admin_mon.import_excel'))
            
            # Validate cột yêu cầu
            required_cols = ['MaMon', 'TenMon', 'SoTinChi']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                flash(f'File thiếu cột: {", ".join(missing_cols)}', 'danger')
                return redirect(url_for('admin_mon.import_excel'))
            
            # Import dữ liệu
            success_count = 0
            error_list = []
            
            for idx, row in df.iterrows():
                try:
                    ma_mon = str(row['MaMon']).strip().upper()
                    ten_mon = str(row['TenMon']).strip()
                    so_tin_chi = int(row['SoTinChi'])
                    hoc_ky = int(row['HocKy']) if 'HocKy' in df.columns and pd.notna(row['HocKy']) else None
                    mo_ta = str(row['MoTa']).strip() if 'MoTa' in df.columns and pd.notna(row['MoTa']) else None
                    
                    # Validate
                    if not ma_mon or not ten_mon or so_tin_chi <= 0:
                        error_list.append(f"Dòng {idx+2}: Dữ liệu không hợp lệ")
                        continue
                    
                    # Kiểm tra trùng lặp
                    if MonHoc.query.filter_by(MaMon=ma_mon).first():
                        error_list.append(f"Dòng {idx+2}: Mã môn {ma_mon} đã tồn tại")
                        continue
                    
                    # Thêm môn học
                    mon_hoc = MonHoc(
                        MaMon=ma_mon,
                        TenMon=ten_mon,
                        SoTinChi=so_tin_chi,
                        HocKy=hoc_ky,
                        MoTa=mo_ta,
                        TrangThai=True
                    )
                    db.session.add(mon_hoc)
                    success_count += 1
                    
                except Exception as e:
                    error_list.append(f"Dòng {idx+2}: {str(e)}")
            
            db.session.commit()
            
            # Flash message
            if success_count > 0:
                flash(f'Đã thêm {success_count} môn học thành công!', 'success')
            
            if error_list:
                flash(f'Có {len(error_list)} dòng lỗi: ' + '; '.join(error_list[:5]), 'warning')
            
            return redirect(url_for('admin_mon.list_mon'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')
            return redirect(url_for('admin_mon.import_excel'))
    
    return render_template('admin/monhoc_import.html')

# ==================== API - Lấy dữ liệu cho DataTables ====================
@admin_mon_bp.route('/api/list', methods=['GET'])
@login_required
def api_list_mon():
    """API endpoint cho DataTables"""
    draw = request.args.get('draw', 1, type=int)
    start = request.args.get('start', 0, type=int)
    length = request.args.get('length', 10, type=int)
    search_value = request.args.get('search[value]', '', type=str)
    
    # Query
    query = MonHoc.query
    
    # Search
    if search_value:
        query = query.filter(or_(
            MonHoc.MaMon.contains(search_value),
            MonHoc.TenMon.contains(search_value)
        ))
    
    # Total
    total_records = MonHoc.query.count()
    filtered_records = query.count()
    
    # Pagination
    mon_hocs = query.offset(start).limit(length).all()
    
    # Format data
    data = []
    for mon in mon_hocs:
        data.append({
            'MaMon': mon.MaMon,
            'TenMon': mon.TenMon,
            'SoTinChi': mon.SoTinChi,
            'HocKy': mon.HocKy or '-',
            'MoTa': mon.MoTa or '-',
            'TrangThai': 'Hoạt động' if mon.TrangThai else 'Vô hiệu',
            'NgayCapNhat': mon.NgayCapNhat.strftime('%d/%m/%Y %H:%M') if mon.NgayCapNhat else ''
        })
    
    return jsonify({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })

# ==================== BULK ACTIONS ====================
@admin_mon_bp.route('/bulk-action', methods=['POST'])
@login_required
def bulk_action():
    """Xử lý hành động hàng loạt"""
    action = request.form.get('action')
    selected_ids = request.form.getlist('selected_ids')
    
    if not selected_ids:
        flash('Vui lòng chọn ít nhất một môn học!', 'warning')
        return redirect(url_for('admin_mon.list_mon'))
    
    try:
        if action == 'delete':
            # Xóa mềm
            MonHoc.query.filter(MonHoc.MaMon.in_(selected_ids)).update(
                {'TrangThai': False},
                synchronize_session=False
            )
            flash(f'Đã vô hiệu hóa {len(selected_ids)} môn học!', 'success')
        
        elif action == 'restore':
            # Phục hồi
            MonHoc.query.filter(MonHoc.MaMon.in_(selected_ids)).update(
                {'TrangThai': True},
                synchronize_session=False
            )
            flash(f'Đã kích hoạt {len(selected_ids)} môn học!', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi: {str(e)}', 'danger')
    
    return redirect(url_for('admin_mon.list_mon'))
