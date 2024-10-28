DROP DATABASE IF EXISTS crudvtdb;

CREATE DATABASE crudvtdb
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE crudvtdb;

CREATE TABLE owner (
    o_id INT PRIMARY KEY AUTO_INCREMENT,
    o_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    o_birth DATE,
    o_name VARCHAR(127) NOT NULL,
    o_email VARCHAR(255) NOT NULL,
    o_pass VARCHAR(63) NOT NULL,
    o_status ENUM('on', 'off', 'del') DEFAULT 'on'
);

CREATE TABLE thing (
    t_id INT PRIMARY KEY AUTO_INCREMENT,
    t_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    t_owner INT NOT NULL,
    t_photo VARCHAR(255),
    t_name VARCHAR(127) NOT NULL,
    t_description TEXT,
    t_location VARCHAR(255),
    t_status ENUM('on', 'off', 'del') DEFAULT 'on',
    FOREIGN KEY (t_owner) REFERENCES owner (o_id)
);


INSERT INTO owner (
    o_birth,
    o_name,
    o_email,
    o_pass
) VALUES (
    '2000-10-28',
    'Joca da Silva',
    'jocasilva@email.com',
    SHA1('Senha123')
);

INSERT INTO thing (
    t_owner,
    t_photo,
    t_name,
    t_description,
    t_location
) VALUES (
    '1',
    'https://picsum.photos/200',
    'peteca',
    'Cheia de penas velhas',
    'Caixa de sapato sob a cama'
);