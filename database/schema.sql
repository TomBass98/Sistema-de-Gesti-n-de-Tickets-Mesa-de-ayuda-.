CREATE DATABASE IF NOT EXISTS mesa_ayuda;

USE mesa_ayuda;

CREATE TABLE tbl_clientes(
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cli VARCHAR(100) NOT NULL,
    documento_cli VARCHAR(20) NOT NULL UNIQUE,
    telefono_cli VARCHAR(20),
    correo_cli VARCHAR(100)
);

CREATE TABLE tbl_tecnicos(
    id_tecnico INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tec VARCHAR(100) NOT NULL,
    especialidad VARCHAR(80),
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE tbl_equipos(
    id_equipo INT AUTO_INCREMENT PRIMARY KEY,
    tipo_equipo VARCHAR(50) NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    serial_number VARCHAR(80) UNIQUE,

    id_cliente INT NOT NULL,

    FOREIGN KEY(id_cliente) REFERENCES tbl_clientes(id_cliente)
);

CREATE TABLE tbl_tickets_servicio(
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    fecha_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP,
    falla_reportada VARCHAR(255) NOT NULL,
    estado VARCHAR(30) DEFAULT 'Abierto',
    costo_total DECIMAL(10,2) DEFAULT 0.00,

    id_equipo INT NOT NULL,
    id_tecnico INT NOT NULL,

    FOREIGN KEY(id_equipo) REFERENCES tbl_equipos(id_equipo),
    FOREIGN KEY(id_tecnico) REFERENCES tbl_tecnicos(id_tecnico)
);



