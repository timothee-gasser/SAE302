CREATE DATABASE SAE302;
USE SAE302;
CREATE USER 'toto'@'%' IDENTIFIED BY 'toto';
GRANT INSERT, SELECT, UPDATE, DELETE ON SAE302.* TO 'toto'@'%';

CREATE TABLE `Ban` (
  `id_ban` int(11) NOT NULL,
  `ban_ip` text DEFAULT NULL,
  `id_util` int(11) DEFAULT NULL,
  `raison_ban` text DEFAULT NULL,
  `d_h_ban` datetime NOT NULL
);

CREATE TABLE `Demande` (
  `id_demande` int(11) NOT NULL,
  `type_demande` varchar(20) NOT NULL,
  `id_util` int(11) NOT NULL,
  `d_h_demande` datetime NOT NULL,
  `etat_demande` varchar(20) NOT NULL,
  `demande` text NOT NULL,
  `commentaire` text DEFAULT NULL
) ;

CREATE TABLE `Demande_salon` (
  `id_dsalon` int(11) NOT NULL,
  `id_util` int(11) NOT NULL,
  `id_salon` int(11) NOT NULL,
  `etat_dsalon` varchar(20) NOT NULL,
  `raison_dsalon` text DEFAULT NULL
);

CREATE TABLE `Histo_msg` (
  `id_msg` int(11) NOT NULL,
  `h_d_msg` datetime NOT NULL,
  `emetteur` varchar(20) NOT NULL,
  `recepteur` varchar(20) DEFAULT NULL,
  `msg` text NOT NULL,
  `id_salon` int(11) DEFAULT NULL
);

CREATE TABLE `Kick` (
  `id_kick` int(11) NOT NULL,
  `id_util` int(11) NOT NULL,
  `raison_kick` text NOT NULL,
  `d_h_kick` datetime NOT NULL,
  `fin_kick` datetime NOT NULL
);

CREATE TABLE `Killh` (
  `id_kill` int(11) NOT NULL,
  `id_util` int(11) NOT NULL,
  `raison_kill` text DEFAULT NULL,
  `d_h_kill` datetime NOT NULL
);

CREATE TABLE `Logs` (
  `id_logs` int(11) NOT NULL,
  `logs` text NOT NULL,
  `d_h_logs` datetime NOT NULL
) ;

CREATE TABLE `Salon` (
  `id_salon` int(11) NOT NULL,
  `id_membre` text DEFAULT NULL,
  `nom_salon` varchar(20) NOT NULL,
  `type_salon` varchar(20) NOT NULL
) ;


INSERT INTO `Salon` (`id_salon`, `id_membre`, `nom_salon`, `type_salon`) VALUES
(1, '1', 'general', 'open'),
(2, '1', 'admin', 'close'),
(3, '1', 'salle_de_pause', 'open');

CREATE TABLE `Utilisateur` (
  `id_util` int(11) NOT NULL,
  `login` varchar(20) NOT NULL,
  `mdp` varchar(20) NOT NULL,
  `last_ip` text DEFAULT NULL,
  `type_util` varchar(20) DEFAULT NULL,
  `etat_util` varchar(20) NOT NULL
);


INSERT INTO `Utilisateur` (`id_util`, `login`, `mdp`, `last_ip`, `type_util`, `etat_util`) VALUES
(1, 'root', 'admin', admin, NULL, '');

ALTER TABLE `Ban`
  ADD PRIMARY KEY (`id_ban`),
  ADD UNIQUE KEY `type_ban` (`ban_ip`) USING HASH,
  ADD KEY `id_util` (`id_util`);

ALTER TABLE `Demande`
  ADD PRIMARY KEY (`id_demande`),
  ADD KEY `id_util` (`id_util`);

ALTER TABLE `Demande_salon`
  ADD PRIMARY KEY (`id_dsalon`),
  ADD KEY `id_util` (`id_util`,`id_salon`),
  ADD KEY `id_salon` (`id_salon`);

ALTER TABLE `Histo_msg`
  ADD PRIMARY KEY (`id_msg`),
  ADD KEY `id_salon` (`id_salon`);

ALTER TABLE `Kick`
  ADD PRIMARY KEY (`id_kick`),
  ADD KEY `id_util` (`id_util`);

ALTER TABLE `Killh`
  ADD PRIMARY KEY (`id_kill`),
  ADD KEY `id_util` (`id_util`);

ALTER TABLE `Logs`
  ADD PRIMARY KEY (`id_logs`);

ALTER TABLE `Salon`
  ADD PRIMARY KEY (`id_salon`),
  ADD UNIQUE KEY `nom_salon` (`nom_salon`);

ALTER TABLE `Utilisateur`
  ADD PRIMARY KEY (`id_util`),
  ADD UNIQUE KEY `login` (`login`);

ALTER TABLE `Ban`
  MODIFY `id_ban` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Demande`
  MODIFY `id_demande` int(11) NOT NULL AUTO_INCREMENT

ALTER TABLE `Demande_salon`
  MODIFY `id_dsalon` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Histo_msg`
  MODIFY `id_msg` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Kick`
  MODIFY `id_kick` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Killh`
  MODIFY `id_kill` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Logs`
  MODIFY `id_logs` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Salon`
  MODIFY `id_salon` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Utilisateur`
  MODIFY `id_util` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Ban`
  ADD CONSTRAINT `Ban_ibfk_1` FOREIGN KEY (`id_util`) REFERENCES `Utilisateur` (`id_util`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Demande`
  ADD CONSTRAINT `Demande_ibfk_1` FOREIGN KEY (`id_util`) REFERENCES `Utilisateur` (`id_util`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Demande_salon`
  ADD CONSTRAINT `Demande_salon_ibfk_1` FOREIGN KEY (`id_util`) REFERENCES `Utilisateur` (`id_util`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Demande_salon_ibfk_2` FOREIGN KEY (`id_salon`) REFERENCES `Salon` (`id_salon`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Histo_msg`
  ADD CONSTRAINT `Histo_msg_ibfk_1` FOREIGN KEY (`id_salon`) REFERENCES `Salon` (`id_salon`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Kick`
  ADD CONSTRAINT `Kick_ibfk_1` FOREIGN KEY (`id_util`) REFERENCES `Utilisateur` (`id_util`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Killh`
  ADD CONSTRAINT `Killh_ibfk_1` FOREIGN KEY (`id_util`) REFERENCES `Utilisateur` (`id_util`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

