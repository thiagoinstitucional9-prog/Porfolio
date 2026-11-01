CREATE TABLE `users` (
  `id` integer PRIMARY KEY,
  `username` varchar(255),
  `email` varchar(255),
  `role` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `teams` (
  `id` integer PRIMARY KEY,
  `name` varchar(255),
  `country` varchar(255),
  `group_name` varchar(10)
);

CREATE TABLE `players` (
  `id` integer PRIMARY KEY,
  `name` varchar(255),
  `position` varchar(255),
  `team_id` integer
);

CREATE TABLE `matches` (
  `id` integer PRIMARY KEY,
  `team1_id` integer,
  `team2_id` integer,
  `date` timestamp,
  `stadium` varchar(255),
  `score_team1` integer,
  `score_team2` integer
);

CREATE TABLE `news` (
  `id` integer PRIMARY KEY,
  `title` varchar(255),
  `body` text,
  `user_id` integer,
  `created_at` timestamp
);

CREATE TABLE `comments` (
  `id` integer PRIMARY KEY,
  `body` text,
  `user_id` integer,
  `news_id` integer,
  `created_at` timestamp
);

ALTER TABLE `players`
ADD FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`);

ALTER TABLE `matches`
ADD FOREIGN KEY (`team1_id`) REFERENCES `teams` (`id`);

ALTER TABLE `matches`
ADD FOREIGN KEY (`team2_id`) REFERENCES `teams` (`id`);

ALTER TABLE `news`
ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `comments`
ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `comments`
ADD FOREIGN KEY (`news_id`) REFERENCES `news` (`id`);


NSERT INTO `users` (`id`, `username`, `email`, `role`)
VALUES
(1, 'admin', 'admin@gmail.com', 'admin'),
(2, 'juan', 'juan@gmail.com', 'user'),
(3, 'pedro', 'pedro@gmail.com', 'user');




INSERT INTO `teams` (`id`, `name`, `country`, `group_name`)
VALUES
(1, 'Argentina', 'Argentina', 'J'),
(2, 'Brasil', 'Brasil', 'C'),
(3, 'Francia', 'Francia', 'I'),
(4, 'España', 'España', 'H');


INSERT INTO `players` (`id`, `name`, `position`, `team_id`)
VALUES
(1, 'Messi', 'Delantero', 1),
(2, 'Alvarez', 'Delantero', 1),
(3, 'Vinicius', 'Delantero', 2),
(4, 'Mbappe', 'Delantero', 3),
(5, 'Yamal', 'Delantero', 4);



INSERT INTO `matches` (`id`, `team1_id`, `team2_id`, `date`, `stadium`)
VALUES
(1, 1, 2, '2026-06-15 18:00:00', 'Estadio 1'),
(2, 3, 4, '2026-06-16 20:00:00', 'Estadio 2');




INSERT INTO `news` (`id`, `title`, `body`, `user_id`)
VALUES
(1, 'Comienza el Mundial 2026', 'Se acerca el inicio de la Copa del Mundo.', 1),
(2, 'Argentina busca defender el titulo', 'La seleccion argentina se prepara para el torneo.', 1);



INSERT INTO `comments` (`id`, `body`, `user_id`, `news_id`)
VALUES
(1, 'Vamos Argentina!', 2, 2),
(2, 'Va a ser un gran mundial.', 3, 1);