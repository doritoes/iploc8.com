#!/bin/bash
# Start MySQL in the background
/usr/local/bin/docker-entrypoint.sh mysqld &
# Wait for MySQL to initialize
until mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" &> /dev/null; do
  echo >&2 "MySQL is unavailable - sleeping"
  sleep 2
done
echo >&2 "MySQL is up - starting data import"
mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "
    USE mydatabase;
    LOAD DATA LOCAL INFILE '/app/countries.csv'
        INTO TABLE countries
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\n';
        (Code, Name);
"
# git clone https://github.com/sapics/ip-location-db

echo >&2 "download complete - starting app"
python3 app.py
