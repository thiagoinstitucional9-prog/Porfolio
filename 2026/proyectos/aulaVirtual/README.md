# Aula Virtual

Aplicación web desarrollada con Python, Flask, SQLAlchemy y MySQL para organizar cursos, materiales y evaluaciones.

## Funcionalidades

- Registro, inicio y cierre de sesión con contraseñas hasheadas.
- Roles de estudiante, profesor y administrador.
- Alta, edición y eliminación de cursos para profesores/administradores.
- Inscripción de estudiantes a cursos y protección del contenido para inscriptos.
- Publicación de enlaces o archivos como material didáctico.
- Creación de evaluaciones, entregas de estudiantes y calificación manual de 0 a 10.

## Base de datos

`Usuario` se relaciona con `Curso` como profesor y con `Inscripcion` como estudiante. Cada `Curso` contiene `Contenido` y `Evaluacion`; cada evaluación tiene `Pregunta` y `EntregaEvaluacion`.

## Puesta en marcha

1. Crear la base de datos MySQL: `CREATE DATABASE aula_virtual CHARACTER SET utf8mb4;`.
2. Crear y activar un entorno virtual.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Copiar `.env.example` a `.env` y completar las credenciales locales de MySQL.
5. Ejecutar `python app.py` y abrir `http://127.0.0.1:5000`.

Los registros nuevos son estudiantes. Para probar la gestión docente, cambiá el campo `rol` de un usuario a `profesor` desde MySQL.

## Pruebas recomendadas

1. Registrar un estudiante y un profesor.
2. Crear un curso con el profesor, publicar un contenido y una evaluación.
3. Inscribir al estudiante, comprobar que puede ver el curso, entregar la evaluación y luego calificarla con el profesor.
