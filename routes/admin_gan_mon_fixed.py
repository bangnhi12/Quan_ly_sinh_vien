"""
Module Gán Môn cho Ngành (Many-to-Many)
- Xem danh sách ngành (nhóm theo khoa)
- Xem môn học theo ngành
- Gán/bỏ gán môn cho ngành
- Kiểm tra trùng lặp
- Tìm kiếm nhanh
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from extensions import db
from models import Nganh, MonHoc, NganhMonHoc, Khoa
from datetime import datetime
from sqlalchemy import and_, func
from collections import defaultdict

# Tạo Blueprint
admin_gan_mon_bp = Blueprint('admin_gan_mon', __name__, url_prefix='/admin/gan-mon')

# ==================== DANH SÁCH NGÀNH (NHÓM THEO KHOA) ====================
@admin_gan_mon_bp.route('/list', methods=['GET'])
@login_required
def list_nganh():
    """Hiển thị danh sách ngành nhóm theo khoa"""
    # Lấy tất cả ngành với khoa
    nganhs = db.session.query(Nganh, Khoa).join(
        Khoa, Nganh.MaKhoa == Khoa.MaKhoa
    ).order_by(Khoa.TenKhoa, Nganh.TenNganh).all()
    
    # Nhóm ngành theo khoa (để frontend dễ xử lý)
    khoas_dict = defaultdict(list)
    for nganh, khoa in nganhs:
        khoas_dict[khoa.MaKhoa].append({
            'khoa': khoa,
            'nganh': nganh,
            'mon_count': len(nganh.mon_hocs)
        })
    
    # Convert sang list để dùng trong template
    khoas_grouped = []
    for khoa_code in sorted(khoas_dict.keys()):
        items = khoas_dict[khoa_code]
        khoa = items[0]['khoa']  # Khoa object (giống nhau cho tất cả items)
        khoas_grouped.append({
            'khoa': khoa,
            'nganhs': items
        })
    
    return render_template('admin/ganmon_list_nganh.html', khoas_grouped=khoas_grouped)

# ==================== GIAO DIỆN GÁN MÔN ====================
@admin_gan_mon_bp.route('/assign/<string:ma_nganh>', methods=['GET', 'POST'])
@login_required
def assign_mon(ma_nganh):
    """Giao diện gán môn cho ngành cụ thể"""
    nganh = Nganh.query.get_or_404(ma_nganh)
    
    # Lấy các môn đã gán cho ngành này (dùng composite key: MaNganh, MaMon)
    assigned_mons = db.session.query(NganhMonHoc.MaMon).filter(
        NganhMonHoc.MaNganh == ma_nganh
    ).all()
    assigned_mon_ids = [m[0] for m in assigned_mons]
    
    # Lấy tất cả môn học (chỉ lấy những môn đang hoạt động)
    all_mons = MonHoc.query.filter_by(TrangThai=True).order_by(MonHoc.MaMon).all()
    
    if request.method == 'POST':
        try:
            # Lấy danh sách môn được chọn từ form
            selected_mons = request.form.getlist('selected_mons')
            
            # Xóa tất cả gán cũ (delete by MaNganh)
            NganhMonHoc.query.filter_by(MaNganh=ma_nganh).delete()
            
            # Thêm gán mới
            for ma_mon in selected_mons:
                # Validate môn tồn tại
                if not MonHoc.query.filter_by(MaMon=ma_mon).first():
                    continue
                
                # Thêm bản ghi mới (composite key: MaNganh + MaMon)
                nganh_mon = NganhMonHoc(
                    MaNganh=ma_nganh,
                    MaMon=ma_mon,
                    NgayTao=datetime.now()
                )
                db.session.add(nganh_mon)
            
            db.session.commit()
            flash(f'Đã cập nhật {len(selected_mons)} môn học cho ngành "{nganh.TenNganh}"!', 'success')
            return redirect(url_for('admin_gan_mon.list_nganh'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')
            return redirect(url_for('admin_gan_mon.assign_mon', ma_nganh=ma_nganh))
    
    # Nhóm môn theo học kỳ để hiển thị dễ hơn
    mons_by_ky = {}
    for mon in all_mons:
        hoc_ky = mon.HocKy or 'Không xác định'
        if hoc_ky not in mons_by_ky:
            mons_by_ky[hoc_ky] = []
        mons_by_ky[hoc_ky].append(mon)
    
    return render_template('admin/ganmon_assign_mon.html',
                         nganh=nganh,
                         all_mons=all_mons,
                         assigned_mon_ids=assigned_mon_ids,
                         mons_by_ky=mons_by_ky)

# ==================== BỎ GÁN MÔN (DELETE BY COMPOSITE KEY: MaNganh + MaMon) ====================
@admin_gan_mon_bp.route('/unassign/<string:ma_nganh>/<string:ma_mon>', methods=['POST'])
@login_required
def unassign_mon(ma_nganh, ma_mon):
    """Bỏ gán môn khỏi ngành (delete by composite key)"""
    try:
        # Query by composite key: MaNganh + MaMon
        nganh_mon = NganhMonHoc.query.filter(
            and_(
                NganhMonHoc.MaNganh == ma_nganh,
                NganhMonHoc.MaMon == ma_mon
            )
        ).first_or_404()
        
        # Get môn info để flash message
        mon = MonHoc.query.get(ma_mon)
        
        db.session.delete(nganh_mon)
        db.session.commit()
        
        flash(f'Đã bỏ gán môn "{mon.TenMon}" ({ma_mon})!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi bỏ gán: {str(e)}', 'danger')
    
    return redirect(url_for('admin_gan_mon.view_mons_by_nganh', ma_nganh=ma_nganh))

# ==================== API - Lấy môn theo ngành ====================
@admin_gan_mon_bp.route('/api/mons/<string:ma_nganh>', methods=['GET'])
@login_required
def api_get_mons_by_nganh(ma_nganh):
    """API lấy danh sách môn của ngành"""
    # Lấy các môn gán cho ngành (join bằng composite key)
    mons = db.session.query(MonHoc).join(
        NganhMonHoc, and_(
            MonHoc.MaMon == NganhMonHoc.MaMon,
            NganhMonHoc.MaNganh == ma_nganh
        )
    ).all()
    
    data = []
    for mon in mons:
        data.append({
            'MaMon': mon.MaMon,
            'TenMon': mon.TenMon,
            'SoTinChi': mon.SoTinChi,
            'HocKy': mon.HocKy or '-',
            'MoTa': mon.MoTa or '-'
        })
    
    return jsonify(data)

# ==================== API - Tìm kiếm môn ====================
@admin_gan_mon_bp.route('/api/search-mons', methods=['GET'])
@login_required
def api_search_mons():
    """API tìm kiếm môn học"""
    query_str = request.args.get('q', '', type=str)
    ma_nganh = request.args.get('ma_nganh', '', type=str)
    
    # Lấy các môn đã gán (by composite key)
    if ma_nganh:
        assigned_mons = db.session.query(NganhMonHoc.MaMon).filter(
            NganhMonHoc.MaNganh == ma_nganh
        ).all()
        assigned_mon_ids = [m[0] for m in assigned_mons]
    else:
        assigned_mon_ids = []
    
    # Tìm kiếm
    query = MonHoc.query.filter_by(TrangThai=True)
    
    if query_str:
        from sqlalchemy import or_
        query = query.filter(or_(
            MonHoc.MaMon.contains(query_str),
            MonHoc.TenMon.contains(query_str)
        ))
    
    mons = query.limit(20).all()
    
    data = []
    for mon in mons:
        data.append({
            'MaMon': mon.MaMon,
            'TenMon': mon.TenMon,
            'SoTinChi': mon.SoTinChi,
            'HocKy': mon.HocKy or '-',
            'assigned': mon.MaMon in assigned_mon_ids
        })
    
    return jsonify(data)

# ==================== DANH SÁCH CHI TIẾT MÔN CỦA NGÀNH ====================
@admin_gan_mon_bp.route('/view/<string:ma_nganh>', methods=['GET'])
@login_required
def view_mons_by_nganh(ma_nganh):
    """Xem danh sách môn của một ngành"""
    nganh = Nganh.query.get_or_404(ma_nganh)
    khoa = Khoa.query.get(nganh.MaKhoa)
    
    # Lấy các môn gán cho ngành (query bằng composite key: MaNganh + MaMon)
    mons = db.session.query(MonHoc, NganhMonHoc.NgayTao).join(
        NganhMonHoc, and_(
            MonHoc.MaMon == NganhMonHoc.MaMon,
            NganhMonHoc.MaNganh == ma_nganh
        )
    ).order_by(MonHoc.MaMon).all()
    
    # Tính tổng tín chỉ
    #total_tin_chi = sum(mon[0].SoTinChi for mon in mons)
    total_tin_chi = sum((mon[0].SoTinChi or 0) for mon in mons)
    
    return render_template('admin/ganmon_view_mons.html',
                         nganh=nganh,
                         khoa=khoa,
                         mons=mons,
                         total_tin_chi=total_tin_chi)

# ==================== REPORT - THỐNG KÊ ====================
@admin_gan_mon_bp.route('/report', methods=['GET'])
@login_required
def report():
    """Báo cáo thống kê gán môn"""
    # Lấy tất cả ngành
    nganhs = Nganh.query.order_by(Nganh.TenNganh).all()
    
    # Thống kê
    stats = []
    for nganh in nganhs:
        # Count môn của ngành (query by composite key)
        mon_count = db.session.query(func.count(NganhMonHoc.MaMon)).filter(
            NganhMonHoc.MaNganh == nganh.MaNganh
        ).scalar() or 0
        
        # Tính tổng tín chỉ
        total_tin_chi = db.session.query(func.sum(MonHoc.SoTinChi)).join(
            NganhMonHoc, and_(
                MonHoc.MaMon == NganhMonHoc.MaMon,
                NganhMonHoc.MaNganh == nganh.MaNganh
            )
        ).scalar() or 0
        
        stats.append({
            'nganh': nganh,
            'khoa': nganh.khoa if hasattr(nganh, 'khoa') else Khoa.query.get(nganh.MaKhoa),
            'mon_count': mon_count,
            'total_tin_chi': total_tin_chi
        })
    
    # Nhóm theo khoa để hiển thị dễ hơn
    khoas_stats = defaultdict(list)
    for stat in stats:
        khoa = stat['khoa']
        khoas_stats[khoa.MaKhoa].append(stat)
    
    # Convert sang list
    khoas_grouped_stats = []
    for khoa_code in sorted(khoas_stats.keys()):
        khoas_grouped_stats.append({
            'khoa': khoas_stats[khoa_code][0]['khoa'],
            'stats': khoas_stats[khoa_code]
        })
    
    return render_template('admin/ganmon_report.html', khoas_grouped_stats=khoas_grouped_stats)
