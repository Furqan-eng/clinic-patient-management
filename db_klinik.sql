-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Nov 10, 2025 at 03:17 PM
-- Server version: 8.0.30
-- PHP Version: 8.3.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_klinik`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_pasien`
--

CREATE TABLE `tb_pasien` (
  `id_pasien` int NOT NULL,
  `nama` varchar(100) NOT NULL,
  `umur` int NOT NULL,
  `jenis_kelamin` varchar(10) NOT NULL,
  `keluhan` varchar(255) NOT NULL,
  `dokter` varchar(100) NOT NULL,
  `tanggal_kunjungan` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_pasien`
--

INSERT INTO `tb_pasien` (`id_pasien`, `nama`, `umur`, `jenis_kelamin`, `keluhan`, `dokter`, `tanggal_kunjungan`) VALUES
(1, 'Ahmad Fauzi', 32, 'L', 'Demam Demam tinggi dan batuk', 'dr. Sinta Marlina', '2025-11-10'),
(2, 'Nur Aisyah', 27, 'P', 'Sakit kepala terus-menerus', 'dr. Rian Saputra', '2025-11-09'),
(3, 'Budi Santoso', 40, 'L', 'Nyeri dada ringan', 'dr. Rian Saputra', '2025-11-08'),
(4, 'Siti Zulaikha', 22, 'P', 'Gangguan pencernaan', 'dr. Sinta Marlina', '2025-11-07'),
(6, 'Ahmad Fauzi', 32, 'L', 'Demam tinggi dan batuk', 'dr. Sinta Marlina', '2025-11-10'),
(8, 'Furqan', 12, 'P', 'BAtuk', 'dr. Sinta Marlina', '2025-11-10');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_pasien`
--
ALTER TABLE `tb_pasien`
  ADD PRIMARY KEY (`id_pasien`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_pasien`
--
ALTER TABLE `tb_pasien`
  MODIFY `id_pasien` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
