from flask import *
from flask_login import *
from extensions import db
from models import *
import uuid

from routes import student

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route('/dashboard')
@login_required
def dashboard():
    hso = HSO_XETTUYEN.query.filter_by(ID_TaiKhoan=current_user.id).first()
    return render_template('candidate/dashboard.html', hso=hso)

@candidate_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    hso = HSO_XETTUYEN.query.filter_by(ID_TaiKhoan=current_user.id).first()

    if request.method == 'POST':
        hoten = request.form.get('fullname')
        cccd = request.form.get('cccd')
        sdt = request.form.get('sdt')

        if not hso:
            new_hso = HSO_XETTUYEN(
            ID_TaiKhoan = current_user.id,
            HoTen = hoten,
            CCCD = cccd,
            SDT = sdt 
        )
            db.session.add(new_hso)
            flash('Đã tạo hồ sơ thành công')
        else:
            hso.HoTen = hoten
            hso.CCCD = cccd
            hso.SDT = sdt
            flash('Đã cập nhật lại hồ sơ của bạn')

        db.session.commit()
        return redirect(url_for('candidate.dashboard'))
    return render_template('candidate/update_profile.html', hso=hso)

@candidate_bp.route('/regadmission', methods=['GET','POST'])
@login_required
def register_admission():
    hso = HSO_XETTUYEN.query.filter_by(ID_TaiKhoan=current_user.id).first()
    ds_nganh = Nganh.query.all()

    if not hso:
        flash('Vui lòng cập nhật thông tin cá nhân trước khi đăng ký xét tuyển')
        return redirect(url_for('candidate.update_profile'))

    if request.method == 'POST':
        ma_nganh = request.form.get('ma_nganh')
        phuong_thuc = request.form.get('phuong_thuc')
        random_id = str(uuid.uuid4())[:5].upper()
        diem = request.form.get('diem')
        new_admission = PT_XetTuyen(
            MaPTXT = random_id,
            MaNganh = ma_nganh,
            PhuongThuc = phuong_thuc,
            Diem = diem,
            TrangThai = TrangThaiXT.CHO_DUYET,
            MaHSO = hso.MaHSO
        )
        db.session.add(new_admission)
        db.session.commit()
        flash('Đã gửi nguyện vọng xét tuyển thành công')
        return redirect(url_for('candidate.dashboard'))
    return render_template('candidate/register_admission.html', ds_nganh=ds_nganh)

@candidate_bp.route('/result', methods=['GET'])
@login_required
def view_results():
    hso = HSO_XETTUYEN.query.filter_by(ID_TaiKhoan=current_user.id).first()

    if not hso:
        flash('Bạn chưa có hồ sơ trên hệ thống')
        return redirect(url_for('candidate.profile'))
    results = PT_XetTuyen.query.filter_by(MaHSO=hso.MaHSO).all()
    
    return render_template('candidate/results.html', results=results)

@candidate_bp.route('/notifications')
@login_required
def view_notifications():
    notifications = db.session.query(
        ThongBao.MaTB,
        ThongBao.NoiDung,
        ThongBao.NgayGui,
        TB_NguoiNhan.TrangThaiDoc,
        TB_NguoiNhan.ThoiGianDoc,
        QuanTri.HoTen.label("NguoiGui")
    ).join(
        TB_NguoiNhan, ThongBao.MaTB == TB_NguoiNhan.MaTB
    ).outerjoin(
        QuanTri, ThongBao.MaAdmin == QuanTri.MaAdmin
    ).filter(
        TB_NguoiNhan.ID_TaiKhoan == current_user.id
    ).order_by(
        ThongBao.NgayGui.desc()
    ).all()

    from datetime import datetime
    unread_receipts = TB_NguoiNhan.query.filter_by(
        ID_TaiKhoan=current_user.id, 
        TrangThaiDoc=False 
    ).all()
    
    if unread_receipts:
        for r in unread_receipts:
            r.TrangThaiDoc = True
            r.ThoiGianDoc = datetime.now()
        db.session.commit()

    return render_template('candidate/notifications.html', notifications=notifications)