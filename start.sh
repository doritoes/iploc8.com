#!/bin/bash

# Wait for MySQL to initialize
until mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" &> /dev/null; do
  echo >&2 "MySQL is unavailable - sleeping"
  sleep 2
done

echo >&2 "MySQL is up - executing command"

# Change root password if needed
mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" <<-EOSQL
ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';

# Load initial schema (optional, remove if not needed)
mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" < /docker-entrypoint-initdb.d/schema.sql 
EOSQL

# Start the Flask application
python app.py
