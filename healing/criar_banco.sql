-- Script de criação do banco de dados HEALING
-- Execute como root no MySQL

CREATE DATABASE IF NOT EXISTS bd_healing
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'usuario_healing'@'localhost' IDENTIFIED BY 'Healing@2024';
GRANT ALL PRIVILEGES ON bd_healing.* TO 'usuario_healing'@'localhost';
FLUSH PRIVILEGES;

USE bd_healing;
