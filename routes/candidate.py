from flask import *
from flask_login import *
from extensions import db
from models import *
import uuid
from werkzeug.utils import secure_filename
from models import db, PT_XetTuyen, HSO_XETTUYEN, Nganh, LoaiPhuongThuc
from routes import student
import os

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
        fullname = request.form.get('fullname')
        cccd = request.form.get('cccd')
        sdt = request.form.get('sdt')
        email = request.form.get('email')
        ngay_sinh_str = request.form.get('ngay_sinh')
        gioi_tinh = request.form.get('gioi_tinh')
        ngay_sinh = datetime.strptime(ngay_sinh_str, '%Y-%m-%d').date()
        if not hso:
            hso = HSO_XETTUYEN(
                ID_TaiKhoan=current_user.id,
                HoTen=fullname,
                Email=email,
                SDT=sdt,
                CCCD=cccd,
                NgaySinh=ngay_sinh,
                GioiTinh=GioiTinh[gioi_tinh]
            )
            db.session.add(hso)
        else:
            hso.HoTen = fullname
            hso.Email = email
            hso.SDT = sdt
            hso.CCCD = cccd
            hso.NgaySinh = ngay_sinh
            hso.GioiTinh = GioiTinh[gioi_tinh]

        try:
            db.session.commit()
            flash("Cập nhật hồ sơ thành công!", "success")
            return redirect(url_for('candidate.register_admission')) # Chuyển hướng sang trang đăng ký xét tuyển
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi khi lưu dữ liệu: {str(e)}", "danger")

    return render_template('candidate/update_profile.html', hso=hso)
UPLOAD_PATH = os.path.join('static', 'uploads', 'hoso')

# Kiểm tra nếu thư mục chưa tồn tại thì tạo mới
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)

# Hàm hỗ trợ lưu file
def save_uploaded_file(file, prefix, hso_id):
    if file and file.filename != '':
        filename = secure_filename(f"{prefix}_{hso_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_PATH, filename))
        return filename
    return None
import os
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@candidate_bp.route("/register_admission", methods=["GET", "POST"])
@login_required
def register_admission():
    if request.method == "POST":

        loai = request.form.get("loai_pt")
        ma_nganh = request.form.get("ma_nganh")
        ma_to_hop = request.form.get("ma_to_hop")

        try:
            loai_enum = LoaiPhuongThuc[loai]
        except KeyError:
            flash("Loại phương thức không hợp lệ", "danger")
            return redirect(url_for("candidate.register_admission"))
        if not ma_to_hop or ma_to_hop == "":
             ma_to_hop = None
        pt = PT_XetTuyen(
            MaHSO=current_user.hso_xettuyen.MaHSO,
            MaNganh=ma_nganh,
            MaToHop=ma_to_hop,
            LoaiPT=loai_enum
        )

        # ================= THPT (DYNAMIC) =================
        if loai == "THPT":
            diem_list = [
                float(v) for k, v in request.form.items()
                if k.startswith("diem_") and v.strip() != ""
            ]
            pt.Diem = sum(diem_list)

        # ================= HỌC BẠ + IELTS =================
        elif loai == "HOCBA_IELTS":

            diem_list = [
                float(v) for k, v in request.form.items()
                if k.startswith("diem_") and v.strip() != ""
            ]
            pt.Diem = sum(diem_list)
            pt.DiemIELTS = float(request.form.get("ielts", 0))

            f1 = request.files.get("file_hocba")
            if f1 and f1.filename:
                path = os.path.join("uploads", f1.filename)
                f1.save(path)
                pt.FileHocBa = path

            f2 = request.files.get("file_ielts")
            if f2 and f2.filename:
                path = os.path.join("uploads", f2.filename)
                f2.save(path)
                pt.FileIELTS = path

        # ================= DGNL =================
        elif loai == "DGNL":

            pt.Diem = float(request.form.get("dgnl", 0))

            f = request.files.get("file_dgnl")
            if f and f.filename:
                path = os.path.join("uploads", f.filename)
                f.save(path)
                pt.FileDGNL = path

        db.session.add(pt)
        db.session.commit()

        flash("Đăng ký thành công", "success")
        return redirect(url_for("candidate.register_admission"))

    return render_template(
        "candidate/register_admission.html",
        ds_nganh=Nganh.query.all(),
        ds_tohop=ToHopMon.query.all()
    )
from flask import jsonify

@candidate_bp.route('/get_mon_tohop/<int:id>')
def get_mon_tohop(id):
    # Lấy tổ hợp từ DB
    tohop = ToHopMon.query.get(id)
    
    if tohop and tohop.CacMon:
        # Tách chuỗi "Toán, Lý, Hóa" thành list ["Toán", "Lý", "Hóa"]
        ds_mon = [m.strip() for m in tohop.CacMon.split(',')]
        return jsonify({"mon": ds_mon})
    
    # Nếu không tìm thấy hoặc dữ liệu trống
    return jsonify({"mon": []})
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

@candidate_bp.route('/chat_thisinh', methods=['GET', 'POST'])
@login_required
def chat_thisinh():
    if request.method == 'POST':
        noi_dung = request.form.get('message')
        if noi_dung and noi_dung.strip():
            moi_tin = TinNhan(
                ID_NguoiGui=current_user.id,
                ID_NguoiNhan=None,  
                NoiDung=noi_dung.strip()
            )
            db.session.add(moi_tin)
            
            try:
                db.session.commit()
                print(f"Đã lưu tin nhắn từ ID: {current_user.id}")
            except Exception as e:
                db.session.rollback()
                print("LỖI DATABASE:", e)
                
        return redirect(url_for('candidate.chat_thisinh'))
    messages = TinNhan.query.filter(
        (TinNhan.ID_NguoiGui == current_user.id) | 
        (TinNhan.ID_NguoiNhan == current_user.id)
    ).order_by(TinNhan.ThoiGianGui.asc()).all()

    return render_template('candidate/chat_thisinh.html', messages=messages)