#!/bin/bash
# Start MySQL
/usr/local/bin/docker-entrypoint.sh mysqld
# Wait for MySQL to initialize
until mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" &> /dev/null; do
  echo >&2 "MySQL is unavailable - sleeping"
  sleep 2
done

echo >&2 "MySQL is up - executing command"
nohup /usr/bin/python3 -m app flask --host=0.0.0.0 &
