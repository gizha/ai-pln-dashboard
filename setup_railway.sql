-- ============================================
-- CREATE TABLE KARYAWAN_PLN
-- ============================================
CREATE TABLE IF NOT EXISTS karyawan_pln (
    id INT AUTO_INCREMENT PRIMARY KEY,
    NIP VARCHAR(20) UNIQUE NOT NULL,
    Nama VARCHAR(100) NOT NULL,
    Jenis_Kelamin CHAR(1),
    Tanggal_Lahir DATE,
    Divisi VARCHAR(50),
    Jabatan VARCHAR(50),
    Tanggal_Masuk DATE,
    Status_Pegawai VARCHAR(20),
    Email VARCHAR(100)
);

-- ============================================
-- INSERT DATA KARYAWAN (SAMPLE)
-- ============================================
INSERT INTO karyawan_pln (NIP, Nama, Jenis_Kelamin, Tanggal_Lahir, Divisi, Jabatan, Tanggal_Masuk, Status_Pegawai, Email) VALUES
('1001', 'Budi Santoso', 'L', '1985-03-15', 'IT', 'Manager', '2015-06-01', 'Tetap', 'budi@pln.id'),
('1002', 'Siti Nurhaliza', 'P', '1990-07-22', 'Finance', 'Supervisor', '2018-01-15', 'Tetap', 'siti@pln.id'),
('1003', 'Ahmad Rizki', 'L', '1988-11-10', 'HR', 'Staff', '2016-03-20', 'Tetap', 'ahmad@pln.id'),
('1004', 'Rina Wijaya', 'P', '1992-05-08', 'IT', 'Developer', '2020-02-10', 'Tetap', 'rina@pln.id'),
('1005', 'Hendra Gunawan', 'L', '1987-09-14', 'Finance', 'Manager', '2017-04-05', 'Tetap', 'hendra@pln.id'),
('1006', 'Nur Azizah', 'P', '1994-02-28', 'Marketing', 'Coordinator', '2019-08-20', 'Tetap', 'nur@pln.id'),
('1007', 'Rudi Setiawan', 'L', '1989-06-12', 'IT', 'Developer', '2018-10-15', 'Tetap', 'rudi@pln.id'),
('1008', 'Putri Lestari', 'P', '1993-04-03', 'HR', 'Manager', '2017-01-10', 'Tetap', 'putri@pln.id'),
('1009', 'Tomi Wijaya', 'L', '1991-09-25', 'Finance', 'Analyst', '2020-03-01', 'Tetap', 'tomi@pln.id'),
('1010', 'Citra Dewi', 'P', '1992-12-17', 'Marketing', 'Manager', '2016-05-20', 'Tetap', 'citra@pln.id');

-- ============================================
-- CREATE TABLE CUSTOMERS (CLASSICMODELS SAMPLE)
-- ============================================
CREATE TABLE IF NOT EXISTS customers (
    customerNumber INT PRIMARY KEY,
    customerName VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    country VARCHAR(50),
    creditLimit DECIMAL(10, 2),
    salesRepEmployeeNumber INT
);

-- ============================================
-- INSERT SAMPLE CUSTOMER DATA
-- ============================================
INSERT INTO customers (customerNumber, customerName, city, country, creditLimit, salesRepEmployeeNumber) VALUES
(101, 'Atelier Graphique', 'Paris', 'France', 21000, 1370),
(112, 'Signal Gift Stores', 'Las Vegas', 'USA', 71800, 1166),
(114, 'Australian Collectors, Co.', 'Melbourne', 'Australia', 117300, 1166),
(119, 'La Rochelle Gifts', 'La Rochelle', 'France', 118400, 1370),
(121, 'Baane Inc.', 'Stavern', 'Norway', 81700, 1504),
(124, 'Mini Creations Ltd.', 'New York', 'USA', 210500, 1286),
(125, 'Havel & Zbyszek Co', 'Warsaw', 'Poland', 0, 1501),
(128, 'Blauer See Auto', 'Berlin', 'Germany', 59300, 1504),
(129, 'Mini Wheels Co.', 'San Francisco', 'USA', 64600, 1286),
(131, 'Land of Toys Inc.', 'NYC', 'USA', 114900, 1323);
