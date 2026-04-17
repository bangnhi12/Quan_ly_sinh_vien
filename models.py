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

class Lop(db.Model):
    __tablename__ = "Lop"
    MaLop: Mapped[str] = mapped_column(String(11), primary_key=True)
    TenLop: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    MaNganh: Mapped[str] = mapped_column(ForeignKey("Nganh.MaNganh"))
    nganh = relationship("Nganh")

class MonHoc(db.Model):
    __tablename__ = "MonHoc"
    MaMH: Mapped[str] = mapped_column(String(7), primary_key=True)
    TenMH: Mapped[str] = mapped_column(String(100), nullable=False)
    SoTinChi: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (CheckConstraint('SoTinChi > 0'),)

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

# --- 4. Các bảng Nghiệp vụ (Xét tuyển, Kết quả, Tốt nghiệp) ---
class PT_XetTuyen(db.Model):
    __tablename__ = "PT_XetTuyen"
    MaPTXT: Mapped[str] = mapped_column(String(5), primary_key=True)
    MaNganh: Mapped[str] = mapped_column(ForeignKey("Nganh.MaNganh"))
    PhuongThuc: Mapped[str] = mapped_column(String(100), nullable=False)
    Diem: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    TrangThai: Mapped[TrangThaiXT] = mapped_column(Enum(TrangThaiXT,  values_callable=lambda x: [e.value for e in x]), default=TrangThaiXT.CHO_DUYET)
    MaHSO: Mapped[int] = mapped_column(ForeignKey("HSO_XETTUYEN.MaHSO"))
    MaAdmin: Mapped[int] = mapped_column(ForeignKey("QuanTri.MaAdmin"), nullable=True)

class KQ_HocTap(db.Model):
    __tablename__ = "KQ_HocTap"
    MaSV: Mapped[str] = mapped_column(ForeignKey("SinhVien.MaSV"), primary_key=True)
    MaMH: Mapped[str] = mapped_column(ForeignKey("MonHoc.MaMH"), primary_key=True)
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
