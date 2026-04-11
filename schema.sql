-- 1. Bảng Khoa
CREATE TABLE Khoa (
    MaKhoa VARCHAR(2) PRIMARY KEY,
    TenKhoa VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Bảng Ngành
CREATE TABLE Nganh (
    MaNganh VARCHAR(4) PRIMARY KEY,
    TenNganh VARCHAR(100) NOT NULL,
    MaKhoa VARCHAR(2),
    FOREIGN KEY(MaKhoa) REFERENCES Khoa(MaKhoa)
);

-- 3. Bảng Lớp
CREATE TABLE Lop (
    MaLop VARCHAR(11) PRIMARY KEY,
    TenLop VARCHAR(100) NOT NULL UNIQUE,
    MaNganh VARCHAR(4),
    FOREIGN KEY(MaNganh) REFERENCES Nganh(MaNganh)
);

-- 4. Bảng Tài Khoản (Bảng trung tâm để Đăng nhập)
CREATE TABLE TaiKhoan (
    ID_TaiKhoan INT PRIMARY KEY AUTO_INCREMENT,
    TenDangNhap VARCHAR(50) NOT NULL UNIQUE,
    MatKhau VARCHAR(255) NOT NULL,
    VaiTro ENUM('admin', 'sinhvien', 'thisinh') NOT NULL,
    TrangThai TINYINT(1) DEFAULT 1 -- 1: Hoạt động, 0: Khóa
);

-- 5. Bảng Quản Trị
CREATE TABLE QuanTri (
    MaAdmin INT(2) PRIMARY KEY AUTO_INCREMENT,
    HoTen VARCHAR(100) NOT NULL,
    ID_TaiKhoan INT UNIQUE,
    FOREIGN KEY(ID_TaiKhoan) REFERENCES TaiKhoan(ID_TaiKhoan)
);

-- 6. Bảng Hồ Sơ Xét Tuyển (Thí sinh)
CREATE TABLE HSO_XETTUYEN (
    MaHSO INT(4) PRIMARY KEY AUTO_INCREMENT,
    ID_TaiKhoan INT UNIQUE,
    HoTen VARCHAR(100) NOT NULL,
    CCCD VARCHAR(12) NOT NULL UNIQUE,
    SDT VARCHAR(15) NOT NULL UNIQUE,
    FOREIGN KEY(ID_TaiKhoan) REFERENCES TaiKhoan(ID_TaiKhoan)
);

-- 7. Bảng Sinh Viên
CREATE TABLE SinhVien (
    MaSV VARCHAR(10) PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    NgaySinh DATE NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    ID_TaiKhoan INT UNIQUE,
    MaLop VARCHAR(11),
    MaHSO INT(4), 
    FOREIGN KEY (ID_TaiKhoan) REFERENCES TaiKhoan(ID_TaiKhoan),
    FOREIGN KEY (MaLop) REFERENCES Lop(MaLop),
    FOREIGN KEY (MaHSO) REFERENCES HSO_XETTUYEN(MaHSO)
);

-- 8. Bảng Môn Học
CREATE TABLE MonHoc (
    MaMH VARCHAR(7) PRIMARY KEY,
    TenMH VARCHAR(100) NOT NULL,
    SoTinChi INT(1) NOT NULL CHECK (SoTinChi > 0)
);

-- 9. Bảng Phương Thức Xét Tuyển
CREATE TABLE PT_XetTuyen(
    MaPTXT VARCHAR(5) PRIMARY KEY,
    MaNganh VARCHAR(4),
    PhuongThuc VARCHAR(100) NOT NULL,
    Diem DECIMAL(4,2) NOT NULL,
    TrangThai ENUM('Chờ duyệt', 'Trúng tuyển', 'Từ chối') DEFAULT 'Chờ duyệt',
    MaHSO INT(4),
    MaAdmin INT(2),
    FOREIGN KEY(MaAdmin) REFERENCES QuanTri(MaAdmin),
    FOREIGN KEY(MaHSO) REFERENCES HSO_XETTUYEN(MaHSO),
    FOREIGN KEY(MaNganh) REFERENCES Nganh(MaNganh)
);

-- 10. Bảng Kết Quả Học Tập
CREATE TABLE KQ_HocTap(
    MaSV VARCHAR(10),
    MaMH VARCHAR(7),
    Diem DECIMAL(4,2) NOT NULL,
    PRIMARY KEY(MaSV, MaMH),
    FOREIGN KEY(MaSV) REFERENCES SinhVien(MaSV),
    FOREIGN KEY(MaMH) REFERENCES MonHoc(MaMH)
);

-- 11. Bảng Tốt Nghiệp
CREATE TABLE TotNghiep (
    MaSV VARCHAR(10) PRIMARY KEY,
    GPA DECIMAL(4,2) NOT NULL CHECK (GPA >= 0 AND GPA <= 4.0),
    XepLoai ENUM('Xuất sắc', 'Giỏi', 'Khá', 'Trung bình', 'Yếu') NOT NULL,
    FOREIGN KEY(MaSV) REFERENCES SinhVien(MaSV)
);

-- 12. Bảng Thông Báo
CREATE TABLE ThongBao (
    MaTB INT(5) PRIMARY KEY AUTO_INCREMENT,
    NoiDung VARCHAR(255) NOT NULL,
    NgayGui DATETIME DEFAULT CURRENT_TIMESTAMP,
    MaAdmin INT(2),
    FOREIGN KEY(MaAdmin) REFERENCES QuanTri(MaAdmin)
);

-- 13. Bảng Thông Báo Người Nhận
CREATE TABLE TB_NguoiNhan (
    MaTBNN INT PRIMARY KEY AUTO_INCREMENT,
    MaTB INT(5),
    ID_TaiKhoan INT, -- Gửi theo tài khoản sẽ linh hoạt hơn gửi theo MaSV
    TrangThaiDoc TINYINT(1) DEFAULT 0,
    ThoiGianDoc DATETIME,
    FOREIGN KEY(MaTB) REFERENCES ThongBao(MaTB),
    FOREIGN KEY(ID_TaiKhoan) REFERENCES TaiKhoan(ID_TaiKhoan)
);