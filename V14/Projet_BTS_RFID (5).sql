-- phpMyAdmin SQL Dump
-- version 5.2.1deb1+deb12u1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost:3306
-- Généré le : lun. 27 avr. 2026 à 07:05
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
-- Structure de la table `historique_acces`
--

CREATE TABLE `historique_acces` (
  `id_historique` int(11) NOT NULL,
  `id_utilisateur` int(11) DEFAULT NULL,
  `id_porte_physique` varchar(50) DEFAULT NULL,
  `date_acces` date DEFAULT NULL,
  `heure_acces` time DEFAULT NULL,
  `statut_acces` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `historique_acces`
--

INSERT INTO `historique_acces` (`id_historique`, `id_utilisateur`, `id_porte_physique`, `date_acces`, `heure_acces`, `statut_acces`) VALUES
(1, 1, 'PORTE_SUD_01', '2026-03-27', '08:05:22', 'ACCÈS_AUTORISÉ'),
(2, 2, 'LABO_RFID_02', '2026-03-27', '22:15:00', 'REFUSÉ_HORAIRE'),
(3, NULL, 'PORTE_SUD_01', '2026-03-27', '10:30:15', 'BADGE_INCONNU'),
(4, 1, 'STOCK_INFO_03', '2026-03-27', '14:20:10', 'ACCÈS_AUTORISÉ'),
(5, NULL, 'LABO_RFID_02', '2026-03-27', '02:00:00', 'REFUSÉ_INCONNU'),
(6, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '14:22:02', 'Refusé - Inconnu'),
(7, 5, 'PORTE_PRINCIPALE', '2026-04-02', '14:22:08', 'Autorisé'),
(8, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '14:22:15', 'Refusé - Inconnu'),
(9, 5, 'PORTE_PRINCIPALE', '2026-04-02', '14:23:21', 'Autorisé'),
(10, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '14:23:26', 'Refusé - Inconnu'),
(11, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '14:23:36', 'Refusé - Inconnu'),
(12, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '14:24:02', 'Refusé - Inconnu'),
(13, 5, 'PORTE_PRINCIPALE', '2026-04-02', '14:24:08', 'Autorisé'),
(14, 5, 'PORTE_PRINCIPALE', '2026-04-02', '15:08:28', 'Autorisé'),
(15, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:09:25', 'Refusé - Inconnu'),
(16, 5, 'PORTE_PRINCIPALE', '2026-04-02', '15:09:31', 'Autorisé'),
(17, 5, 'PORTE_PRINCIPALE', '2026-04-02', '15:12:54', 'Autorisé'),
(18, 5, 'PORTE_PRINCIPALE', '2026-04-02', '15:13:54', 'Autorisé'),
(19, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:24:06', 'Refusé - Inconnu'),
(20, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:24:11', 'Refusé - Inconnu'),
(21, 5, 'PORTE_PRINCIPALE', '2026-04-02', '15:24:16', 'Autorisé'),
(22, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:26:21', 'Refusé - Inconnu'),
(23, 5, 'PORTE_PRINCIPALE', '2026-04-02', '15:26:24', 'Autorisé'),
(24, 5, 'PORTE_PRINCIPALE', '2026-04-02', '15:29:52', 'Autorisé'),
(25, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:36:31', 'Refusé - Inconnu'),
(26, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:36:39', 'Refusé - Inconnu'),
(27, 5, 'PORTE_PRINCIPALE', '2026-04-02', '15:36:49', 'Autorisé'),
(28, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:39:43', 'Refusé - Inconnu'),
(29, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:40:27', 'Refusé - Inconnu'),
(30, 1, 'PORTE_PRINCIPALE', '2026-04-02', '15:51:14', 'Autorisé'),
(31, 1, 'PORTE_PRINCIPALE', '2026-04-02', '15:52:02', 'Autorisé'),
(32, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:52:35', 'Refusé - Inconnu'),
(33, NULL, 'PORTE_PRINCIPALE', '2026-04-02', '15:52:39', 'Refusé - Inconnu'),
(34, 5, 'PORTE_PRINCIPALE', '2026-04-02', '15:53:07', 'Autorisé'),
(35, 1, 'PORTE_PRINCIPALE', '2026-04-02', '16:13:59', 'Autorisé'),
(36, 1, 'PORTE_PRINCIPALE', '2026-04-02', '16:16:36', 'Autorisé'),
(37, 1, 'PORTE_PRINCIPALE', '2026-04-02', '17:03:51', 'Autorisé'),
(38, NULL, 'PORTE_PRINCIPALE', '2026-04-03', '09:26:37', 'Refusé - Inconnu'),
(39, 5, 'PORTE_PRINCIPALE', '2026-04-03', '09:26:41', 'Autorisé'),
(40, 5, 'PORTE_PRINCIPALE', '2026-04-03', '09:27:10', 'Autorisé'),
(41, 5, 'PORTE_PRINCIPALE', '2026-04-03', '09:41:44', 'Autorisé'),
(42, 5, 'PORTE_PRINCIPALE', '2026-04-03', '09:52:20', 'Autorisé'),
(43, 5, 'PORTE_PRINCIPALE', '2026-04-03', '09:52:30', 'Autorisé'),
(44, 5, 'PORTE_PRINCIPALE', '2026-04-03', '09:53:27', 'Autorisé'),
(45, 5, 'PORTE_PRINCIPALE', '2026-04-03', '09:53:38', 'Autorisé'),
(46, NULL, 'PORTE_PRINCIPALE', '2026-04-03', '09:53:43', 'Refusé - Inconnu'),
(47, NULL, 'PORTE_PRINCIPALE', '2026-04-03', '09:54:00', 'Refusé - Inconnu'),
(48, NULL, 'PORTE_PRINCIPALE', '2026-04-03', '09:54:12', 'Refusé - Inconnu'),
(49, 5, 'PORTE_PRINCIPALE', '2026-04-03', '09:54:16', 'Autorisé'),
(50, NULL, 'PORTE_PRINCIPALE', '2026-04-03', '09:54:20', 'Refusé - Inconnu'),
(51, NULL, 'PORTE_PRINCIPALE', '2026-04-03', '10:21:22', 'Refusé - Inconnu'),
(52, 5, 'PORTE_PRINCIPALE', '2026-04-03', '10:21:27', 'Autorisé'),
(53, NULL, 'PORTE_PRINCIPALE', '2026-04-08', '09:07:36', 'Refusé - Inconnu'),
(54, 5, 'PORTE_PRINCIPALE', '2026-04-08', '09:07:40', 'Autorisé'),
(55, 5, 'PORTE_PRINCIPALE', '2026-04-08', '09:12:35', 'Autorisé'),
(56, NULL, 'PORTE_PRINCIPALE', '2026-04-08', '09:12:56', 'Refusé - Inconnu'),
(57, NULL, 'PORTE_PRINCIPALE', '2026-04-08', '09:15:08', 'Refusé - Inconnu'),
(58, 5, 'PORTE_PRINCIPALE', '2026-04-08', '09:15:12', 'Autorisé'),
(59, 5, 'PORTE_PRINCIPALE', '2026-04-08', '09:15:21', 'Autorisé'),
(60, 5, 'PORTE_PRINCIPALE', '2026-04-08', '09:15:34', 'Autorisé'),
(61, 5, 'PORTE_PRINCIPALE', '2026-04-08', '09:17:25', 'Autorisé'),
(62, 5, 'PORTE_PRINCIPALE', '2026-04-08', '09:45:10', 'Autorisé'),
(63, NULL, 'PORTE_PRINCIPALE', '2026-04-08', '10:46:27', 'Refusé - Inconnu'),
(64, NULL, 'PORTE_PRINCIPALE', '2026-04-08', '10:46:28', 'Refusé - Inconnu'),
(65, 5, 'PORTE_PRINCIPALE', '2026-04-08', '10:46:32', 'Autorisé'),
(66, 5, 'PORTE_PRINCIPALE', '2026-04-08', '10:46:57', 'Autorisé'),
(67, 5, 'PORTE_PRINCIPALE', '2026-04-08', '10:47:21', 'Autorisé'),
(68, NULL, 'PORTE_PRINCIPALE', '2026-04-08', '10:47:44', 'Refusé - Inconnu'),
(69, NULL, 'PORTE_PRINCIPALE', '2026-04-08', '10:47:45', 'Refusé - Inconnu'),
(70, 5, 'PORTE_PRINCIPALE', '2026-04-08', '10:47:48', 'Autorisé'),
(71, NULL, 'PORTE_PRINCIPALE', '2026-04-09', '14:16:44', 'Refusé - Inconnu'),
(72, 5, 'PORTE_PRINCIPALE', '2026-04-09', '14:16:48', 'Autorisé'),
(73, NULL, 'PORTE_PRINCIPALE', '2026-04-09', '16:15:21', 'Refusé - Inconnu'),
(74, NULL, 'PORTE_PRINCIPALE', '2026-04-10', '08:54:41', 'Refusé - Inconnu'),
(75, 5, 'PORTE_PRINCIPALE', '2026-04-10', '08:54:44', 'Autorisé'),
(76, 5, 'PORTE_PRINCIPALE', '2026-04-10', '09:00:03', 'Autorisé'),
(77, 5, 'PORTE_PRINCIPALE', '2026-04-10', '09:00:58', 'Autorisé'),
(78, 5, 'PORTE_PRINCIPALE', '2026-04-10', '09:01:54', 'Autorisé');

-- --------------------------------------------------------

--
-- Structure de la table `materiel_stock`
--

CREATE TABLE `materiel_stock` (
  `id_materiel` int(11) NOT NULL,
  `nom_modele` varchar(50) NOT NULL,
  `rfid_tag_epc` varchar(50) NOT NULL,
  `id_utilisateur_actuel` int(11) DEFAULT NULL,
  `actif` tinyint(1) DEFAULT 1,
  `reservable` tinyint(1) DEFAULT 1,
  `etat` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `materiel_stock`
--

INSERT INTO `materiel_stock` (`id_materiel`, `nom_modele`, `rfid_tag_epc`, `id_utilisateur_actuel`, `actif`, `reservable`, `etat`) VALUES
(1, 'PC Dell Latitude', 'TAG_E041', 14, 1, 1, 'sortie'),
(3, 'Vidéoprojecteur Epson', 'TAG_E042', 1, 1, 1, 'Sortie'),
(4, 'Ecran IIyama', 'TAG_E045', NULL, 1, 1, 'Disponible'),
(5, 'Tablette Samsung', 'TAG_E046', 1, 1, 1, 'Sortie'),
(6, 'Tablette Samsung', 'TAG_E049', NULL, 1, 1, 'Disponible'),
(55, 'Ecran AOC', 'RFID188888266', NULL, 1, 1, 'maintenance'),
(77, 'Test', 'TAG_E052', NULL, 1, 1, 'disponible');

-- --------------------------------------------------------

--
-- Structure de la table `mouvements`
--

CREATE TABLE `mouvements` (
  `id_mouvement` int(11) NOT NULL,
  `id_materiel` int(11) NOT NULL,
  `id_utilisateur` int(11) NOT NULL,
  `id_utilisateur_destinataire` int(11) DEFAULT NULL,
  `type_mouvement` varchar(50) NOT NULL,
  `date_heure` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `mouvements`
--

INSERT INTO `mouvements` (`id_mouvement`, `id_materiel`, `id_utilisateur`, `id_utilisateur_destinataire`, `type_mouvement`, `date_heure`) VALUES
(25, 1, 1, NULL, 'Entrée', '2026-03-19 10:52:30'),
(26, 1, 1, NULL, 'Entrée', '2026-03-19 10:52:37'),
(27, 1, 5, NULL, 'Entrée', '2026-03-20 10:21:30'),
(28, 1, 5, NULL, 'Entrée', '2026-03-20 10:21:38'),
(29, 1, 5, NULL, 'Entrée', '2026-03-20 10:22:03'),
(30, 1, 5, NULL, 'Entrée', '2026-03-20 10:22:17'),
(31, 1, 5, NULL, 'Entrée', '2026-03-20 10:23:27'),
(32, 1, 5, NULL, 'Entrée', '2026-03-20 10:23:45'),
(33, 1, 5, NULL, 'Entrée', '2026-03-20 10:23:56'),
(34, 1, 5, NULL, 'Entrée', '2026-03-20 10:24:27'),
(35, 1, 5, NULL, 'Entrée', '2026-03-20 10:24:32'),
(36, 1, 5, NULL, 'Entrée', '2026-03-20 10:24:36'),
(37, 1, 5, NULL, 'Entrée', '2026-03-20 10:40:39'),
(38, 1, 1, 1, 'sortie', '2026-03-23 09:44:47'),
(39, 1, 1, 1, 'disponible', '2026-03-23 09:44:55'),
(40, 1, 1, 1, 'disponible', '2026-03-23 09:47:29'),
(41, 1, 1, 1, 'disponible', '2026-03-23 09:47:49'),
(42, 1, 1, 1, 'sortie', '2026-03-23 09:49:30'),
(43, 1, 1, 1, 'disponible', '2026-03-23 09:49:37'),
(44, 4, 1, 1, 'disponible', '2026-03-23 09:54:26'),
(45, 4, 1, NULL, 'sortie', '2026-03-23 09:54:33'),
(46, 3, 1, NULL, 'maintenance', '2026-03-23 09:54:49'),
(47, 3, 1, NULL, 'maintenance', '2026-03-23 10:00:47'),
(48, 1, 1, 2, 'sortie', '2026-03-23 10:03:54'),
(49, 3, 5, 1, 'disponible', '2026-03-23 10:20:25'),
(50, 3, 5, NULL, 'disponible', '2026-03-23 10:20:45'),
(51, 1, 1, 1, 'sortie', '2026-03-23 10:52:14'),
(52, 4, 1, 1, 'sortie', '2026-03-26 09:53:25'),
(53, 4, 1, 2, 'sortie', '2026-03-26 09:53:34'),
(54, 1, 1, 1, 'disponible', '2026-03-26 15:10:01'),
(55, 3, 1, NULL, 'sortie', '2026-03-26 15:10:11'),
(56, 55, 1, NULL, 'maintenance', '2026-03-26 15:24:13'),
(57, 1, 5, NULL, 'Sortie', '2026-03-30 09:41:53'),
(58, 1, 5, NULL, 'Sortie', '2026-03-30 09:42:32'),
(59, 1, 5, NULL, 'Sortie', '2026-03-30 09:44:34'),
(60, 1, 1, NULL, 'Sortie', '2026-03-30 09:46:00'),
(61, 5, 1, NULL, 'Sortie', '2026-04-09 09:46:17'),
(62, 1, 2, NULL, 'Entrée', '2026-04-09 09:58:00'),
(63, 1, 1, NULL, 'Sortie', '2026-04-09 10:13:13'),
(64, 3, 1, NULL, 'Sortie', '2026-04-09 11:09:07'),
(65, 3, 1, NULL, 'Sortie', '2026-04-09 11:17:53'),
(66, 1, 1, NULL, 'Entrée', '2026-04-09 11:28:09'),
(67, 4, 1, NULL, 'Sortie', '2026-04-09 11:33:53'),
(68, 4, 1, NULL, 'Entrée', '2026-04-09 11:34:15'),
(69, 6, 1, NULL, 'Entrée', '2026-04-09 15:03:16');

-- --------------------------------------------------------

--
-- Structure de la table `portes`
--

CREATE TABLE `portes` (
  `id_acces` int(11) NOT NULL,
  `id_porte_physique` varchar(50) DEFAULT NULL,
  `nom_affichage` varchar(100) DEFAULT NULL,
  `heure_debut` time DEFAULT '08:00:00',
  `heure_fin` time DEFAULT '18:00:00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `portes`
--

INSERT INTO `portes` (`id_acces`, `id_porte_physique`, `nom_affichage`, `heure_debut`, `heure_fin`) VALUES
(1, NULL, NULL, '07:30:00', '18:00:00');

-- --------------------------------------------------------

--
-- Structure de la table `prets`
--

CREATE TABLE `prets` (
  `id_pret` int(11) NOT NULL,
  `id_materiel` int(11) NOT NULL,
  `id_preteur` int(11) NOT NULL,
  `id_emprunteur` int(11) NOT NULL,
  `date_demande` datetime DEFAULT current_timestamp(),
  `date_validation` datetime DEFAULT NULL,
  `statut` enum('en_attente','accepte','refuse') DEFAULT 'en_attente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `prets`
--

INSERT INTO `prets` (`id_pret`, `id_materiel`, `id_preteur`, `id_emprunteur`, `date_demande`, `date_validation`, `statut`) VALUES
(1, 1, 1, 5, '2026-03-19 14:49:58', '2026-03-19 14:50:25', 'refuse'),
(2, 1, 2, 1, '2026-03-23 10:47:18', '2026-03-23 10:47:34', 'accepte');

-- --------------------------------------------------------

--
-- Structure de la table `reservations`
--

CREATE TABLE `reservations` (
  `id_reservation` int(11) NOT NULL,
  `id_materiel` int(11) NOT NULL,
  `id_utilisateur` int(11) NOT NULL,
  `date_reservation` datetime DEFAULT current_timestamp(),
  `date_rendu_prevue` datetime DEFAULT NULL,
  `statut` enum('En attente','Confirmée','Annulée','Récupérée','Rendu','Retard') DEFAULT 'En attente',
  `date_limite` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `utilisateurs`
--

CREATE TABLE `utilisateurs` (
  `id_utilisateur` int(11) NOT NULL,
  `utilisateur` varchar(50) NOT NULL,
  `mot_de_passe` varchar(255) NOT NULL,
  `badge_uid` varchar(255) DEFAULT NULL,
  `nom` varchar(50) NOT NULL,
  `prenom` varchar(50) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `role` varchar(20) NOT NULL,
  `admin` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id_utilisateur`, `utilisateur`, `mot_de_passe`, `badge_uid`, `nom`, `prenom`, `email`, `telephone`, `role`, `admin`) VALUES
(1, 'ethan', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '8d10c4659e6fcfc5dc30413f87508e3510da73fff2d5aa115a9995d8ec27b431', 'Delaporte', 'Ethan', 'delaporte.ethanpro@gmail.com', '07848456521', 'Professeur', 1),
(2, 'louis', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'UID23456', 'Ferrand', 'Louis', 'Louis@gmail', '076767676767', 'Professeur', 0),
(3, 'moussa', 'db3894853d31b0a4318e732d125c39df90224cfbece2cb3136d1552483f2e624', 'UID5678', 'Moussa', 'Jean', 'Louis@gmail', NULL, 'Professeur', 0),
(5, 'Thibaud', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '13f216a45795b897e3f6e05cd3807c107c055a88dc59828cf2fb2adddba02200', 'Van-Heule', 'Thibaud', 'thibuad@email', '0689879163', 'Élève', 1),
(12, 'aidan', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'aidan', 'aidan', 'aidan@gmail', '0607065165', 'Élève', 0),
(14, 'eyal', 'fa4163dfc1f6223c36e1d74fa46d5849e4b95cc463e728437b933273921132cb', '15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225', 'eyal', 'eyal', 'eyal@aaa', '07789', 'Élève', 0),
(15, 'kln', '1aba584103fff51ee61286c31600bbb7443b50f82f5128bb5c6b198dfb4bfa00', NULL, 'kln', 'kln', 'kln@gmail.com', '0689879163', 'Élève', 0);

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `historique_acces`
--
ALTER TABLE `historique_acces`
  ADD PRIMARY KEY (`id_historique`),
  ADD KEY `id_utilisateur` (`id_utilisateur`);

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
  ADD KEY `id_utilisateur` (`id_utilisateur`),
  ADD KEY `id_utilisateur_destinataire` (`id_utilisateur_destinataire`);

--
-- Index pour la table `portes`
--
ALTER TABLE `portes`
  ADD PRIMARY KEY (`id_acces`),
  ADD UNIQUE KEY `id_porte_physique` (`id_porte_physique`);

--
-- Index pour la table `prets`
--
ALTER TABLE `prets`
  ADD PRIMARY KEY (`id_pret`),
  ADD KEY `id_materiel` (`id_materiel`),
  ADD KEY `id_preteur` (`id_preteur`),
  ADD KEY `id_emprunteur` (`id_emprunteur`);

--
-- Index pour la table `reservations`
--
ALTER TABLE `reservations`
  ADD PRIMARY KEY (`id_reservation`),
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
-- AUTO_INCREMENT pour la table `historique_acces`
--
ALTER TABLE `historique_acces`
  MODIFY `id_historique` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=79;

--
-- AUTO_INCREMENT pour la table `materiel_stock`
--
ALTER TABLE `materiel_stock`
  MODIFY `id_materiel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=78;

--
-- AUTO_INCREMENT pour la table `mouvements`
--
ALTER TABLE `mouvements`
  MODIFY `id_mouvement` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=70;

--
-- AUTO_INCREMENT pour la table `portes`
--
ALTER TABLE `portes`
  MODIFY `id_acces` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `prets`
--
ALTER TABLE `prets`
  MODIFY `id_pret` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT pour la table `reservations`
--
ALTER TABLE `reservations`
  MODIFY `id_reservation` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  MODIFY `id_utilisateur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `historique_acces`
--
ALTER TABLE `historique_acces`
  ADD CONSTRAINT `historique_acces_ibfk_1` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`);

--
-- Contraintes pour la table `materiel_stock`
--
ALTER TABLE `materiel_stock`
  ADD CONSTRAINT `materiel_stock_ibfk_1` FOREIGN KEY (`id_utilisateur_actuel`) REFERENCES `utilisateurs` (`id_utilisateur`);

--
-- Contraintes pour la table `mouvements`
--
ALTER TABLE `mouvements`
  ADD CONSTRAINT `mouvements_ibfk_1` FOREIGN KEY (`id_materiel`) REFERENCES `materiel_stock` (`id_materiel`),
  ADD CONSTRAINT `mouvements_ibfk_2` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`),
  ADD CONSTRAINT `mouvements_ibfk_3` FOREIGN KEY (`id_utilisateur_destinataire`) REFERENCES `utilisateurs` (`id_utilisateur`);

--
-- Contraintes pour la table `prets`
--
ALTER TABLE `prets`
  ADD CONSTRAINT `prets_ibfk_1` FOREIGN KEY (`id_materiel`) REFERENCES `materiel_stock` (`id_materiel`),
  ADD CONSTRAINT `prets_ibfk_2` FOREIGN KEY (`id_preteur`) REFERENCES `utilisateurs` (`id_utilisateur`),
  ADD CONSTRAINT `prets_ibfk_3` FOREIGN KEY (`id_emprunteur`) REFERENCES `utilisateurs` (`id_utilisateur`);

--
-- Contraintes pour la table `reservations`
--
ALTER TABLE `reservations`
  ADD CONSTRAINT `reservations_ibfk_1` FOREIGN KEY (`id_materiel`) REFERENCES `materiel_stock` (`id_materiel`),
  ADD CONSTRAINT `reservations_ibfk_2` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
