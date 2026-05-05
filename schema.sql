-- ============================================================
-- SCHEMA QUẢN LÝ SINH VIÊN - PRODUCTION (2026)
-- Database: quan_ly_sinh_vien_1
-- Engine: InnoDB
-- Charset: utf8mb4
-- 
-- This schema is synchronized with Flask-SQLAlchemy models.py
-- All tables, columns, and relationships match the ORM definitions
-- ============================================================

CREATE DATABASE IF NOT EXISTS quan_ly_sinh_vien_1;
USE quan_ly_sinh_vien_1;

-- ============================================================
-- 1. TaiKhoan - Central user account management
-- ============================================================
CREATE TABLE IF NOT EXISTS TaiKhoan (
    ID_TaiKhoan INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Account ID',
    TenDangNhap VARCHAR(50) UNIQUE NOT NULL COMMENT 'Username',
    MatKhau VARCHAR(255) NOT NULL COMMENT 'Password (hashed)',
    VaiTro ENUM('admin','sinhvien','thisinh') NOT NULL COMMENT 'Role: admin, student, or applicant',
    TrangThai BOOLEAN DEFAULT TRUE COMMENT 'Account status (active/inactive)',
    
    INDEX idx_tendangnhap (TenDangNhap)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Central account table for login management';

-- ============================================================
-- 2. Khoa - Faculty/Department
-- ============================================================
CREATE TABLE IF NOT EXISTS Khoa (
    MaKhoa VARCHAR(2) PRIMARY KEY COMMENT 'Faculty code (e.g., CN, KT)',
    TenKhoa VARCHAR(100) UNIQUE NOT NULL COMMENT 'Faculty name (e.g., Khoa Công nghệ thông tin)',
    
    INDEX idx_tenkhoa (TenKhoa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Faculty/Department master data';

-- ============================================================
-- 3. Nganh - Major/Specialization
-- ============================================================
CREATE TABLE IF NOT EXISTS Nganh (
    MaNganh VARCHAR(4) PRIMARY KEY COMMENT 'Major code (e.g., CNPM, HTTT)',
    TenNganh VARCHAR(100) NOT NULL COMMENT 'Major name',
    MaKhoa VARCHAR(2) NOT NULL COMMENT 'Faculty code (foreign key)',
    
    CONSTRAINT FK_Nganh_Khoa FOREIGN KEY (MaKhoa) 
        REFERENCES Khoa(MaKhoa) ON DELETE RESTRICT ON UPDATE CASCADE,
    
    INDEX idx_tennganhh (TenNganh),
    INDEX idx_makhoa (MaKhoa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Major/Specialization under each faculty';

-- ============================================================
-- 4. Lop - Class/Group
-- ============================================================
CREATE TABLE IF NOT EXISTS Lop (
    MaLop VARCHAR(11) PRIMARY KEY COMMENT 'Class code (e.g., CNPM19A1)',
    TenLop VARCHAR(100) UNIQUE NOT NULL COMMENT 'Class name',
    MaNganh VARCHAR(4) NOT NULL COMMENT 'Major code (foreign key)',
    
    CONSTRAINT FK_Lop_Nganh FOREIGN KEY (MaNganh) 
        REFERENCES Nganh(MaNganh) ON DELETE RESTRICT ON UPDATE CASCADE,
    
    INDEX idx_tenlow (TenLop),
    INDEX idx_manganh (MaNganh)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Classes/Groups belonging to majors';

-- 5. MonHoc
CREATE TABLE MonHoc (
    MaMon VARCHAR(7) PRIMARY KEY,
    TenMon VARCHAR(100) NOT NULL,
    SoTinChi INT NOT NULL,
    HocKy INT COMMENT 'Học kỳ (1-8)',
    MoTa VARCHAR(500) COMMENT 'Mô tả chi tiết',
    TrangThai BOOLEAN DEFAULT TRUE COMMENT 'Hoạt động/Vô hiệu',
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Ngày tạo',
    NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Ngày cập nhật',
    CHECK (SoTinChi > 0)
);

-- 6. QuanTri
CREATE TABLE QuanTri (
    MaAdmin INT AUTO_INCREMENT PRIMARY KEY,
    HoTen VARCHAR(100),
    ID_TaiKhoan INT UNIQUE,
    FOREIGN KEY (ID_TaiKhoan) REFERENCES TaiKhoan(ID_TaiKhoan)
);

-- 7. HSO_XETTUYEN
CREATE TABLE HSO_XETTUYEN (
    MaHSO INT AUTO_INCREMENT PRIMARY KEY,
    ID_TaiKhoan INT UNIQUE,
    HoTen VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    NgaySinh DATE NOT NULL,
    GioiTinh ENUM('Nam','Nữ') NOT NULL,
    CCCD VARCHAR(12) UNIQUE NOT NULL,
    SDT VARCHAR(15) UNIQUE NOT NULL,
    FOREIGN KEY (ID_TaiKhoan) REFERENCES TaiKhoan(ID_TaiKhoan)
);

-- 8. SinhVien
CREATE TABLE SinhVien (
    MaSV VARCHAR(10) PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    NgaySinh DATE NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    ID_TaiKhoan INT UNIQUE,
    MaLop VARCHAR(11),
    MaHSO INT,
    FOREIGN KEY (ID_TaiKhoan) REFERENCES TaiKhoan(ID_TaiKhoan),
    FOREIGN KEY (MaLop) REFERENCES Lop(MaLop),
    FOREIGN KEY (MaHSO) REFERENCES HSO_XETTUYEN(MaHSO)
);

-- 9. PT_XetTuyen
CREATE TABLE PT_XetTuyen (
    MaPTXT INT AUTO_INCREMENT PRIMARY KEY,
    MaHSO INT NOT NULL,
    MaNganh VARCHAR(4) NOT NULL,
    LoaiPT ENUM('Đánh giá năng lực','Học bạ kết hợp IELTS','Điểm thi THPT') NOT NULL,
    Diem DECIMAL(4,2) NOT NULL,
    DiemIELTS DECIMAL(2,1),
    FileDGNL VARCHAR(255),
    FileHocBa VARCHAR(255),
    FileIELTS VARCHAR(255),
    TrangThai ENUM('Chờ duyệt','Trúng tuyển','Từ chối') DEFAULT 'Chờ duyệt',
    MaAdmin INT,
    FOREIGN KEY (MaHSO) REFERENCES HSO_XETTUYEN(MaHSO),
    FOREIGN KEY (MaNganh) REFERENCES Nganh(MaNganh),
    FOREIGN KEY (MaAdmin) REFERENCES QuanTri(MaAdmin)
);

-- 10. KQ_HocTap
CREATE TABLE KQ_HocTap (
    MaSV VARCHAR(10),
    MaMH VARCHAR(7),
    Diem DECIMAL(4,2) NOT NULL,
    PRIMARY KEY (MaSV, MaMH),
    FOREIGN KEY (MaSV) REFERENCES SinhVien(MaSV),
    FOREIGN KEY (MaMH) REFERENCES MonHoc(MaMon)
);

-- 11. TotNghiep
CREATE TABLE TotNghiep (
    MaSV VARCHAR(10) PRIMARY KEY,
    GPA DECIMAL(4,2) NOT NULL,
    XepLoai ENUM('Xuất sắc','Giỏi','Khá','Trung bình','Yếu') NOT NULL,
    CHECK (GPA >= 0 AND GPA <= 4.0),
    FOREIGN KEY (MaSV) REFERENCES SinhVien(MaSV)
);

-- 12. ThongBao
CREATE TABLE ThongBao (
    MaTB INT AUTO_INCREMENT PRIMARY KEY,
    NoiDung VARCHAR(255) NOT NULL,
    NgayGui DATETIME DEFAULT CURRENT_TIMESTAMP,
    MaAdmin INT,
    FOREIGN KEY (MaAdmin) REFERENCES QuanTri(MaAdmin)
);

-- 13. TB_NguoiNhan
CREATE TABLE TB_NguoiNhan (
    MaTBNN INT AUTO_INCREMENT PRIMARY KEY,
    MaTB INT NOT NULL,
    ID_TaiKhoan INT NOT NULL,
    TrangThaiDoc BOOLEAN DEFAULT FALSE,
    ThoiGianDoc DATETIME,
    FOREIGN KEY (MaTB) REFERENCES ThongBao(MaTB),
    FOREIGN KEY (ID_TaiKhoan) REFERENCES TaiKhoan(ID_TaiKhoan)
);

-- 14. ViecLamSinhVien
CREATE TABLE ViecLamSinhVien (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    MaSV VARCHAR(10) NOT NULL,
    TenCongTy VARCHAR(255) NOT NULL,
    ChucVu VARCHAR(100),
    DiaChiCongTy VARCHAR(255),
    ThoiGianBatDau DATE,
    NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (MaSV) REFERENCES SinhVien(MaSV)
);

-- 15. TinNhan
CREATE TABLE TinNhan (
    MaTinNhan INT AUTO_INCREMENT PRIMARY KEY,
    ID_NguoiGui INT NOT NULL,
    ID_NguoiNhan INT,
    NoiDung VARCHAR(100) NOT NULL,
    ThoiGianGui DATETIME DEFAULT CURRENT_TIMESTAMP,
    DaDoc BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (ID_NguoiGui) REFERENCES TaiKhoan(ID_TaiKhoan),
    FOREIGN KEY (ID_NguoiNhan) REFERENCES TaiKhoan(ID_TaiKhoan)
);

-- 16. ReviewNganh
CREATE TABLE ReviewNganh (
    MaReview INT AUTO_INCREMENT PRIMARY KEY,
    MaSV VARCHAR(10) NOT NULL,
    MaNganh VARCHAR(4) NOT NULL,
    NoiDung VARCHAR(255),
    ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP,
    TrangThai ENUM('Chờ duyệt','Đã hiển thị','Vi phạm') DEFAULT 'Chờ duyệt',
    MaAdmin INT,
    FOREIGN KEY (MaSV) REFERENCES SinhVien(MaSV),
    FOREIGN KEY (MaNganh) REFERENCES Nganh(MaNganh),
    FOREIGN KEY (MaAdmin) REFERENCES QuanTri(MaAdmin)
);
--17. Tổ hợp môn
CREATE TABLE ToHopMon (
    MaToHop INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    TenToHop VARCHAR(100) NOT NULL, 
    CacMon VARCHAR(255) DEFAULT NULL        
);

-- 1. Thêm cột MaToHop vào bảng PT_XetTuyen
ALTER TABLE PT_XetTuyen 
ADD COLUMN MaToHop INT DEFAULT NULL;

-- 2. Thiết lập ràng buộc khóa ngoại
ALTER TABLE PT_XetTuyen
ADD CONSTRAINT FK_PTXT_ToHop 
FOREIGN KEY (MaToHop) REFERENCES ToHopMon(MaToHop) 
ON DELETE SET NULL ON UPDATE CASCADE;

CREATE TABLE ChiTietDiemHocBa (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    MaPTXT INT NOT NULL,
    TenMon VARCHAR(50) NOT NULL,
    DiemMon DECIMAL(4, 2) NOT NULL,
    CONSTRAINT fk_chi_tiet_ptxt FOREIGN KEY (MaPTXT) 
        REFERENCES PT_XetTuyen(MaPTXT) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Đảm bảo cột Diem có thể nhận giá trị mặc định là 0 trước khi tính toán
ALTER TABLE PT_XetTuyen 
MODIFY COLUMN Diem DECIMAL(4, 2) DEFAULT 0.00;

CREATE TABLE Nganh_ToHop (
    MaNganh VARCHAR(4) NOT NULL,
    MaToHop INT NOT NULL,
    PRIMARY KEY (MaNganh, MaToHop),
    CONSTRAINT FK_Nganh_ToHop_Nganh FOREIGN KEY (MaNganh) 
        REFERENCES Nganh(MaNganh) ON DELETE CASCADE,
    CONSTRAINT FK_Nganh_ToHop_ToHop FOREIGN KEY (MaToHop) 
        REFERENCES ToHopMon(MaToHop) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== NÂNG CẤP BẢNG MonHoc (2026) =====
-- Thêm các cột mới cho MonHoc
ALTER TABLE MonHoc
ADD COLUMN IF NOT EXISTS HocKy INT COMMENT 'Học kỳ (1-8)',
ADD COLUMN IF NOT EXISTS MoTa VARCHAR(500) COMMENT 'Mô tả chi tiết',
ADD COLUMN IF NOT EXISTS TrangThai BOOLEAN DEFAULT TRUE COMMENT 'Hoạt động/Vô hiệu',
ADD COLUMN IF NOT EXISTS NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Ngày tạo',
ADD COLUMN IF NOT EXISTS NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Ngày cập nhật';

-- ===== BẢNG TRUNG GIAN: Nganh_MonHoc (Many-to-Many) =====
CREATE TABLE IF NOT EXISTS Nganh_MonHoc (
    MaNganh VARCHAR(4) NOT NULL COMMENT 'Mã ngành',
    MaMon VARCHAR(7) NOT NULL COMMENT 'Mã môn',
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Ngày gán',
    
    -- Composite Primary Key (MaNganh + MaMon)
    PRIMARY KEY (MaNganh, MaMon),
    
    -- Foreign Keys
    CONSTRAINT FK_NganhMonHoc_Nganh FOREIGN KEY (MaNganh) 
        REFERENCES Nganh(MaNganh) ON DELETE CASCADE,
    CONSTRAINT FK_NganhMonHoc_MonHoc FOREIGN KEY (MaMon) 
        REFERENCES MonHoc(MaMon) ON DELETE CASCADE
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
  COMMENT='Bảng trung gian: Gán Môn Học cho Ngành (Many-to-Many với Composite PK)';

-- ============================================================
-- NÂNG CẤP 2026: BẢNG QUẢN LÝ ĐIỂM HỌC TẬP (DIEM)
-- ============================================================
-- Bảng này lưu trữ chi tiết điểm số của sinh viên cho mỗi môn học
-- theo học kỳ và năm học cụ thể, hỗ trợ nhập/cập nhật qua Excel
-- và truy vấn thống kê toàn diện.
-- ============================================================
CREATE TABLE IF NOT EXISTS Diem (
    ID INT AUTO_INCREMENT PRIMARY KEY,

    MaSV VARCHAR(10) NOT NULL,
    MaMon VARCHAR(7) NOT NULL,

    DiemQT DECIMAL(4,2),
    DiemThi DECIMAL(4,2),
    DiemTK DECIMAL(4,2) NOT NULL,

    HocKy INT,
    NamHoc INT,

    TrangThai BOOLEAN DEFAULT TRUE,
    NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_diem_student_course (MaSV, MaMon, HocKy, NamHoc),

    CONSTRAINT chk_diem_qt CHECK (DiemQT IS NULL OR (DiemQT >= 0 AND DiemQT <= 10)),
    CONSTRAINT chk_diem_thi CHECK (DiemThi IS NULL OR (DiemThi >= 0 AND DiemThi <= 10)),
    CONSTRAINT chk_diem_tk CHECK (DiemTK >= 0 AND DiemTK <= 10),
    CONSTRAINT chk_hocky CHECK (HocKy IS NULL OR (HocKy >= 1 AND HocKy <= 8)),

    CONSTRAINT FK_Diem_SinhVien FOREIGN KEY (MaSV)
        REFERENCES SinhVien(MaSV)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT FK_Diem_MonHoc FOREIGN KEY (MaMon)
        REFERENCES MonHoc(MaMon)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);