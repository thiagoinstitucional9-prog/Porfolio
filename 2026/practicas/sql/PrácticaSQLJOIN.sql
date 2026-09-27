DROP DATABASE Ventas;
CREATE DATABASE Ventas;
USE Ventas;


CREATE TABLE pais (
    id_pais INT PRIMARY KEY,
    nombre_pais VARCHAR(100) NOT NULL,
    region VARCHAR(100)
);

CREATE TABLE cliente (
    id_cliente INT PRIMARY KEY,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    ciudad VARCHAR(100),
    id_pais INT,
    FOREIGN KEY (id_pais) REFERENCES pais(id_pais)
);

CREATE TABLE producto (
    id_producto INT PRIMARY KEY,
    nombre_producto VARCHAR(150) NOT NULL,
    categoria VARCHAR(100),
    subcategoria VARCHAR(100),
    precio_lista DECIMAL(12,2)
);

CREATE TABLE costo (
    id_producto INT PRIMARY KEY,
    costo_unitario DECIMAL(12,2),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

CREATE TABLE canal (
    id_canal INT PRIMARY KEY,
    descripcion VARCHAR(100),
    clase VARCHAR(50)
);

CREATE TABLE promocion (
    id_promocion INT PRIMARY KEY,
    nombre_promocion VARCHAR(150)
);

CREATE TABLE tiempo (
    id_tiempo INT PRIMARY KEY,
    fecha DATE NOT NULL,
    dia_semana VARCHAR(20),
    anio INT,
    trimestre INT,
    mes INT
);

CREATE TABLE venta (
    id_venta INT PRIMARY KEY,
    id_cliente INT,
    id_producto INT,
    id_canal INT,
    id_promocion INT NULL,
    id_tiempo INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(12,2),
    monto DECIMAL(12,2),

    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
    FOREIGN KEY (id_canal) REFERENCES canal(id_canal),
    FOREIGN KEY (id_promocion) REFERENCES promocion(id_promocion),
    FOREIGN KEY (id_tiempo) REFERENCES tiempo(id_tiempo)
);

-- nivel 1 

--1
select venta.cantidad, venta.monto, producto.nombre_producto
from venta
INNER JOIN producto 
ON venta.id_producto = producto.id_producto
--2
select cliente.apellido, cliente.ciudad, pais.nombre_pais
from cliente
INNER JOIN pais
ON cliente.id_pais = pais.id_pais
--3
select venta.id_venta, venta.monto, canal.descripcion
from venta
INNER JOIN canal
ON venta.id_canal = canal.id_canal
--4
select producto.nombre_producto, costo.costo_unitario
from producto
INNER JOIN costo
ON producto.id_producto = costo.id_producto

-- 5 revisar
select cliente.nombre, cliente.apellido, tiempo.fecha
from cliente
INNER JOIN venta
ON cliente.id_cliente = tiempo.id_tiempo
inner join tiempo 
on venta.id_tiempo = tiempo.id_tiempo

--6
select promocion.nombre_promocion, venta.monto
from promocion
INNER JOIN venta
ON promocion.id_promocion = venta.id_promocion

--7
select cliente.nombre, cliente.apellido, venta.monto
from cliente
INNER JOIN venta
ON cliente.id_cliente = venta.id_cliente

SELECT producto.nombre_producto, producto.precio_lista, venta.monto
FROM producto
INNER JOIN venta
    ON producto.id_producto = venta.id_producto;

SELECT DISTINCT producto.categoria, canal.clase
FROM producto
INNER JOIN venta
    ON producto.id_producto = venta.id_producto
INNER JOIN canal
    ON venta.id_canal = canal.id_canal;

--8
select tiempo.fecha, tiempo.dia_semana, venta.monto
from tiempo
INNER JOIN venta
ON tiempo.id_tiempo = venta.id_tiempo


--9
select producto.categoria, canal.clase
from producto
INNER JOIN canal
ON producto.id_producto = canal.id_canal

--10
select cliente.nombre, pais.nombre_pais, pais.region
from cliente
INNER JOIN pais
ON cliente.id_pais = pais.id_pais

--11
select venta.precio_unitario, canal.descripcion
from venta
INNER JOIN canal
ON venta.id_canal = canal.id_canal
--12
select producto.nombre_producto, 

--level 2

--13
select cliente.nombre, 

select sales.amount_sold, sales.quantity_sold, product.product_name
from sales
INNER JOIN product
ON sales.product_id = product.product_id

select  customer.first_name, product.product_name, sales.quanty_sold
from customer
INNER JOIN sales
ON customer.customer_id = sales.customer_id
INNER JOIN product
ON sales.product_id = product.product_id

select customer.first_name, sales.amount_sold
from customer
left JOIN  sales
ON customer.customer_id = sales.customer_id

