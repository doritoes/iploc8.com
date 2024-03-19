#!/bin/bash
# Start MySQL in the background
/usr/local/bin/docker-entrypoint.sh mysqld --local-infile=1 &
# Wait for MySQL to initialize
until mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" &> /dev/null; do
  echo >&2 "MySQL is unavailable - sleeping"
  sleep 2
done
echo >&2 "MySQL is up - starting data import"
echo >&2 "importing countries.csv"
mysql --local-infile=1 -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "
    USE mydatabase;
    LOAD DATA LOCAL INFILE '/app/countries.csv'
        INTO TABLE countries
        FIELDS TERMINATED BY ','
        ENCLOSED BY '\"'
        LINES TERMINATED BY '\n'
        (Name, Code);
"
echo >&2 "Downloading ip-location-db files..."
curl -s -o iptoasn-asn-ipv4-num.csv  https://cdn.jsdelivr.net/npm/@ip-location-db/iptoasn-asn/iptoasn-asn-ipv4-num.csv
curl -s -o geo-whois-asn-country-ipv4-num.csv  https://cdn.jsdelivr.net/npm/@ip-location-db/geo-whois-asn-country/geo-whois-asn-country-ipv4-num.csv

echo >&2 "download complete - starting app"
python3 app.py
