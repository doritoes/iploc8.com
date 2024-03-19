#!/bin/bash
# Start MySQL in the background
/usr/local/bin/docker-entrypoint.sh mysqld &
# Wait for MySQL to initialize
until mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" &> /dev/null; do
  echo >&2 "MySQL is unavailable - sleeping"
  sleep 2
done
echo >&2 "MySQL is up - starting app"
python3 app.py
