from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Numeric, Date, ForeignKey, Enum, DateTime, Boolean, CheckConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, date
import enum
from flask_login import UserMixin
from extensions import db
from sqlalchemy import DateTime
class Base(DeclarativeBase):
    pass


# --- Các tập hợp giá trị (Enum) ---
class LoaiPhuongThuc(enum.Enum):
    DGNL = "Đánh giá năng lực"
    HOCBA_IELTS = "Học bạ kết hợp IELTS"
    THPT = "Điểm thi THPT"
class VaiTro(enum.Enum):
    ADMIN = "admin"
    SINHVIEN = "sinhvien"
    THISINH = "thisinh"

class TrangThaiXT(enum.Enum):
    CHO_DUYET = "Chờ duyệt"
    TRUNG_TUYEN = "Trúng tuyển"
    TU_CHOI = "Từ chối"

class XepLoaiSV(enum.Enum):
    XUAT_SAC = "Xuất sắc"
    GIOI = "Giỏi"
    KHA = "Khá"
    TRUNG_BINH = "Trung bình"
    YEU = "Yếu"
class TrangThaiPhanHoi (enum.Enum):
    CHO_DUYET = "Chờ duyệt"
    DA_DUYET = "Đã hiển thị"
    VI_PHAM = "Vi phạm"
class GioiTinh(enum.Enum):
    NAM = "Nam"
    NU = "Nữ"
# --- 1. Bảng Tài Khoản (Trung tâm) ---
class TaiKhoan(UserMixin, db.Model):
    __tablename__ = "TaiKhoan"
    
    id: Mapped[int] = mapped_column("ID_TaiKhoan",Integer, primary_key=True, autoincrement=True)
    
    # Sửa tên cột ánh xạ để khớp với phpMyAdmin (thường là viết hoa chữ cái đầu)
    ten_dang_nhap: Mapped[str] = mapped_column("TenDangNhap", String(50), unique=True, nullable=False)
    mat_khau: Mapped[str] = mapped_column("MatKhau", String(255), nullable=False)
    vai_tro: Mapped[VaiTro] = mapped_column("VaiTro", Enum(VaiTro,  values_callable=lambda x: [e.value for e in x]), nullable=False)
    trang_thai: Mapped[bool] = mapped_column("TrangThai", Boolean, default=True)

    # Relationships giữ nguyên
    quan_tri = relationship("QuanTri", back_populates="tai_khoan", uselist=False)
    sinh_vien = relationship("SinhVien", back_populates="tai_khoan", uselist=False)
    hso_xettuyen = relationship("HSO_XETTUYEN", back_populates="tai_khoan", uselist=False)
    thong_bao_nhan = relationship("TB_NguoiNhan", back_populates="tai_khoan")
# --- 2. Các bảng Danh mục (Khoa, Ngành, Lớp, Môn học) ---
class Khoa(db.Model):
    __tablename__ = "Khoa"
    MaKhoa: Mapped[str] = mapped_column(String(2), primary_key=True)
    TenKhoa: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    nganhs = relationship("Nganh", back_populates="khoa")

class Nganh(db.Model):
    __tablename__ = "Nganh"
    MaNganh: Mapped[str] = mapped_column(String(4), primary_key=True)
    TenNganh: Mapped[str] = mapped_column(String(100), nullable=False)
    MaKhoa: Mapped[str] = mapped_column(ForeignKey("Khoa.MaKhoa"))
    khoa = relationship("Khoa", back_populates="nganhs")
    ds_to_hop = relationship("ToHopMon", secondary="Nganh_ToHop", backref="ds_nganh")   
class Lop(db.Model):
    __tablename__ = "Lop"
    MaLop: Mapped[str] = mapped_column(String(11), primary_key=True)
    TenLop: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    MaNganh: Mapped[str] = mapped_column(ForeignKey("Nganh.MaNganh"))
    nganh = relationship("Nganh")

class MonHoc(db.Model):
    __tablename__ = "MonHoc"
    MaMon: Mapped[str] = mapped_column(String(7), primary_key=True)
    TenMon: Mapped[str] = mapped_column(String(100), nullable=False)
    SoTinChi: Mapped[int] = mapped_column(Integer, nullable=False)
    HocKy: Mapped[int] = mapped_column(Integer, nullable=True)  # Học kỳ (1, 2, 3...)
    MoTa: Mapped[str] = mapped_column(String(500), nullable=True)  # Mô tả chi tiết
    TrangThai: Mapped[bool] = mapped_column(Boolean, default=True)  # Active/Inactive
    NgayTao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    NgayCapNhat: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    __table_args__ = (CheckConstraint('SoTinChi > 0'),)
    
    # Relationship với ngành (many-to-many)
    nganhs = relationship("Nganh", secondary="Nganh_MonHoc", backref="mon_hocs")

# --- 3. Các bảng Người dùng (QuanTri, SinhVien, HSO_XetTuyen) ---
class QuanTri(db.Model):
    __tablename__ = "QuanTri"
    MaAdmin: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    HoTen: Mapped[str] = mapped_column(String(100))
    ID_TaiKhoan: Mapped[int] = mapped_column(ForeignKey("TaiKhoan.ID_TaiKhoan"), unique=True)
    tai_khoan = relationship("TaiKhoan", back_populates="quan_tri")

class HSO_XETTUYEN(db.Model):
    __tablename__ = "HSO_XETTUYEN"
    MaHSO: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ID_TaiKhoan: Mapped[int] = mapped_column(ForeignKey("TaiKhoan.ID_TaiKhoan"), unique=True)
    HoTen: Mapped[str] = mapped_column(String(100), nullable=False)
    Email: Mapped[str] = mapped_column(String(100), nullable=False)
    NgaySinh: Mapped[date] = mapped_column(Date, nullable=False)
    GioiTinh: Mapped[GioiTinh] = mapped_column( 
        Enum(GioiTinh, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    CCCD: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    SDT: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    tai_khoan = relationship("TaiKhoan", back_populates="hso_xettuyen")

class SinhVien(db.Model):
    __tablename__ = "SinhVien"
    MaSV: Mapped[str] = mapped_column(String(10), primary_key=True)
    HoTen: Mapped[str] = mapped_column(String(100), nullable=False)
    NgaySinh: Mapped[date] = mapped_column(Date, nullable=False)
    Email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    ID_TaiKhoan: Mapped[int] = mapped_column(ForeignKey("TaiKhoan.ID_TaiKhoan"), unique=True)
    MaLop: Mapped[str] = mapped_column(ForeignKey("Lop.MaLop"))
    MaHSO: Mapped[int] = mapped_column(ForeignKey("HSO_XETTUYEN.MaHSO"), nullable=True)
    tai_khoan = relationship("TaiKhoan", back_populates="sinh_vien")
    tot_nghiep = relationship("TotNghiep", backref="sinh_vien", uselist=False)

class ToHopMon(db.Model):
    __tablename__ = "ToHopMon"
    MaToHop: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # VD: A00, A01, D01
    TenToHop: Mapped[str] = mapped_column(String(100), nullable=False) # VD: Toán, Lý, Hóa
    CacMon: Mapped[str] = mapped_column(String(255), nullable=False)
    def __repr__(self):
        return f"<ToHopMon {self.MaToHop}>"
# --- 4. Các bảng Nghiệp vụ (Xét tuyển, Kết quả, Tốt nghiệp) ---
class PT_XetTuyen(db.Model):
    __tablename__ = "PT_XetTuyen"
    MaPTXT: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MaHSO: Mapped[int] = mapped_column(ForeignKey("HSO_XETTUYEN.MaHSO"), nullable=False)
    MaNganh: Mapped[str] = mapped_column(ForeignKey("Nganh.MaNganh"), nullable=False)
    MaToHop: Mapped[int] = mapped_column(ForeignKey("ToHopMon.MaToHop"), nullable=True)
    LoaiPT: Mapped[LoaiPhuongThuc] = mapped_column(
        Enum(LoaiPhuongThuc, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    Diem: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    DiemIELTS: Mapped[float] = mapped_column(Numeric(2, 1), nullable=True)
    FileDGNL: Mapped[str] = mapped_column(String(255), nullable=True)   # Cho phương thức DGNL
    FileHocBa: Mapped[str] = mapped_column(String(255), nullable=True)  # Cho phương thức Học bạ
    FileIELTS: Mapped[str] = mapped_column(String(255), nullable=True)  # Cho phương thức IELTS
    TrangThai: Mapped[TrangThaiXT] = mapped_column(
        Enum(TrangThaiXT, values_callable=lambda x: [e.value for e in x]), 
        default=TrangThaiXT.CHO_DUYET
    )
    MaAdmin: Mapped[int] = mapped_column(ForeignKey("QuanTri.MaAdmin"), nullable=True)
    ho_so = relationship("HSO_XETTUYEN", backref=db.backref("ds_dang_ky", lazy=True))
    nganh = relationship("Nganh")
    to_hop = relationship("ToHopMon")
    chi_tiet_diem = relationship("ChiTietDiemHocBa", back_populates="pt_xettuyen", cascade="all, delete-orphan")

class ChiTietDiemHocBa (db.Model):
    __tablename__ = "ChiTietDiemHocBa"
    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MaPTXT: Mapped[int]=mapped_column(ForeignKey("PT_XetTuyen.MaPTXT"),nullable=False)
    TenMon: Mapped[str] = mapped_column(String(50), nullable=False)
    DiemMon: Mapped[float] = mapped_column(Numeric(4,2), nullable=False)

    pt_xettuyen = relationship("PT_XetTuyen", back_populates="chi_tiet_diem")

class KQ_HocTap(db.Model):
    __tablename__ = "KQ_HocTap"
    MaSV: Mapped[str] = mapped_column(ForeignKey("SinhVien.MaSV"), primary_key=True)
    MaMH: Mapped[str] = mapped_column(ForeignKey("MonHoc.MaMon"), primary_key=True)
    Diem: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)

class TotNghiep(db.Model):
    __tablename__ = "TotNghiep"
    MaSV: Mapped[str] = mapped_column(ForeignKey("SinhVien.MaSV"), primary_key=True)
    GPA: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    XepLoai: Mapped[XepLoaiSV] = mapped_column(Enum(XepLoaiSV,  values_callable=lambda x: [e.value for e in x]), nullable=False)
    __table_args__ = (CheckConstraint('GPA >= 0 AND GPA <= 4.0'),)

# --- 5. Các bảng Thông báo ---
class ThongBao(db.Model):
    __tablename__ = "ThongBao"
    MaTB: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    NoiDung: Mapped[str] = mapped_column(String(255), nullable=False)
    NgayGui: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    MaAdmin: Mapped[int] = mapped_column(ForeignKey("QuanTri.MaAdmin"))

class TB_NguoiNhan(db.Model):
    __tablename__ = "TB_NguoiNhan"
    MaTBNN: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MaTB: Mapped[int] = mapped_column(ForeignKey("ThongBao.MaTB"),nullable=False)
    ID_TaiKhoan: Mapped[int] = mapped_column(ForeignKey("TaiKhoan.ID_TaiKhoan"),nullable=False)
    TrangThaiDoc: Mapped[bool] = mapped_column(Boolean, default=datetime.now())
    ThoiGianDoc: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    tai_khoan = relationship("TaiKhoan", back_populates="thong_bao_nhan")

class ViecLamSinhVien(db.Model):
    __tablename__ = 'ViecLamSinhVien'
    ID = db.Column(db.Integer, primary_key=True)
    MaSV = db.Column(db.String(20), db.ForeignKey('SinhVien.MaSV'), nullable=False)
    TenCongTy = db.Column(db.String(255), nullable=False)
    ChucVu = db.Column(db.String(100))
    DiaChiCongTy = db.Column(db.String(255))
    ThoiGianBatDau = db.Column(db.Date)
    NgayCapNhat = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # Quan hệ
    sinh_vien = db.relationship("SinhVien", backref=db.backref("viec_lam", uselist=False))

class TinNhan(db.Model):
    __tablename__ = "TinNhan"
    MaTinNhan: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ID_NguoiGui: Mapped[int] = mapped_column(ForeignKey("TaiKhoan.ID_TaiKhoan"),nullable=False)
    ID_NguoiNhan: Mapped[int] = mapped_column(ForeignKey("TaiKhoan.ID_TaiKhoan"))
    NoiDung: Mapped[str] = mapped_column(String(100), nullable=False)
    ThoiGianGui: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), default=datetime.now)
    DaDoc: Mapped[bool] = mapped_column(Boolean, default=False)

    sender = relationship("TaiKhoan", foreign_keys=[ID_NguoiGui])
    receiver = relationship("TaiKhoan", foreign_keys=[ID_NguoiNhan])

class ReviewNganh (db.Model):
    __tablename__ = "ReviewNganh"
    MaReview: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MaSV: Mapped[str] = mapped_column(ForeignKey("SinhVien.MaSV"),nullable=False)
    MaNganh: Mapped[str] = mapped_column(ForeignKey("Nganh.MaNganh"), nullable=False)
    NoiDung: Mapped[str] = mapped_column(String(255), nullable=True)
    ThoiGian: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    TrangThai: Mapped[TrangThaiPhanHoi] = mapped_column(
        Enum(TrangThaiPhanHoi, values_callable = lambda x: [e.value for e in x]),
        default=TrangThaiPhanHoi.CHO_DUYET
    )
    MaAdmin: Mapped[int] = mapped_column(ForeignKey("QuanTri.MaAdmin"), nullable=True)

    sinh_vien = relationship("SinhVien", backref=db.backref("reviews", lazy=True))
    nganh = relationship("Nganh", backref=db.backref("ds_reviews", lazy=True))
    admin = relationship("QuanTri", backref=db.backref("ds_review_da_duyet", lazy=True))

# Bảng trung gian nối Ngành và Tổ hợp
class NganhToHop(db.Model):
    __tablename__ = "Nganh_ToHop"
    MaNganh: Mapped[str] = mapped_column(ForeignKey("Nganh.MaNganh"), primary_key=True)
    MaToHop: Mapped[int] = mapped_column(ForeignKey("ToHopMon.MaToHop"), primary_key=True)

# Bảng trung gian nối Ngành và Môn học (Many-to-Many)
# Sử dụng Composite Primary Key (MaNganh, MaMon) thay vì ID
class NganhMonHoc(db.Model):
    __tablename__ = "Nganh_MonHoc"
    MaNganh: Mapped[str] = mapped_column(ForeignKey("Nganh.MaNganh"), primary_key=True, nullable=False)
    MaMon: Mapped[str] = mapped_column(ForeignKey("MonHoc.MaMon"), primary_key=True, nullable=False)
    NgayTao: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Composite Primary Key definition
    __table_args__ = (
        db.PrimaryKeyConstraint('MaNganh', 'MaMon', name='pk_nganh_monhoc'),
    )

# ============================================================
# NÂNG CẤP 2026: BẢNG QUẢN LÝ ĐIỂM HỌC TẬP (DIEM)
# ============================================================
# Bảng này lưu trữ chi tiết điểm số của sinh viên cho mỗi môn học
# theo học kỳ và năm học cụ thể, hỗ trợ nhập/cập nhật qua Excel
# và truy vấn thống kê toàn diện.
# ============================================================

class Diem(db.Model):
    __tablename__ = "Diem"
    
    # Primary key
    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    MaSV: Mapped[str] = mapped_column(ForeignKey("SinhVien.MaSV"), nullable=False)
    MaMon: Mapped[str] = mapped_column(ForeignKey("MonHoc.MaMon"), nullable=False)
    
    # Score components
    DiemQT: Mapped[float] = mapped_column(Numeric(4, 2), nullable=True)  # Process score
    DiemThi: Mapped[float] = mapped_column(Numeric(4, 2), nullable=True)  # Exam score
    DiemTK: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)  # Final score
    
    # Time context
    HocKy: Mapped[int] = mapped_column(Integer, nullable=True)  # Semester (1-8)
    NamHoc: Mapped[int] = mapped_column(Integer, nullable=True)  # Academic year
    
    # Status
    TrangThai: Mapped[bool] = mapped_column(Boolean, default=True)  # Active/Inactive
    NgayCapNhat: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now, 
        onupdate=datetime.now
    )
    
    # Relationships
    sinh_vien = relationship("SinhVien", backref=db.backref("diem_list", lazy=True))
    mon_hoc = relationship("MonHoc", backref=db.backref("diem_list", lazy=True))
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('MaSV', 'MaMon', 'HocKy', 'NamHoc', name='uk_diem_student_course'),
        CheckConstraint('DiemQT IS NULL OR (DiemQT >= 0 AND DiemQT <= 10)'),
        CheckConstraint('DiemThi IS NULL OR (DiemThi >= 0 AND DiemThi <= 10)'),
        CheckConstraint('DiemTK >= 0 AND DiemTK <= 10'),
        CheckConstraint('HocKy IS NULL OR (HocKy >= 1 AND HocKy <= 8)'),
        db.Index('idx_diem_masv', 'MaSV'),
        db.Index('idx_diem_mamon', 'MaMon'),
        db.Index('idx_diem_hocky', 'HocKy'),
        db.Index('idx_diem_namhoc', 'NamHoc'),
        db.Index('idx_diem_trangthaitm', 'TrangThai'),
        db.Index('idx_diem_sv_hocky', 'MaSV', 'HocKy'),
        db.Index('idx_diem_mon_hocky', 'MaMon', 'HocKy'),
    )
    
    def get_xep_loai(self) -> str:
        """Phân loại điểm theo GPA scale"""
        if self.DiemTK >= 9:
            return "A+"
        elif self.DiemTK >= 8.5:
            return "A"
        elif self.DiemTK >= 8:
            return "B+"
        elif self.DiemTK >= 7:
            return "B"
        elif self.DiemTK >= 6:
            return "C"
        elif self.DiemTK >= 5:
            return "D"
        else:
            return "F"
    
    def is_passed(self) -> bool:
        """Kiểm tra có đạt môn không (DiemTK >= 4.0)"""
        return self.DiemTK >= 4.0
    
    def __repr__(self):
        return f"<Diem {self.MaSV} - {self.MaMon}: {self.DiemTK}>"

