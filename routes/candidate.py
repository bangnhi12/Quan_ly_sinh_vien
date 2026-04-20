from flask import *
from flask_login import *
from extensions import db
from models import *
import uuid
from datetime import datetime

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
        return redirect(url_for('candidate.update_profile'))
    results = PT_XetTuyen.query.filter_by(MaHSO=hso.MaHSO).all()
    
    return render_template('candidate/results.html', results=results)

@candidate_bp.route('/notifications')
@login_required
def view_notifications():
    receipts = TB_NguoiNhan.query.filter_by(ID_TaiKhoan=current_user.id).all()
    notifications = []

    for receipt in receipts:
        content = ThongBao.query.get(receipt.MaTB)
        if not content:
            continue

        sender_name = "Hệ thống"
        if content.MaAdmin:
            sender = QuanTri.query.get(content.MaAdmin)
            if sender and sender.HoTen:
                sender_name = sender.HoTen

        notifications.append({
            'receipt': receipt,
            'content': content,
            'sender_name': sender_name
        })

    notifications.sort(key=lambda x: x['content'].NgayGui, reverse=True)
    return render_template('candidate/notifications.html', notifications=notifications)

@candidate_bp.route('/notifications/<int:receipt_id>')
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
        'candidate/notification_detail.html',
        receipt=receipt,
        notification=notification,
        sender_name=sender_name
    )
