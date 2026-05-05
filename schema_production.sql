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

-- ============================================================
-- 5. MonHoc - Course/Subject (UPDATED 2026)
-- ============================================================
CREATE TABLE IF NOT EXISTS MonHoc (
    MaMon VARCHAR(7) PRIMARY KEY COMMENT 'Course code (e.g., CS101, MATH201)',
    TenMon VARCHAR(100) NOT NULL COMMENT 'Course name',
    SoTinChi INT NOT NULL COMMENT 'Credit hours',
    HocKy INT COMMENT 'Semester (1-8, null if not assigned)',
    MoTa VARCHAR(500) COMMENT 'Course description',
    TrangThai BOOLEAN DEFAULT TRUE COMMENT 'Status (active/inactive)',
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Created date',
    NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated date',
    
    CONSTRAINT chk_sotinchi CHECK (SoTinChi > 0),
    CONSTRAINT chk_hocky CHECK (HocKy IS NULL OR (HocKy >= 1 AND HocKy <= 8)),
    
    INDEX idx_tenmon (TenMon),
    INDEX idx_trangthaitm (TrangThai),
    INDEX idx_hocky (HocKy)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Courses/Subjects - Enhanced 2026 with semester, description, status';

-- ============================================================
-- 6. ToHopMon - Subject Combination for Admission
-- ============================================================
CREATE TABLE IF NOT EXISTS ToHopMon (
    MaToHop INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Subject combination code',
    TenToHop VARCHAR(100) NOT NULL COMMENT 'Subject combination name (e.g., A00, D01)',
    CacMon VARCHAR(255) COMMENT 'List of subjects in combination',
    
    INDEX idx_tentohopm (TenToHop)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Subject combinations for admission exam';

-- ============================================================
-- 7. Nganh_ToHop - Many-to-Many: Major-SubjectCombination
-- ============================================================
CREATE TABLE IF NOT EXISTS Nganh_ToHop (
    MaNganh VARCHAR(4) NOT NULL COMMENT 'Major code',
    MaToHop INT NOT NULL COMMENT 'Subject combination code',
    
    PRIMARY KEY (MaNganh, MaToHop),
    
    CONSTRAINT FK_NganhToHop_Nganh FOREIGN KEY (MaNganh) 
        REFERENCES Nganh(MaNganh) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_NganhToHop_ToHop FOREIGN KEY (MaToHop) 
        REFERENCES ToHopMon(MaToHop) ON DELETE CASCADE ON UPDATE CASCADE,
    
    INDEX idx_matohopm (MaToHop)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Junction table: Links majors to subject combinations';

-- ============================================================
-- 8. Nganh_MonHoc - Many-to-Many: Major-Course (PRODUCTION 2026)
-- ============================================================
-- CRITICAL: Uses COMPOSITE PRIMARY KEY (MaNganh, MaMon) instead of separate ID
-- This ensures uniqueness at combination level and prevents duplicates
CREATE TABLE IF NOT EXISTS Nganh_MonHoc (
    MaNganh VARCHAR(4) NOT NULL COMMENT 'Major code',
    MaMon VARCHAR(7) NOT NULL COMMENT 'Course code',
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Assignment date',
    
    PRIMARY KEY (MaNganh, MaMon),
    
    CONSTRAINT FK_NganhMonHoc_Nganh FOREIGN KEY (MaNganh) 
        REFERENCES Nganh(MaNganh) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_NganhMonHoc_MonHoc FOREIGN KEY (MaMon) 
        REFERENCES MonHoc(MaMon) ON DELETE CASCADE ON UPDATE CASCADE,
    
    INDEX idx_nganh (MaNganh),
    INDEX idx_monhoc (MaMon)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Junction table (Many-to-Many): Courses assigned to majors - COMPOSITE PK';

-- ============================================================
-- 9. QuanTri - Administrator
-- ============================================================
CREATE TABLE IF NOT EXISTS QuanTri (
    MaAdmin INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Admin ID',
    HoTen VARCHAR(100) COMMENT 'Admin name',
    ID_TaiKhoan INT UNIQUE NOT NULL COMMENT 'Link to TaiKhoan',
    
    CONSTRAINT FK_QuanTri_TaiKhoan FOREIGN KEY (ID_TaiKhoan) 
        REFERENCES TaiKhoan(ID_TaiKhoan) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Administrator account details';

-- ============================================================
-- 10. HSO_XETTUYEN - Applicant Profile
-- ============================================================
CREATE TABLE IF NOT EXISTS HSO_XETTUYEN (
    MaHSO INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Applicant ID',
    ID_TaiKhoan INT UNIQUE NOT NULL COMMENT 'Link to TaiKhoan',
    HoTen VARCHAR(100) NOT NULL COMMENT 'Applicant name',
    Email VARCHAR(100) NOT NULL COMMENT 'Email address',
    NgaySinh DATE NOT NULL COMMENT 'Date of birth',
    GioiTinh ENUM('Nam','Nữ') NOT NULL COMMENT 'Gender',
    CCCD VARCHAR(12) UNIQUE NOT NULL COMMENT 'National ID',
    SDT VARCHAR(15) UNIQUE NOT NULL COMMENT 'Phone number',
    
    CONSTRAINT FK_HSO_TaiKhoan FOREIGN KEY (ID_TaiKhoan) 
        REFERENCES TaiKhoan(ID_TaiKhoan) ON DELETE CASCADE ON UPDATE CASCADE,
    
    INDEX idx_email (Email),
    INDEX idx_cccd (CCCD)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Applicant profiles for admission examination';

-- ============================================================
-- 11. SinhVien - Student
-- ============================================================
CREATE TABLE IF NOT EXISTS SinhVien (
    MaSV VARCHAR(10) PRIMARY KEY COMMENT 'Student ID',
    HoTen VARCHAR(100) NOT NULL COMMENT 'Student name',
    NgaySinh DATE NOT NULL COMMENT 'Date of birth',
    Email VARCHAR(100) UNIQUE NOT NULL COMMENT 'Student email',
    ID_TaiKhoan INT UNIQUE NOT NULL COMMENT 'Link to TaiKhoan',
    MaLop VARCHAR(11) NOT NULL COMMENT 'Class code',
    MaHSO INT COMMENT 'Applicant ID (if admitted)',
    
    CONSTRAINT FK_SinhVien_TaiKhoan FOREIGN KEY (ID_TaiKhoan) 
        REFERENCES TaiKhoan(ID_TaiKhoan) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_SinhVien_Lop FOREIGN KEY (MaLop) 
        REFERENCES Lop(MaLop) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT FK_SinhVien_HSO FOREIGN KEY (MaHSO) 
        REFERENCES HSO_XETTUYEN(MaHSO) ON DELETE SET NULL ON UPDATE CASCADE,
    
    INDEX idx_email_sv (Email),
    INDEX idx_malop_sv (MaLop)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Student records';

-- ============================================================
-- 12. KQ_HocTap - Student Learning Results
-- ============================================================
CREATE TABLE IF NOT EXISTS KQ_HocTap (
    MaSV VARCHAR(10) NOT NULL COMMENT 'Student ID',
    MaMH VARCHAR(7) NOT NULL COMMENT 'Course code',
    Diem DECIMAL(4, 2) NOT NULL COMMENT 'Grade/Score',
    
    PRIMARY KEY (MaSV, MaMH),
    
    CONSTRAINT FK_KQHocTap_SinhVien FOREIGN KEY (MaSV) 
        REFERENCES SinhVien(MaSV) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_KQHocTap_MonHoc FOREIGN KEY (MaMH) 
        REFERENCES MonHoc(MaMon) ON DELETE CASCADE ON UPDATE CASCADE,
    
    INDEX idx_mamon_kq (MaMH)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Student academic results per course';

-- ============================================================
-- 13. TotNghiep - Graduation Records
-- ============================================================
CREATE TABLE IF NOT EXISTS TotNghiep (
    MaSV VARCHAR(10) PRIMARY KEY COMMENT 'Student ID',
    GPA DECIMAL(4, 2) NOT NULL COMMENT 'GPA (0.0 - 4.0)',
    XepLoai ENUM('Xuất sắc','Giỏi','Khá','Trung bình','Yếu') NOT NULL COMMENT 'Graduation classification',
    
    CONSTRAINT chk_gpa CHECK (GPA >= 0 AND GPA <= 4.0),
    CONSTRAINT FK_TotNghiep_SinhVien FOREIGN KEY (MaSV) 
        REFERENCES SinhVien(MaSV) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Graduation information and GPA';

-- ============================================================
-- 14. PT_XetTuyen - Admission Application
-- ============================================================
CREATE TABLE IF NOT EXISTS PT_XetTuyen (
    MaPTXT INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Application ID',
    MaHSO INT NOT NULL COMMENT 'Applicant ID',
    MaNganh VARCHAR(4) NOT NULL COMMENT 'Applied major',
    MaToHop INT COMMENT 'Subject combination',
    LoaiPT ENUM('Đánh giá năng lực','Học bạ kết hợp IELTS','Điểm thi THPT') NOT NULL COMMENT 'Admission method',
    Diem DECIMAL(4, 2) DEFAULT 0.00 COMMENT 'Score/Grade',
    DiemIELTS DECIMAL(2, 1) COMMENT 'IELTS score',
    FileDGNL VARCHAR(255) COMMENT 'Capacity assessment file',
    FileHocBa VARCHAR(255) COMMENT 'Academic transcript file',
    FileIELTS VARCHAR(255) COMMENT 'IELTS certificate file',
    TrangThai ENUM('Chờ duyệt','Trúng tuyển','Từ chối') DEFAULT 'Chờ duyệt' COMMENT 'Application status',
    MaAdmin INT COMMENT 'Admin reviewer',
    
    CONSTRAINT FK_PTXT_HSO FOREIGN KEY (MaHSO) 
        REFERENCES HSO_XETTUYEN(MaHSO) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_PTXT_Nganh FOREIGN KEY (MaNganh) 
        REFERENCES Nganh(MaNganh) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT FK_PTXT_ToHop FOREIGN KEY (MaToHop) 
        REFERENCES ToHopMon(MaToHop) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT FK_PTXT_Admin FOREIGN KEY (MaAdmin) 
        REFERENCES QuanTri(MaAdmin) ON DELETE SET NULL ON UPDATE CASCADE,
    
    INDEX idx_mahso_ptxt (MaHSO),
    INDEX idx_manganh_ptxt (MaNganh),
    INDEX idx_trangthai_ptxt (TrangThai)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Admission applications from applicants';

-- ============================================================
-- 15. ChiTietDiemHocBa - Score Details from Academic Transcript
-- ============================================================
CREATE TABLE IF NOT EXISTS ChiTietDiemHocBa (
    ID INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Detail ID',
    MaPTXT INT NOT NULL COMMENT 'Application ID',
    TenMon VARCHAR(50) NOT NULL COMMENT 'Course name',
    DiemMon DECIMAL(4, 2) NOT NULL COMMENT 'Course score',
    
    CONSTRAINT FK_ChiTietDiem_PTXT FOREIGN KEY (MaPTXT) 
        REFERENCES PT_XetTuyen(MaPTXT) ON DELETE CASCADE ON UPDATE CASCADE,
    
    INDEX idx_maptxt_chitiet (MaPTXT)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Score details extracted from academic transcripts';

-- ============================================================
-- 16. ThongBao - Notifications/Announcements
-- ============================================================
CREATE TABLE IF NOT EXISTS ThongBao (
    MaTB INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Announcement ID',
    NoiDung VARCHAR(255) NOT NULL COMMENT 'Announcement content',
    NgayGui DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Send date',
    MaAdmin INT COMMENT 'Admin who created it',
    
    CONSTRAINT FK_TB_Admin FOREIGN KEY (MaAdmin) 
        REFERENCES QuanTri(MaAdmin) ON DELETE SET NULL ON UPDATE CASCADE,
    
    INDEX idx_ngayguii (NgayGui)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Announcements from administrators';

-- ============================================================
-- 17. TB_NguoiNhan - Notification Recipients
-- ============================================================
CREATE TABLE IF NOT EXISTS TB_NguoiNhan (
    MaTBNN INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Receipt ID',
    MaTB INT NOT NULL COMMENT 'Announcement ID',
    ID_TaiKhoan INT NOT NULL COMMENT 'Recipient account',
    TrangThaiDoc BOOLEAN DEFAULT FALSE COMMENT 'Read status',
    ThoiGianDoc DATETIME COMMENT 'Read time',
    
    CONSTRAINT FK_TBNN_TB FOREIGN KEY (MaTB) 
        REFERENCES ThongBao(MaTB) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_TBNN_TaiKhoan FOREIGN KEY (ID_TaiKhoan) 
        REFERENCES TaiKhoan(ID_TaiKhoan) ON DELETE CASCADE ON UPDATE CASCADE,
    
    INDEX idx_matb_nn (MaTB),
    INDEX idx_id_tk_nn (ID_TaiKhoan),
    INDEX idx_trangthaodoc (TrangThaiDoc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Tracks notification delivery to users';

-- ============================================================
-- 18. ViecLamSinhVien - Student Employment Record
-- ============================================================
CREATE TABLE IF NOT EXISTS ViecLamSinhVien (
    ID INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Record ID',
    MaSV VARCHAR(10) NOT NULL COMMENT 'Student ID',
    TenCongTy VARCHAR(255) NOT NULL COMMENT 'Company name',
    ChucVu VARCHAR(100) COMMENT 'Position',
    DiaChiCongTy VARCHAR(255) COMMENT 'Company address',
    ThoiGianBatDau DATE COMMENT 'Start date',
    NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last updated',
    
    CONSTRAINT FK_ViecLam_SinhVien FOREIGN KEY (MaSV) 
        REFERENCES SinhVien(MaSV) ON DELETE CASCADE ON UPDATE CASCADE,
    
    INDEX idx_masv_vl (MaSV),
    INDEX idx_tencongty (TenCongTy)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Employment records for students';

-- ============================================================
-- 19. TinNhan - Messages between Users
-- ============================================================
CREATE TABLE IF NOT EXISTS TinNhan (
    MaTinNhan INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Message ID',
    ID_NguoiGui INT NOT NULL COMMENT 'Sender account',
    ID_NguoiNhan INT COMMENT 'Recipient account',
    NoiDung VARCHAR(100) NOT NULL COMMENT 'Message content',
    ThoiGianGui DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Send time',
    DaDoc BOOLEAN DEFAULT FALSE COMMENT 'Read status',
    
    CONSTRAINT FK_TN_Gui FOREIGN KEY (ID_NguoiGui) 
        REFERENCES TaiKhoan(ID_TaiKhoan) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_TN_Nhan FOREIGN KEY (ID_NguoiNhan) 
        REFERENCES TaiKhoan(ID_TaiKhoan) ON DELETE CASCADE ON UPDATE CASCADE,
    
    INDEX idx_id_gui (ID_NguoiGui),
    INDEX idx_id_nhan (ID_NguoiNhan),
    INDEX idx_da_doc (DaDoc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='User-to-user messaging system';

-- ============================================================
-- 20. ReviewNganh - Student Major Reviews/Feedback
-- ============================================================
CREATE TABLE IF NOT EXISTS ReviewNganh (
    MaReview INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Review ID',
    MaSV VARCHAR(10) NOT NULL COMMENT 'Student ID',
    MaNganh VARCHAR(4) NOT NULL COMMENT 'Major ID',
    NoiDung VARCHAR(255) COMMENT 'Review content/feedback',
    ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Review time',
    TrangThai ENUM('Chờ duyệt','Đã hiển thị','Vi phạm') DEFAULT 'Chờ duyệt' COMMENT 'Moderation status',
    MaAdmin INT COMMENT 'Admin moderator',
    
    CONSTRAINT FK_Review_SinhVien FOREIGN KEY (MaSV) 
        REFERENCES SinhVien(MaSV) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_Review_Nganh FOREIGN KEY (MaNganh) 
        REFERENCES Nganh(MaNganh) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_Review_Admin FOREIGN KEY (MaAdmin) 
        REFERENCES QuanTri(MaAdmin) ON DELETE SET NULL ON UPDATE CASCADE,
    
    INDEX idx_masv_review (MaSV),
    INDEX idx_manganh_review (MaNganh),
    INDEX idx_trangthai_review (TrangThai)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Major reviews/feedback from students (moderated)';

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
-- Run these after import to verify schema integrity:
/*
-- 1. Check all tables exist
SELECT COUNT(*) as total_tables FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'quan_ly_sinh_vien_1';

-- 2. Verify composite key on Nganh_MonHoc
DESC quan_ly_sinh_vien_1.Nganh_MonHoc;

-- 3. Check all foreign keys
SELECT CONSTRAINT_NAME, TABLE_NAME, REFERENCED_TABLE_NAME 
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'quan_ly_sinh_vien_1' 
  AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME;

-- 4. Test insert on junction table
-- INSERT INTO Nganh_MonHoc (MaNganh, MaMon) VALUES ('CNPM', 'CS101');
-- SELECT * FROM Nganh_MonHoc;
*/

-- ============================================================
-- NOTES FOR DEVELOPERS
-- ============================================================
/*
CRITICAL CHANGES IN 2026:

1. Nganh_MonHoc (Junction Table):
   - Uses COMPOSITE PRIMARY KEY (MaNganh, MaMon)
   - NO separate ID field (was causing Unknown column errors)
   - Prevents duplicate assignments of same course to same major
   - When updating code: Use and_(MaNganh==x, MaMon==y) in SQLAlchemy joins

2. MonHoc (Course Table):
   - Added HocKy (Semester): 1-8, or NULL if not assigned
   - Added MoTa (Description): Nullable, up to 500 chars
   - Added TrangThai (Status): Boolean, default True (active)
   - Added NgayTao, NgayCapNhat: Automatic timestamps

3. Foreign Key Constraints:
   - ON DELETE CASCADE: Cascades deletes (used for detail records)
   - ON DELETE RESTRICT: Prevents delete if child records exist (used for master data)
   - ON DELETE SET NULL: Sets FK to NULL on parent delete (used for optional references)

4. Indexes:
   - Added on all foreign keys for query performance
   - Added on commonly searched columns (TenMon, Email, etc.)
   - Added on status/type columns (TrangThai, etc.)

5. Engine & Charset:
   - InnoDB: Transaction support, referential integrity
   - utf8mb4: Full Unicode support for Vietnamese characters

DATABASE DEPLOYMENT:
  mysql -u root -p < schema_production.sql

ROLLBACK (if needed):
  DROP DATABASE quan_ly_sinh_vien_1;
  
VERIFY:
  USE quan_ly_sinh_vien_1;
  SHOW TABLES;
  SHOW FULL PROCESSLIST;
*/
