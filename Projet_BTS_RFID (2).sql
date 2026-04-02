-- phpMyAdmin SQL Dump
-- version 5.2.1deb1+deb12u1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost:3306
-- Généré le : ven. 27 mars 2026 à 08:29
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
(1, 'PC Dell Latitude', 'TAG_E041', NULL, 1, 1, 'disponible'),
(3, 'Vidéoprojecteur Epson', 'TAG_E042', NULL, 1, 1, 'sortie'),
(4, 'Ecran IIyama', 'TAG_E045', 2, 1, 1, 'sortie'),
(5, 'Tablette Samsung', 'TAG_E046', NULL, 1, 1, 'sortie'),
(6, 'Tablette Samsung', 'TAG_E049', NULL, 1, 1, 'disponible'),
(55, 'Ecran AOC', 'RFID188888266', NULL, 1, 1, 'maintenance'),
(77, 'Test', '123456789', NULL, 1, 1, 'disponible');

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
(56, 55, 1, NULL, 'maintenance', '2026-03-26 15:24:13');

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
  `statut` enum('en attente','confirmée','annulée') DEFAULT 'en attente',
  `date_limite` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `reservations`
--

INSERT INTO `reservations` (`id_reservation`, `id_materiel`, `id_utilisateur`, `date_reservation`, `statut`, `date_limite`) VALUES
(11, 1, 1, '2026-03-19 00:00:00', 'annulée', '2026-03-20 08:00:00'),
(12, 3, 1, '2026-03-21 00:00:00', 'annulée', '2026-03-22 08:00:00'),
(13, 6, 1, '2026-03-29 00:00:00', 'confirmée', '2026-03-30 08:00:00');

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
(1, 'ethan', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'UID1234', 'Delaporte', 'Ethan', 'delaporte.ethanpro@gmail.com', '07848456521', 'Admin', 1),
(2, 'louis', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'UID23456', 'Ferrand', 'Louis', 'Louis@gmail', '076767676767', 'Professeur', 0),
(3, 'moussa', 'db3894853d31b0a4318e732d125c39df90224cfbece2cb3136d1552483f2e624', 'UID5678', 'Moussa', 'Jean', NULL, NULL, 'Professeur', 0),
(4, 'tessier', '4b076202647e0eb41d1e263e2b3c11d5b9b8fea9a856864b67c9a477e17341c6', 'none', 'Tessier', 'Paul', 'None@132', 'None', 'Professeur', 0),
(5, 'Thibaud', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '84141775136', 'Van-Heule', 'Thibaud', 'thibuad@email', '0689879163', 'Élève', 1),
(8, 'test2', '60303ae22b998861bce3b28f33eec1be758a213c86c93c076dbe9f558c11c752', 'None', 'test2', 'test2', 'test2@aaaa', '07125155', 'Élève', 0),
(12, 'aidan', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'aidan', 'aidan', 'aidan@gmail', '0607065165', 'Élève', 0),
(14, 'eyal', 'fa4163dfc1f6223c36e1d74fa46d5849e4b95cc463e728437b933273921132cb', '15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225', 'eyal', 'eyal', 'eyal@aaa', '07789', 'Élève', 0);

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
  MODIFY `id_historique` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `materiel_stock`
--
ALTER TABLE `materiel_stock`
  MODIFY `id_materiel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=78;

--
-- AUTO_INCREMENT pour la table `mouvements`
--
ALTER TABLE `mouvements`
  MODIFY `id_mouvement` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;

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
  MODIFY `id_reservation` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  MODIFY `id_utilisateur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

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
