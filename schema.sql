CREATE DATABASE IF NOT EXISTS mydatabase;
USE mydatabase;

CREATE TABLE IF NOT EXISTS countries (
  Code CHAR(2) PRIMARY KEY,
  Name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS asn (
  id INT AUTO_INCREMENT PRIMARY KEY,
  start BIGINT NOT NULL,
  end BIGINT NOT NULL,
  asn BIGINT NOT NULL,
  description VARCHAR(255),
  INDEX (start),
  INDEX (end)
);

CREATE TABLE IF NOT EXISTS geo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start BIGINT NOT NULL,
    end BIGINT NOT NULL,
    country CHAR(2),
    INDEX (start),
    INDEX (end)
);

CREATE TABLE IF NOT EXISTS sanctions (
    Country CHAR(2) PRIMARY KEY,
    Sanction VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS city (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start BIGINT NOT NULL,
    end BIGINT NOT NULL,
    country_code CHAR(2),
    state1 VARCHAR(255),
    state2 VARCHAR(255), 
    city VARCHAR(255),
    postcode VARCHAR(128),
    latitude VARCHAR(10),
    longitude VARCHAR(10), 
    timezone VARCHAR(32),
    INDEX (start),
    INDEX (end)
);

CREATE TABLE IF NOT EXISTS api_keys (
    guuid VARCHAR(48) PRIMARY KEY,
    valid BOOLEAN DEFAULT TRUE
);

INSERT INTO api_keys (guuid, valid) 
VALUES ('e95b186d-3677-4466-9cb2-20a549ab1d85', TRUE); 
