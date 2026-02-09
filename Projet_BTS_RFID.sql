-- phpMyAdmin SQL Dump
-- version 5.2.1deb1+deb12u1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost:3306
-- Généré le : lun. 09 fév. 2026 à 10:06
-- Version du serveur : 10.11.14-MariaDB-0+deb12u2
-- Version de PHP : 8.2.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `Projet_BTS_RFID`
--

-- --------------------------------------------------------

--
-- Structure de la table `materiel_stock`
--

CREATE TABLE `materiel_stock` (
  `id_materiel` int(11) NOT NULL,
  `rfid_tag_epc` varchar(50) NOT NULL,
  `nom_modele` varchar(50) DEFAULT NULL,
  `statut` varchar(20) DEFAULT NULL,
  `id_utilisateur_actuel` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `materiel_stock`
--

INSERT INTO `materiel_stock` (`id_materiel`, `rfid_tag_epc`, `nom_modele`, `statut`, `id_utilisateur_actuel`) VALUES
(1, 'TAG_E041', 'PC Dell Latitude', 'En Stock', NULL),
(2, 'TAG_E042', 'Vidéoprojecteur Epson', 'Sorti', 1),
(3, 'TAG003', 'Souris Logitech', 'En Stock', NULL),
(4, 'TAG004', 'Vidéoprojecteur Epson', 'Sorti', 1),
(5, 'TAG005', 'Webcam Microsoft', 'En Stock', NULL),
(6, 'TAG006', 'Casque Bose', 'En Stock', NULL),
(7, 'TAG007', 'Tablette Samsung', 'Sorti', 3),
(8, 'TAG008', 'Imprimante HP', 'En Stock', NULL),
(9, 'TAG009', 'Scanner Canon', 'En Stock', NULL),
(10, 'TAG010', 'Microphone Blue', 'Sorti', 4),
(11, 'TAG011', 'Switch Netgear', 'En Stock', NULL),
(12, 'TAG012', 'Routeur TP-Link', 'En Stock', NULL),
(13, 'TAG013', 'Disque dur Seagate', 'Sorti', 5),
(14, 'TAG014', 'Projecteur BenQ', 'En Stock', NULL),
(15, 'TAG015', 'Écran LG', 'Sorti', 1);

-- --------------------------------------------------------

--
-- Structure de la table `mouvements`
--

CREATE TABLE `mouvements` (
  `id_mouvement` int(11) NOT NULL,
  `id_materiel` int(11) NOT NULL,
  `id_utilisateur` int(11) NOT NULL,
  `type_mouvement` varchar(20) DEFAULT NULL,
  `date_heure` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `mouvements`
--

INSERT INTO `mouvements` (`id_mouvement`, `id_materiel`, `id_utilisateur`, `type_mouvement`, `date_heure`) VALUES
(1, 2, 1, 'Sortie', '2026-02-09 08:55:06'),
(2, 2, 2, 'Sortie', '2026-02-09 09:10:22'),
(3, 3, 3, 'Sortie', '2026-02-09 09:15:45'),
(4, 4, 1, 'Sortie', '2026-02-09 08:55:06'),
(5, 5, 2, 'Sortie', '2026-02-09 09:20:00'),
(6, 6, 3, 'Sortie', '2026-02-09 09:25:30'),
(7, 7, 4, 'Sortie', '2026-02-09 09:30:12'),
(8, 8, 5, 'Sortie', '2026-02-09 09:35:45'),
(9, 9, 1, 'Sortie', '2026-02-09 09:40:05'),
(10, 10, 2, 'Sortie', '2026-02-09 09:45:20'),
(11, 11, 3, 'Sortie', '2026-02-09 09:50:00'),
(12, 12, 4, 'Sortie', '2026-02-09 09:55:30'),
(13, 13, 5, 'Sortie', '2026-02-09 10:00:00'),
(14, 14, 1, 'Sortie', '2026-02-09 10:05:12'),
(15, 15, 2, 'Sortie', '2026-02-09 10:10:45'),
(16, 2, 2, 'Entrée', '2026-02-09 11:00:00'),
(17, 4, 1, 'Entrée', '2026-02-09 12:30:00'),
(18, 7, 3, 'Entrée', '2026-02-09 14:15:00'),
(19, 10, 4, 'Entrée', '2026-02-09 15:45:00'),
(20, 15, 2, 'Entrée', '2026-02-09 16:20:00');

-- --------------------------------------------------------

--
-- Structure de la table `utilisateurs`
--

CREATE TABLE `utilisateurs` (
  `id_utilisateur` int(11) NOT NULL,
  `utilisateur` varchar(50) NOT NULL,
  `mot_de_passe` varchar(255) NOT NULL,
  `badge_uid` varchar(50) DEFAULT NULL,
  `nom` varchar(50) DEFAULT NULL,
  `prenom` varchar(50) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id_utilisateur`, `utilisateur`, `mot_de_passe`, `badge_uid`, `nom`, `prenom`, `role`) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'UID_001', 'Dupont', 'Jean', 'admin'),
(2, 'ethan', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'UID_002', 'Delaporte', 'Ethan', 'user'),
(3, 'tmartin', '2f81cba8c3e6f76972a8a3991fd5980eb77515f1fc9d05e5e094e1b82f457776', 'UID003', 'Van-Heule', 'Thibaud', 'utilisateur'),
(4, 'lferrand', '2f81cba8c3e6f76972a8a3991fd5980eb77515f1fc9d05e5e094e1b82f457776', 'UID004', 'Ferrand', 'Louis', 'utilisateur'),
(5, 'aleroy', '2f81cba8c3e6f76972a8a3991fd5980eb77515f1fc9d05e5e094e1b82f457776', 'UID005', 'Leroy', 'Alice', 'utilisateur');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `materiel_stock`
--
ALTER TABLE `materiel_stock`
  ADD PRIMARY KEY (`id_materiel`),
  ADD UNIQUE KEY `rfid_tag_epc` (`rfid_tag_epc`),
  ADD KEY `id_utilisateur_actuel` (`id_utilisateur_actuel`);

--
-- Index pour la table `mouvements`
--
ALTER TABLE `mouvements`
  ADD PRIMARY KEY (`id_mouvement`),
  ADD KEY `id_materiel` (`id_materiel`),
  ADD KEY `id_utilisateur` (`id_utilisateur`);

--
-- Index pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  ADD PRIMARY KEY (`id_utilisateur`),
  ADD UNIQUE KEY `utilisateur` (`utilisateur`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `materiel_stock`
--
ALTER TABLE `materiel_stock`
  MODIFY `id_materiel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT pour la table `mouvements`
--
ALTER TABLE `mouvements`
  MODIFY `id_mouvement` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  MODIFY `id_utilisateur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `materiel_stock`
--
ALTER TABLE `materiel_stock`
  ADD CONSTRAINT `materiel_stock_ibfk_1` FOREIGN KEY (`id_utilisateur_actuel`) REFERENCES `utilisateurs` (`id_utilisateur`) ON DELETE SET NULL;

--
-- Contraintes pour la table `mouvements`
--
ALTER TABLE `mouvements`
  ADD CONSTRAINT `mouvements_ibfk_1` FOREIGN KEY (`id_materiel`) REFERENCES `materiel_stock` (`id_materiel`) ON DELETE CASCADE,
  ADD CONSTRAINT `mouvements_ibfk_2` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
