# ============================================================
# ADMIN DIEM BLUEPRINT: Grade Management System
# ============================================================
# Features:
# 1. Nhập điểm theo Excel (Excel import)
# 2. Tra cứu điểm (Grade query)
# 3. Thống kê học tập (Learning statistics)
# ============================================================

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from models import db, Diem, SinhVien, MonHoc, Lop, Nganh, TaiKhoan, VaiTro
from sqlalchemy import and_, func, desc, or_
from datetime import datetime
import pandas as pd
import openpyxl
from io import BytesIO
import os

# ============================================================
# BLUEPRINT SETUP
# ============================================================

admin_diem_bp = Blueprint('admin_diem', __name__, url_prefix='/admin/diem')

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def check_admin():
    """Check if current user is admin"""
    if not current_user.is_authenticated or current_user.vai_tro != VaiTro.ADMIN:
        flash('Chỉ admin mới có quyền truy cập', 'danger')
        return False
    return True

def validate_score(score):
    """Validate score is in range 0-10"""
    try:
        score_float = float(score)
        return 0 <= score_float <= 10
    except:
        return False

def parse_excel_file(file):
    """Parse Excel file and return DataFrame"""
    try:
        # Read Excel file
        df = pd.read_excel(file, sheet_name=0)
        
        # Check required columns
        required_columns = ['MSSV', 'Họ tên', 'Lớp', 'Điểm quá trình', 'Điểm thi', 'Điểm tổng kết']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"Thiếu các cột: {', '.join(missing_columns)}"
        
        # Clean data (remove empty rows)
        df = df.dropna(how='all')
        
        return df, None
    except Exception as e:
        return None, f"Lỗi đọc file Excel: {str(e)}"

def process_excel_grades(df, ma_mon, hoc_ky=None, nam_hoc=None):
    """
    Process grades from Excel DataFrame
    Returns: (success_count, update_count, failed_count, error_list)
    """
    success_count = 0
    update_count = 0
    failed_list = []
    
    for idx, row in df.iterrows():
        try:
            ma_sv = str(row['MSSV']).strip()
            diem_qt = row['Điểm quá trình']
            diem_thi = row['Điểm thi']
            diem_tk = row['Điểm tổng kết']
            
            # Validate MSSV
            if not ma_sv or len(ma_sv) == 0:
                failed_list.append({
                    'row': idx + 2,
                    'mssv': 'N/A',
                    'reason': 'MSSV trống'
                })
                continue
            
            # Check student exists
            sinh_vien = SinhVien.query.filter_by(MaSV=ma_sv).first()
            if not sinh_vien:
                failed_list.append({
                    'row': idx + 2,
                    'mssv': ma_sv,
                    'reason': f'MSSV không tồn tại trong hệ thống'
                })
                continue
            
            # Validate scores
            if pd.isna(diem_tk):
                failed_list.append({
                    'row': idx + 2,
                    'mssv': ma_sv,
                    'reason': 'Điểm tổng kết bắt buộc'
                })
                continue
            
            try:
                diem_tk_float = float(diem_tk)
            except:
                failed_list.append({
                    'row': idx + 2,
                    'mssv': ma_sv,
                    'reason': f'Điểm tổng kết không hợp lệ: {diem_tk}'
                })
                continue
            
            if not validate_score(diem_tk_float):
                failed_list.append({
                    'row': idx + 2,
                    'mssv': ma_sv,
                    'reason': f'Điểm tổng kết phải trong khoảng 0-10'
                })
                continue
            
            # Convert process and exam scores
            diem_qt_float = None
            diem_thi_float = None
            
            if not pd.isna(diem_qt):
                try:
                    diem_qt_float = float(diem_qt)
                    if not validate_score(diem_qt_float):
                        failed_list.append({
                            'row': idx + 2,
                            'mssv': ma_sv,
                            'reason': f'Điểm quá trình phải trong khoảng 0-10'
                        })
                        continue
                except:
                    failed_list.append({
                        'row': idx + 2,
                        'mssv': ma_sv,
                        'reason': f'Điểm quá trình không hợp lệ: {diem_qt}'
                    })
                    continue
            
            if not pd.isna(diem_thi):
                try:
                    diem_thi_float = float(diem_thi)
                    if not validate_score(diem_thi_float):
                        failed_list.append({
                            'row': idx + 2,
                            'mssv': ma_sv,
                            'reason': f'Điểm thi phải trong khoảng 0-10'
                        })
                        continue
                except:
                    failed_list.append({
                        'row': idx + 2,
                        'mssv': ma_sv,
                        'reason': f'Điểm thi không hợp lệ: {diem_thi}'
                    })
                    continue
            
            # Check if grade record already exists
            existing_diem = Diem.query.filter(
                and_(
                    Diem.MaSV == ma_sv,
                    Diem.MaMon == ma_mon,
                    Diem.HocKy == hoc_ky,
                    Diem.NamHoc == nam_hoc
                )
            ).first()
            
            if existing_diem:
                # UPDATE existing record
                existing_diem.DiemQT = diem_qt_float
                existing_diem.DiemThi = diem_thi_float
                existing_diem.DiemTK = diem_tk_float
                existing_diem.TrangThai = True
                existing_diem.NgayCapNhat = datetime.now()
                db.session.add(existing_diem)
                update_count += 1
            else:
                # INSERT new record
                new_diem = Diem(
                    MaSV=ma_sv,
                    MaMon=ma_mon,
                    DiemQT=diem_qt_float,
                    DiemThi=diem_thi_float,
                    DiemTK=diem_tk_float,
                    HocKy=hoc_ky,
                    NamHoc=nam_hoc,
                    TrangThai=True
                )
                db.session.add(new_diem)
                success_count += 1
        
        except Exception as e:
            failed_list.append({
                'row': idx + 2,
                'mssv': str(row.get('MSSV', 'N/A')),
                'reason': f'Lỗi xử lý: {str(e)}'
            })
    
    # Commit all changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return 0, 0, len(df), [{'reason': f'Lỗi lưu database: {str(e)}'}]
    
    return success_count, update_count, len(failed_list), failed_list

def calculate_gpa_semester(ma_sv, hoc_ky, nam_hoc=None):
    """Calculate GPA for a specific semester"""
    # Query all grades for this student in this semester
    grades = Diem.query.filter(
        and_(
            Diem.MaSV == ma_sv,
            Diem.HocKy == hoc_ky,
            Diem.TrangThai == True
        )
    ).all()
    
    if not grades:
        return 0.0
    
    total_credits = 0
    total_score_credits = 0
    
    for grade in grades:
        try:
            mon = MonHoc.query.filter_by(MaMon=grade.MaMon).first()
            if mon and mon.SoTinChi:
                diem_4scale = convert_to_4scale(grade.DiemTK)
                total_score_credits += diem_4scale * mon.SoTinChi
                total_credits += mon.SoTinChi
        except:
            pass
    
    if total_credits == 0:
        return 0.0
    
    return round(total_score_credits / total_credits, 2)

def calculate_gpa_cumulative(ma_sv):
    """Calculate cumulative GPA for a student"""
    grades = Diem.query.filter(
        and_(
            Diem.MaSV == ma_sv,
            Diem.TrangThai == True
        )
    ).all()
    
    if not grades:
        return 0.0
    
    total_credits = 0
    total_score_credits = 0
    
    for grade in grades:
        try:
            mon = MonHoc.query.filter_by(MaMon=grade.MaMon).first()
            if mon and mon.SoTinChi:
                diem_4scale = convert_to_4scale(grade.DiemTK)
                total_score_credits += diem_4scale * mon.SoTinChi
                total_credits += mon.SoTinChi
        except:
            pass
    
    if total_credits == 0:
        return 0.0
    
    return round(total_score_credits / total_credits, 2)

def convert_to_4scale(diem_10):
    """Convert 10-point scale to 4-point scale"""
    if diem_10 >= 9:
        return 4.0
    elif diem_10 >= 8.5:
        return 3.8
    elif diem_10 >= 8:
        return 3.5
    elif diem_10 >= 7.5:
        return 3.2
    elif diem_10 >= 7:
        return 3.0
    elif diem_10 >= 6.5:
        return 2.8
    elif diem_10 >= 6:
        return 2.5
    elif diem_10 >= 5.5:
        return 2.2
    elif diem_10 >= 5:
        return 2.0
    elif diem_10 >= 4:
        return 1.0
    else:
        return 0.0

def get_academic_standing(gpa):
    """Get academic standing based on GPA"""
    if gpa >= 3.5:
        return "Xuất sắc"
    elif gpa >= 3.0:
        return "Giỏi"
    elif gpa >= 2.0:
        return "Khá"
    elif gpa >= 1.0:
        return "Trung bình (Cảnh báo)"
    else:
        return "Yếu (Bị cảnh báo)"

# ============================================================
# ROUTES
# ============================================================

@admin_diem_bp.route('/')
@login_required
def index():
    """Main grade management page"""
    if not check_admin():
        return redirect(url_for('admin.dashboard'))
    
    return redirect(url_for('admin_diem.upload_page'))

# ============================================================
# 1. EXCEL IMPORT ROUTES
# ============================================================

@admin_diem_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_page():
    """Grade upload page"""
    if not check_admin():
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        return upload_grades()
    
    # GET: Show upload form
    courses = MonHoc.query.order_by(MonHoc.TenMon).all()
    
    return render_template('admin/diem_upload.html', courses=courses)

def upload_grades():
    """Handle Excel file upload"""
    try:
        # Get form data
        ma_mon = request.form.get('ma_mon')
        hoc_ky = request.form.get('hoc_ky')
        nam_hoc = request.form.get('nam_hoc')
        
        # Validate course selection
        if not ma_mon:
            flash('Vui lòng chọn môn học', 'warning')
            return redirect(url_for('admin_diem.upload_page'))
        
        # Check course exists
        mon_hoc = MonHoc.query.filter_by(MaMon=ma_mon).first()
        if not mon_hoc:
            flash('Môn học không tồn tại', 'danger')
            return redirect(url_for('admin_diem.upload_page'))
        
        # Get file
        if 'file' not in request.files:
            flash('Không có file được tải lên', 'danger')
            return redirect(url_for('admin_diem.upload_page'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Vui lòng chọn file', 'danger')
            return redirect(url_for('admin_diem.upload_page'))
        
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            flash('Chỉ chấp nhận file Excel (.xlsx hoặc .xls)', 'danger')
            return redirect(url_for('admin_diem.upload_page'))
        
        # Parse Excel file
        df, error = parse_excel_file(file)
        if error:
            flash(f'Lỗi: {error}', 'danger')
            return redirect(url_for('admin_diem.upload_page'))
        
        # Convert semester and year to integers if provided
        try:
            hoc_ky = int(hoc_ky) if hoc_ky else None
            nam_hoc = int(nam_hoc) if nam_hoc else None
        except:
            hoc_ky = None
            nam_hoc = None
        
        # Process Excel grades
        success, updated, failed_count, failed_list = process_excel_grades(
            df, ma_mon, hoc_ky, nam_hoc
        )
        
        # Store result in session for result page
        result_data = {
            'ma_mon': ma_mon,
            'ten_mon': mon_hoc.TenMon,
            'hoc_ky': hoc_ky,
            'nam_hoc': nam_hoc,
            'total_rows': len(df),
            'success_count': success,
            'update_count': updated,
            'failed_count': failed_count,
            'failed_list': failed_list[:50]  # Limit to first 50 errors
        }
        
        flash(f'Nhập thành công {success + updated}/{len(df)} sinh viên', 'success')
        
        return render_template('admin/diem_import_result.html', result=result_data)
    
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('admin_diem.upload_page'))

# ============================================================
# 2. GRADE QUERY ROUTES
# ============================================================

@admin_diem_bp.route('/query', methods=['GET', 'POST'])
@login_required
def query_page():
    """Grade query page"""
    if not check_admin():
        return redirect(url_for('admin.dashboard'))
    
    mode = request.args.get('mode', 'student')  # student, course, class
    results = []
    query_info = {}
    
    if request.method == 'POST':
        if mode == 'student':
            # Query by student
            ma_sv = request.form.get('ma_sv')
            if ma_sv:
                results = query_student_grades(ma_sv)
                query_info = {'mode': 'student', 'ma_sv': ma_sv}
        
        elif mode == 'course':
            # Query by course
            ma_mon = request.form.get('ma_mon')
            if ma_mon:
                results = query_course_grades(ma_mon)
                query_info = {'mode': 'course', 'ma_mon': ma_mon}
        
        elif mode == 'class':
            # Query by class + course
            ma_lop = request.form.get('ma_lop')
            ma_mon = request.form.get('ma_mon')
            if ma_lop and ma_mon:
                results = query_class_grades(ma_lop, ma_mon)
                query_info = {'mode': 'class', 'ma_lop': ma_lop, 'ma_mon': ma_mon}
    
    # Get options for dropdowns
    courses = MonHoc.query.order_by(MonHoc.TenMon).all()
    classes = Lop.query.order_by(Lop.TenLop).all()
    students = SinhVien.query.order_by(SinhVien.HoTen).all()
    
    return render_template(
        'admin/diem_query.html',
        mode=mode,
        results=results,
        query_info=query_info,
        courses=courses,
        classes=classes,
        students=students
    )

def query_student_grades(ma_sv):
    """Get all grades for a student"""
    # Check student exists
    sinh_vien = SinhVien.query.filter_by(MaSV=ma_sv).first()
    if not sinh_vien:
        flash(f'Sinh viên {ma_sv} không tồn tại', 'warning')
        return []
    
    # Get all grades
    grades = Diem.query.filter(
        and_(Diem.MaSV == ma_sv, Diem.TrangThai == True)
    ).order_by(desc(Diem.HocKy)).all()
    
    return grades

def query_course_grades(ma_mon):
    """Get all grades for a course"""
    # Check course exists
    mon_hoc = MonHoc.query.filter_by(MaMon=ma_mon).first()
    if not mon_hoc:
        flash(f'Môn học {ma_mon} không tồn tại', 'warning')
        return []
    
    # Get all grades
    grades = Diem.query.filter(
        and_(Diem.MaMon == ma_mon, Diem.TrangThai == True)
    ).order_by(desc(Diem.DiemTK)).all()
    
    return grades

def query_class_grades(ma_lop, ma_mon):
    """Get grades for all students in a class for a specific course"""
    # Get all students in class
    students = SinhVien.query.filter_by(MaLop=ma_lop).all()
    
    if not students:
        flash(f'Lớp {ma_lop} không có sinh viên', 'warning')
        return []
    
    # Get grades
    ma_sv_list = [s.MaSV for s in students]
    grades = Diem.query.filter(
        and_(
            Diem.MaMon == ma_mon,
            Diem.MaSV.in_(ma_sv_list),
            Diem.TrangThai == True
        )
    ).order_by(desc(Diem.DiemTK)).all()
    
    return grades

# ============================================================
# 3. STATISTICS ROUTES
# ============================================================

@admin_diem_bp.route('/stats', methods=['GET'])
@login_required
def stats_page():
    """Learning statistics page"""
    if not check_admin():
        return redirect(url_for('admin.dashboard'))
    
    ma_sv = request.args.get('ma_sv')
    stats = {}
    
    if ma_sv:
        # Check student exists
        sinh_vien = SinhVien.query.filter_by(MaSV=ma_sv).first()
        if not sinh_vien:
            flash(f'Sinh viên {ma_sv} không tồn tại', 'warning')
        else:
            stats = calculate_student_stats(ma_sv)
    
    students = SinhVien.query.order_by(SinhVien.HoTen).all()
    
    return render_template(
        'admin/diem_stats.html',
        stats=stats,
        ma_sv=ma_sv,
        students=students
    )

def calculate_student_stats(ma_sv):
    """Calculate comprehensive statistics for a student"""
    # Get all grades
    grades = Diem.query.filter(
        and_(Diem.MaSV == ma_sv, Diem.TrangThai == True)
    ).all()
    
    if not grades:
        return {
            'ma_sv': ma_sv,
            'error': 'Không có dữ liệu điểm'
        }
    
    # Get semesters
    semesters = sorted(set(g.HocKy for g in grades if g.HocKy))
    
    # Calculate GPA by semester
    gpa_by_semester = {}
    for semester in semesters:
        gpa = calculate_gpa_semester(ma_sv, semester)
        gpa_by_semester[semester] = gpa
    
    # Calculate cumulative GPA
    gpa_cumulative = calculate_gpa_cumulative(ma_sv)
    
    # Calculate average grade
    avg_grade = round(sum(g.DiemTK for g in grades) / len(grades), 2)
    
    # Count failed courses
    failed_courses = [g for g in grades if g.DiemTK < 4.0]
    failed_count = len(failed_courses)
    
    # Academic standing
    standing = get_academic_standing(gpa_cumulative)
    
    return {
        'ma_sv': ma_sv,
        'gpa_by_semester': gpa_by_semester,
        'gpa_cumulative': gpa_cumulative,
        'avg_grade': avg_grade,
        'total_courses': len(grades),
        'failed_courses': failed_courses,
        'failed_count': failed_count,
        'standing': standing,
        'all_grades': grades
    }

# ============================================================
# 4. EXPORT ROUTES
# ============================================================

@admin_diem_bp.route('/export', methods=['POST'])
@login_required
def export_grades():
    """Export grades to Excel"""
    if not check_admin():
        return redirect(url_for('admin.dashboard'))
    
    try:
        # Get filter options
        ma_mon = request.form.get('ma_mon')
        ma_lop = request.form.get('ma_lop')
        hoc_ky = request.form.get('hoc_ky')
        
        # Build query
        query = Diem.query.filter(Diem.TrangThai == True)
        
        if ma_mon:
            query = query.filter(Diem.MaMon == ma_mon)
        if hoc_ky:
            try:
                hoc_ky_int = int(hoc_ky)
                query = query.filter(Diem.HocKy == hoc_ky_int)
            except:
                pass
        
        grades = query.all()
        
        # If filtering by class
        if ma_lop:
            students = SinhVien.query.filter_by(MaLop=ma_lop).all()
            ma_sv_list = [s.MaSV for s in students]
            grades = [g for g in grades if g.MaSV in ma_sv_list]
        
        # Create DataFrame
        data = []
        for g in grades:
            sinh_vien = SinhVien.query.get(g.MaSV)
            mon_hoc = MonHoc.query.get(g.MaMon)
            
            data.append({
                'MSSV': g.MaSV,
                'Họ tên': sinh_vien.HoTen if sinh_vien else '',
                'Lớp': sinh_vien.MaLop if sinh_vien else '',
                'Môn học': mon_hoc.TenMon if mon_hoc else '',
                'Điểm QT': g.DiemQT,
                'Điểm thi': g.DiemThi,
                'Điểm TK': g.DiemTK,
                'Học kỳ': g.HocKy,
                'Năm học': g.NamHoc
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Điểm', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'diem_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    
    except Exception as e:
        flash(f'Lỗi xuất file: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('admin_diem.query_page'))
