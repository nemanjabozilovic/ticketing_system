-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3308
-- Generation Time: Sep 27, 2020 at 08:22 PM
-- Server version: 8.0.18
-- PHP Version: 7.3.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ticketing_system`
--

DELIMITER $$
--
-- Functions
--
DROP FUNCTION IF EXISTS `imePodnosioca`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `imePodnosioca` (`id_korisnik` INT(11)) RETURNS VARCHAR(200) CHARSET utf8 BEGIN
	DECLARE naziv varchar(200);
		SELECT ime INTO naziv FROM korisnici WHERE id_korisnika = id_korisnik;
	RETURN naziv;
END$$

DROP FUNCTION IF EXISTS `izKompanije`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `izKompanije` (`id_komp` INT(11)) RETURNS VARCHAR(200) CHARSET utf8 BEGIN
	DECLARE naziv varchar(200);
    	SELECT naziv_kompanije INTO naziv FROM kompanije WHERE id_kompanije = id_komp;
        RETURN naziv;
END$$

DROP FUNCTION IF EXISTS `nazivKompanije`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `nazivKompanije` (`id_komp` INT(11)) RETURNS VARCHAR(200) CHARSET utf8 BEGIN
	DECLARE naziv varchar(200);
		SELECT naziv_kompanije INTO naziv FROM kompanije WHERE id_kompanije=id_komp;
	RETURN naziv;
END$$

DROP FUNCTION IF EXISTS `nazivRole`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `nazivRole` (`id_rol` INT(11)) RETURNS VARCHAR(200) CHARSET utf8 BEGIN
	DECLARE naziv varchar(200);
		SELECT naziv_role INTO naziv FROM role WHERE id_role=id_rol;
	RETURN naziv;
END$$

DROP FUNCTION IF EXISTS `nazivStatusa`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `nazivStatusa` (`id_stat` INT(11)) RETURNS VARCHAR(200) CHARSET utf8 BEGIN
	DECLARE naziv varchar(200);
		SELECT tip_statusa INTO naziv FROM status WHERE id_status=id_stat;
	RETURN naziv;
END$$

DROP FUNCTION IF EXISTS `nazivTipa`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `nazivTipa` (`id_tipa_zaht` INT(11)) RETURNS VARCHAR(200) CHARSET utf8 BEGIN
	DECLARE naziv varchar(200);
		SELECT skracena_oznaka INTO naziv FROM tip_zahteva WHERE id_tipa_zahteva = id_tipa_zaht;
	RETURN naziv;
END$$

DROP FUNCTION IF EXISTS `prezimePodnosioca`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `prezimePodnosioca` (`id_korisnik` INT(11)) RETURNS VARCHAR(200) CHARSET utf8 BEGIN
	DECLARE naziv varchar(200);
		SELECT prezime INTO naziv FROM korisnici WHERE id_korisnika = id_korisnik;
	RETURN naziv;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `kompanije`
--

DROP TABLE IF EXISTS `kompanije`;
CREATE TABLE IF NOT EXISTS `kompanije` (
  `id_kompanije` int(11) NOT NULL AUTO_INCREMENT,
  `naziv_kompanije` varchar(100) NOT NULL,
  `adresa` varchar(200) NOT NULL,
  `broj_telefona` varchar(100) NOT NULL,
  PRIMARY KEY (`id_kompanije`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `kompanije`
--

INSERT INTO `kompanije` (`id_kompanije`, `naziv_kompanije`, `adresa`, `broj_telefona`) VALUES
(3, 'VTŠ Apps Team', 'Aleksandra Medvedeva 20', '+381 18 588 211'),
(5, 'ATVSS Niš', 'Aleksandra Medvedeva 20', '+381 18 588 211');

-- --------------------------------------------------------

--
-- Table structure for table `korisnici`
--

DROP TABLE IF EXISTS `korisnici`;
CREATE TABLE IF NOT EXISTS `korisnici` (
  `id_korisnika` int(11) NOT NULL AUTO_INCREMENT,
  `ime` varchar(100) NOT NULL,
  `prezime` varchar(100) NOT NULL,
  `kompanija` int(11) NOT NULL,
  `rola` int(11) NOT NULL,
  `email` varchar(100) NOT NULL,
  `token` varchar(255) NOT NULL DEFAULT 'none',
  `korisnicko_ime` varchar(100) NOT NULL,
  `lozinka` varchar(100) NOT NULL,
  PRIMARY KEY (`id_korisnika`),
  KEY `fk_kompanije` (`kompanija`),
  KEY `fk_rola` (`rola`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `korisnici`
--

INSERT INTO `korisnici` (`id_korisnika`, `ime`, `prezime`, `kompanija`, `rola`, `email`, `token`, `korisnicko_ime`, `lozinka`) VALUES
(20, 'Slavimir', 'Stošović', 3, 1, 'slavimir.stosovic@vtsappsteam.rs', 'none', 'slavimir.stosovic', 'pbkdf2:sha256:150000$OEhjnivj$4fd3033d6c4164e023a1a10dbf97b9d49c7a44cbd930ebc79ff04ef77f9164fc'),
(21, 'Nemanja', 'Božilović', 3, 2, 'bozilovic1998@gmail.com', '97d16787-1aaf-40a4-b505-f47661bb3289', 'nemanja.bozilovic', 'pbkdf2:sha256:150000$LuQAAStY$dee6a2ea63fe7751e30bc8fc2a1f74ffc5c4264f2a252ff6c56241e71bd91038'),
(22, 'Goran', 'Milosavljević', 5, 3, 'goran.milosavljevic@atvssnis.edu.rs', 'none', 'goran.milosavljevic', 'pbkdf2:sha256:150000$q49Y8ppa$76c5bfcbad8e9a3e0c2418dd15611b7bb872c78c2ce20e7f081acadaafdf3f27'),
(23, 'Miloš', 'Perić', 5, 4, 'milos.peric@atvssnis.edu.rs', 'none', 'milos.peric', 'pbkdf2:sha256:150000$ZEXAgROZ$cff4127a239788dff6e738a014277aaf3b3598a78b160295e695c0e555a7c1e2');

-- --------------------------------------------------------

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
CREATE TABLE IF NOT EXISTS `role` (
  `id_role` int(11) NOT NULL AUTO_INCREMENT,
  `naziv_role` varchar(200) NOT NULL,
  PRIMARY KEY (`id_role`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `role`
--

INSERT INTO `role` (`id_role`, `naziv_role`) VALUES
(1, 'Administrator kompanije'),
(2, 'Zaposleni kompanije'),
(3, 'Administrator klijentske kompanije'),
(4, 'Zaposleni klijentske kompanije');

-- --------------------------------------------------------

--
-- Table structure for table `status`
--

DROP TABLE IF EXISTS `status`;
CREATE TABLE IF NOT EXISTS `status` (
  `id_status` int(11) NOT NULL AUTO_INCREMENT,
  `tip_statusa` varchar(100) NOT NULL,
  PRIMARY KEY (`id_status`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `status`
--

INSERT INTO `status` (`id_status`, `tip_statusa`) VALUES
(4, 'Otvoren'),
(5, 'Zatvoren'),
(8, 'U radu');

-- --------------------------------------------------------

--
-- Table structure for table `tip_zahteva`
--

DROP TABLE IF EXISTS `tip_zahteva`;
CREATE TABLE IF NOT EXISTS `tip_zahteva` (
  `id_tipa_zahteva` int(11) NOT NULL AUTO_INCREMENT,
  `naziv_tipa_zahteva` varchar(200) NOT NULL,
  `skracena_oznaka` varchar(100) NOT NULL,
  PRIMARY KEY (`id_tipa_zahteva`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tip_zahteva`
--

INSERT INTO `tip_zahteva` (`id_tipa_zahteva`, `naziv_tipa_zahteva`, `skracena_oznaka`) VALUES
(3, 'Prioritet 0', 'P0'),
(4, 'Prioritet 1', 'P1'),
(5, 'Prioritet 3', 'P3');

-- --------------------------------------------------------

--
-- Table structure for table `zahtevi`
--

DROP TABLE IF EXISTS `zahtevi`;
CREATE TABLE IF NOT EXISTS `zahtevi` (
  `id_zahteva` int(11) NOT NULL AUTO_INCREMENT,
  `broj_zahteva` bigint(20) NOT NULL,
  `datum_podnosenja` varchar(100) NOT NULL,
  `kompanija` int(11) NOT NULL,
  `ime_prezime_podnosioca` int(11) NOT NULL,
  `za_kompaniju` int(11) DEFAULT NULL,
  `zahtev` varchar(100) NOT NULL,
  `slika_kao_opis_zahteva` varchar(2000) DEFAULT NULL,
  `napomena` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT '',
  `tip_zahteva` int(11) DEFAULT NULL,
  `ocekivani_datum` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT '',
  `status` int(11) DEFAULT NULL,
  `komentar` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT '',
  `broj_utrosenih_sati` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT '',
  PRIMARY KEY (`id_zahteva`),
  UNIQUE KEY `broj_zahteva` (`broj_zahteva`),
  KEY `fk_kompanija` (`kompanija`),
  KEY `fk_tip_zahteva` (`tip_zahteva`),
  KEY `fk_ime_prezime_podnosioca` (`ime_prezime_podnosioca`),
  KEY `fk_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `korisnici`
--
ALTER TABLE `korisnici`
  ADD CONSTRAINT `fk_kompanije` FOREIGN KEY (`kompanija`) REFERENCES `kompanije` (`id_kompanije`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_rola` FOREIGN KEY (`rola`) REFERENCES `role` (`id_role`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `zahtevi`
--
ALTER TABLE `zahtevi`
  ADD CONSTRAINT `fk_ime_prezime_podnosioca` FOREIGN KEY (`ime_prezime_podnosioca`) REFERENCES `korisnici` (`id_korisnika`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_kompanija` FOREIGN KEY (`kompanija`) REFERENCES `korisnici` (`kompanija`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_status` FOREIGN KEY (`status`) REFERENCES `status` (`id_status`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_tip_zahteva` FOREIGN KEY (`tip_zahteva`) REFERENCES `tip_zahteva` (`id_tipa_zahteva`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
