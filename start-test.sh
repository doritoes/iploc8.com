#!/bin/bash
# Start MySQL
echo >&2 "About to start mysqld"
/usr/local/bin/docker-entrypoint.sh mysqld
echo >&2 "Finished starting mysqld"
# Wait for MySQL to initialize
until mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" &> /dev/null; do
  echo >&2 "MySQL is unavailable - sleeping"
  sleep 2
done
echo >&2 "MySQL is up - executing command"
python3 app.py &
