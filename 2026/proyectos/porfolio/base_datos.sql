-- ============================================================
-- PROYECTO: Portfolio Web Personal Full Stack
-- ARCHIVO: base_datos.sql
-- MOTOR: MySQL 8 (también funciona en MariaDB moderno)
-- ============================================================
--
-- QUE HACE ESTE ARCHIVO:
-- 1. Crea la base de datos portfolio_db.
-- 2. Crea las tablas con sus claves primarias y foraneas.
-- 3. Carga datos de ejemplo para poder ver el portfolio funcionando.
--
-- COMO SE EJECUTA:
--   mysql -u root -p --default-character-set=utf8mb4 < base_datos.sql
--
-- O también se puede abrir este archivo con MySQL Workbench y ejecutarlo.
-- La opción --default-character-set=utf8mb4 permite que los acentos y
-- la letra ñ se guarden correctamente.
--
-- IMPORTANTE:
-- - Si el servicio de hosting ya creó una base de datos, se pueden
--   comentar las lineas CREATE DATABASE y USE, y ejecutar el resto
--   dentro de la base que nos dieron.
-- - Este script BORRA las tablas si ya existen. Es comodo mientras
--   estamos aprendiendo, pero no se debe ejecutar sobre datos reales.
-- ============================================================


-- ------------------------------------------------------------
-- 1. CREACION DE LA BASE DE DATOS
-- ------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS portfolio_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE portfolio_db;

SET NAMES utf8mb4;


-- ------------------------------------------------------------
-- 2. BORRADO DE TABLAS ANTERIORES
-- ------------------------------------------------------------
-- Se desactivan las comprobaciones de claves foráneas para poder
-- borrar primero las tablas hijas y después las tablas padre.
-- El orden de borrado va de la tabla hija a la tabla padre.

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS redes_sociales;
DROP TABLE IF EXISTS proyectos;
DROP TABLE IF EXISTS idiomas;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS educacion;
DROP TABLE IF EXISTS experiencias;
DROP TABLE IF EXISTS perfil;
DROP TABLE IF EXISTS usuarios;

SET FOREIGN_KEY_CHECKS = 1;


-- ------------------------------------------------------------
-- 3. TABLA usuarios
-- ------------------------------------------------------------
-- Guarda el usuario que puede entrar al modo edicion.
-- La contraseña NUNCA se guarda en texto plano: se guarda un hash
-- generado con werkzeug.security.generate_password_hash().

CREATE TABLE usuarios (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre_usuario VARCHAR(50) NOT NULL,
    clave_hash VARCHAR(255) NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usuarios_nombre_usuario (nombre_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 4. TABLA perfil
-- ------------------------------------------------------------
-- Tiene los datos personales que se muestran en el encabezado y
-- en la seccion "Acerca de".
--
-- usuario_id es una clave foranea: relaciona el perfil con su usuario.
-- La relacion es uno a uno porque un usuario tiene un solo perfil.
-- El UNIQUE en usuario_id impide que un mismo usuario tenga dos perfiles.

CREATE TABLE perfil (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    usuario_id INT UNSIGNED NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    titulo_profesional VARCHAR(150) NOT NULL,
    resumen TEXT NOT NULL,
    texto_banner VARCHAR(255) NOT NULL,
    foto_perfil VARCHAR(255) NOT NULL DEFAULT 'img/perfil-ejemplo.svg',
    imagen_banner VARCHAR(255) NOT NULL DEFAULT 'img/banner-ejemplo.svg',
    archivo_cv VARCHAR(255) NOT NULL DEFAULT 'cv/cv-ejemplo.pdf',
    correo VARCHAR(120) NOT NULL,
    ubicacion VARCHAR(120) NOT NULL,
    mapa_url VARCHAR(500) NOT NULL,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_perfil_usuario (usuario_id),
    CONSTRAINT fk_perfil_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 5. TABLA experiencias
-- ------------------------------------------------------------
-- Cada fila es un trabajo. perfil_id indica a que perfil pertenece.
-- ON DELETE CASCADE significa que, si se borra el perfil, también
-- se borran sus experiencias. Asi no quedan datos huerfanos.

CREATE TABLE experiencias (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    perfil_id INT UNSIGNED NOT NULL,
    puesto VARCHAR(120) NOT NULL,
    empresa VARCHAR(120) NOT NULL,
    periodo VARCHAR(80) NOT NULL,
    descripcion TEXT NOT NULL,
    logo VARCHAR(255) NOT NULL DEFAULT 'img/empresa-ejemplo.svg',
    orden INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_experiencias_perfil (perfil_id),
    CONSTRAINT fk_experiencias_perfil
        FOREIGN KEY (perfil_id)
        REFERENCES perfil (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 6. TABLA educacion
-- ------------------------------------------------------------
-- Cada fila es un estudio, curso o carrera terminada.

CREATE TABLE educacion (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    perfil_id INT UNSIGNED NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    institucion VARCHAR(150) NOT NULL,
    periodo VARCHAR(80) NOT NULL,
    descripcion TEXT NOT NULL,
    logo VARCHAR(255) NOT NULL DEFAULT 'img/instituto-ejemplo.svg',
    orden INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_educacion_perfil (perfil_id),
    CONSTRAINT fk_educacion_perfil
        FOREIGN KEY (perfil_id)
        REFERENCES perfil (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 7. TABLA skills
-- ------------------------------------------------------------
-- categoria solamente puede valer 'Hard' o 'Soft'.
-- porcentaje se guarda como numero entero entre 0 y 100.
-- El control del rango se hace en el formulario de la aplicacion.

CREATE TABLE skills (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    perfil_id INT UNSIGNED NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    porcentaje TINYINT UNSIGNED NOT NULL,
    categoria ENUM('Hard', 'Soft') NOT NULL,
    orden INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_skills_perfil (perfil_id),
    CONSTRAINT fk_skills_perfil
        FOREIGN KEY (perfil_id)
        REFERENCES perfil (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 8. TABLA idiomas
-- ------------------------------------------------------------
-- Se separa de skills porque un idioma tiene nombre, nivel y
-- porcentaje, y se muestra en un bloque distinto.

CREATE TABLE idiomas (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    perfil_id INT UNSIGNED NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    nivel VARCHAR(60) NOT NULL,
    porcentaje TINYINT UNSIGNED NOT NULL,
    orden INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_idiomas_perfil (perfil_id),
    CONSTRAINT fk_idiomas_perfil
        FOREIGN KEY (perfil_id)
        REFERENCES perfil (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 9. TABLA proyectos
-- ------------------------------------------------------------
-- enlace es la direccion del proyecto (por ejemplo GitHub o una demo).
-- imagen guarda una ruta relativa dentro de static.

CREATE TABLE proyectos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    perfil_id INT UNSIGNED NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    fecha DATE NOT NULL,
    descripcion TEXT NOT NULL,
    enlace VARCHAR(500) NOT NULL,
    imagen VARCHAR(255) NOT NULL DEFAULT 'img/proyecto-ejemplo.svg',
    orden INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_proyectos_perfil (perfil_id),
    CONSTRAINT fk_proyectos_perfil
        FOREIGN KEY (perfil_id)
        REFERENCES perfil (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 10. TABLA redes_sociales
-- ------------------------------------------------------------
-- icono guarda la clase de FontAwesome completa.
-- Ejemplo: 'fa-brands fa-github'.

CREATE TABLE redes_sociales (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    perfil_id INT UNSIGNED NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    enlace VARCHAR(500) NOT NULL,
    icono VARCHAR(100) NOT NULL,
    orden INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_redes_sociales_perfil (perfil_id),
    CONSTRAINT fk_redes_sociales_perfil
        FOREIGN KEY (perfil_id)
        REFERENCES perfil (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- 11. DATOS DE EJEMPLO
-- ============================================================
--
-- USUARIO DE EJEMPLO
--   nombre de usuario: admin
--   contraseña:        admin123
--
-- El texto de abajo no es la contraseña: es su hash.
-- Para cambiarla se debe generar otro hash con:
--   from werkzeug.security import generate_password_hash
--   generate_password_hash("nueva_contrasena")
--
-- IMPORTANTE: cambiar esta contraseña antes de publicar el sitio.
-- ============================================================

INSERT INTO usuarios (id, nombre_usuario, clave_hash)
VALUES (
    1,
    'admin',
    'scrypt:32768:8:1$uxzBmTtr8GMa7LV5$168c582410a7d31a4a0f81d164785568d1a975ede4c54347786b83a341bd3833cdab5399e820718538a17d5001e9de380801043b7032d7f4c8bae9712859a5ac'
);


-- Perfil principal del portfolio.
INSERT INTO perfil (
    id,
    usuario_id,
    nombre_completo,
    titulo_profesional,
    resumen,
    texto_banner,
    foto_perfil,
    imagen_banner,
    archivo_cv,
    correo,
    ubicacion,
    mapa_url
)
VALUES (
    1,
    1,
    'Thiago Pérez',
    'Desarrollador Full Stack Jr.',
    'Soy un desarrollador Full Stack Junior con muchas ganas de seguir aprendiendo. Disfruto transformar ideas en sitios web claros, ordenados y fáciles de usar. Trabajo con HTML, CSS, JavaScript, Python, Flask y MySQL, y me interesa especialmente entender bien cada paso del proceso: desde la base de datos hasta lo que ve la persona que visita el sitio.',
    'Construyo experiencias web simples, funcionales y pensadas para las personas.',
    'img/perfil-ejemplo.svg',
    'img/banner-ejemplo.svg',
    'cv/cv-ejemplo.pdf',
    'thiago.ejemplo@correo.com',
    'Buenos Aires, Argentina',
    'https://www.google.com/maps?q=Buenos+Aires,+Argentina&output=embed'
);


-- Experiencias de ejemplo.
-- El campo orden sirve para decidir en que posicion se muestra cada una.
INSERT INTO experiencias (
    id,
    perfil_id,
    puesto,
    empresa,
    periodo,
    descripcion,
    logo,
    orden
)
VALUES
(
    1,
    1,
    'Desarrollador Web Junior',
    'Estudio Digital',
    '2025 - Actualidad',
    'Desarrollo de páginas web para pequeños negocios. Trabajo con HTML, CSS, Bootstrap, JavaScript y Flask, y participo en la revisión de formularios y de la experiencia de usuario.',
    'img/empresa-estudio.svg',
    1
),
(
    2,
    1,
    'Practicante de Desarrollo',
    'TecnoLab',
    '2024 - 2025',
    'Colaboré en el mantenimiento de una aplicación interna. Corregí errores simples, ordené consultas SQL y documenté los cambios realizados para el resto del equipo.',
    'img/empresa-tecnolab.svg',
    2
),
(
    3,
    1,
    'Desarrollador Freelance',
    'Proyectos personales',
    '2023 - Actualidad',
    'Creación de landing pages y pequeños sistemas para conocidos. Me encargo del diseño, del front end, de la base de datos y de la puesta en marcha del proyecto.',
    'img/empresa-freelance.svg',
    3
);


-- Estudios de ejemplo.
INSERT INTO educacion (
    id,
    perfil_id,
    titulo,
    institucion,
    periodo,
    descripcion,
    logo,
    orden
)
VALUES
(
    1,
    1,
    'Tecnicatura en Programación',
    'Instituto Tecnológico del Sur',
    '2024 - 2026',
    'Formación en lógica de programación, bases de datos, desarrollo web y trabajo en equipo. Actualmente estoy desarrollando el proyecto final integrador.',
    'img/instituto-tecnologico.svg',
    1
),
(
    2,
    1,
    'Curso de Desarrollo Web Full Stack',
    'Academia Digital',
    '2025',
    'Curso práctico con HTML, CSS, JavaScript, Python, Flask y MySQL. El trabajo final fue un portfolio personal con modo de edición.',
    'img/academia-digital.svg',
    2
);


-- Habilidades duras y blandas.
-- La categoria permite separarlas en dos grupos en la pagina.
INSERT INTO skills (
    id,
    perfil_id,
    nombre,
    porcentaje,
    categoria,
    orden
)
VALUES
(1, 1, 'HTML5', 85, 'Hard', 1),
(2, 1, 'CSS3', 80, 'Hard', 2),
(3, 1, 'JavaScript', 65, 'Hard', 3),
(4, 1, 'Python', 75, 'Hard', 4),
(5, 1, 'Flask', 70, 'Hard', 5),
(6, 1, 'MySQL', 65, 'Hard', 6),
(7, 1, 'Trabajo en equipo', 85, 'Soft', 7),
(8, 1, 'Comunicación', 80, 'Soft', 8),
(9, 1, 'Resolución de problemas', 75, 'Soft', 9),
(10, 1, 'Organización', 80, 'Soft', 10);


-- Idiomas.
INSERT INTO idiomas (id, perfil_id, nombre, nivel, porcentaje, orden)
VALUES
(1, 1, 'Español', 'Nativo', 100, 1),
(2, 1, 'Inglés', 'Intermedio', 65, 2),
(3, 1, 'Portugués', 'Básico', 35, 3);


-- Proyectos.
-- El primero es este mismo portfolio, como pide la consigna.
INSERT INTO proyectos (
    id,
    perfil_id,
    nombre,
    fecha,
    descripcion,
    enlace,
    imagen,
    orden
)
VALUES
(
    1,
    1,
    'Portfolio Web Personal',
    '2026-03-01',
    'Sitio de una sola página construido con Flask, Jinja2 y MySQL. Incluye modo de edición con login, formularios protegidos con CSRF y diseño responsive.',
    'https://github.com/tu-usuario/portfolio',
    'img/proyecto-portfolio.svg',
    1
),
(
    2,
    1,
    'Gestor de Tareas',
    '2025-11-15',
    'Aplicación para crear, marcar como completadas y eliminar tareas. Practiqué el uso de formularios, validaciones y consultas de tipo CRUD.',
    'https://github.com/tu-usuario/gestor-tareas',
    'img/proyecto-tareas.svg',
    2
),
(
    3,
    1,
    'Tienda de Plantas',
    '2025-08-10',
    'Catálogo de plantas con buscador y carrito simple. El objetivo fue practicar el diseño responsive y el consumo de datos desde una base MySQL.',
    'https://github.com/tu-usuario/tienda-plantas',
    'img/proyecto-plantas.svg',
    3
),
(
    4,
    1,
    'API de Turnos',
    '2024-12-05',
    'Trabajo práctico de backend para reservar turnos. Incluye validación de datos, consultas SQL y una documentación básica de los endpoints.',
    'https://github.com/tu-usuario/api-turnos',
    'img/proyecto-turnos.svg',
    4
);


-- Redes sociales e iconos del encabezado.
-- Se guarda la clase completa de FontAwesome.
INSERT INTO redes_sociales (
    id,
    perfil_id,
    nombre,
    enlace,
    icono,
    orden
)
VALUES
(
    1,
    1,
    'GitHub',
    'https://github.com/tu-usuario',
    'fa-brands fa-github',
    1
),
(
    2,
    1,
    'LinkedIn',
    'https://www.linkedin.com/in/tu-usuario',
    'fa-brands fa-linkedin-in',
    2
),
(
    3,
    1,
    'Instagram',
    'https://www.instagram.com/tu-usuario',
    'fa-brands fa-instagram',
    3
),
(
    4,
    1,
    'Correo',
    'mailto:thiago.ejemplo@correo.com',
    'fa-solid fa-envelope',
    4
);


-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
