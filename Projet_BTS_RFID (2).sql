-- phpMyAdmin SQL Dump
-- version 5.2.1deb1+deb12u1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost:3306
-- Généré le : jeu. 19 mars 2026 à 14:06
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
  `nom_modele` varchar(50) NOT NULL,
  `rfid_tag_epc` varchar(50) NOT NULL,
  `id_utilisateur_actuel` int(11) DEFAULT NULL,
  `actif` tinyint(1) DEFAULT 1,
  `reservable` tinyint(1) DEFAULT 1,
  `etat` enum('disponible','reserve','indisponible','maintenance') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `materiel_stock`
--

INSERT INTO `materiel_stock` (`id_materiel`, `nom_modele`, `rfid_tag_epc`, `id_utilisateur_actuel`, `actif`, `reservable`, `etat`) VALUES
(1, 'PC Dell Latitude', 'TAG_E041', 1, 1, 1, 'reserve'),
(3, 'Vidéoprojecteur Epson', 'TAG_E042', NULL, 1, 1, 'disponible'),
(4, 'Ecran IIyama', 'TAG_E045', NULL, 1, 1, 'maintenance'),
(5, 'Tablette Samsung', 'TAG_E046', NULL, 1, 1, 'indisponible');

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
(26, 1, 1, NULL, 'Entrée', '2026-03-19 10:52:37');

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
(1, 1, 1, 5, '2026-03-19 14:49:58', '2026-03-19 14:50:25', 'refuse');

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
(11, 1, 1, '2026-03-19 00:00:00', 'confirmée', '2026-03-20 08:00:00');

-- --------------------------------------------------------

--
-- Structure de la table `utilisateurs`
--

CREATE TABLE `utilisateurs` (
  `id_utilisateur` int(11) NOT NULL,
  `utilisateur` varchar(50) NOT NULL,
  `mot_de_passe` varchar(255) NOT NULL,
  `badge_uid` varchar(50) DEFAULT NULL,
  `nom` varchar(50) NOT NULL,
  `prenom` varchar(50) NOT NULL,
  `role` varchar(20) NOT NULL,
  `admin` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id_utilisateur`, `utilisateur`, `mot_de_passe`, `badge_uid`, `nom`, `prenom`, `role`, `admin`) VALUES
(1, 'ethan', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'UID1234', 'Delaporte', 'Ethan', 'Admin', 1),
(2, 'louis', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'UID2345', 'Ferrand', 'Louis', 'Professeur', 0),
(3, 'moussa', 'db3894853d31b0a4318e732d125c39df90224cfbece2cb3136d1552483f2e624', 'UID5678', 'Moussa', 'Jean', 'Professeur', 0),
(4, 'tessier', '4b076202647e0eb41d1e263e2b3c11d5b9b8fea9a856864b67c9a477e17341c6', 'UID6789', 'Tessier', 'Paul', 'Professeur', 0),
(5, 'Thibaud', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', NULL, 'Van-Heule', 'Thibaud', 'Élève', 0);

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
  ADD KEY `id_utilisateur` (`id_utilisateur`),
  ADD KEY `id_utilisateur_destinataire` (`id_utilisateur_destinataire`);

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
-- AUTO_INCREMENT pour la table `materiel_stock`
--
ALTER TABLE `materiel_stock`
  MODIFY `id_materiel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `mouvements`
--
ALTER TABLE `mouvements`
  MODIFY `id_mouvement` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT pour la table `prets`
--
ALTER TABLE `prets`
  MODIFY `id_pret` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `reservations`
--
ALTER TABLE `reservations`
  MODIFY `id_reservation` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

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
