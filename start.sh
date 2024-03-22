#!/bin/bash
# Start MySQL in the background
/usr/local/bin/docker-entrypoint.sh mysqld --local-infile=1 &
# Wait for MySQL to initialize
until mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" &> /dev/null; do
  echo >&2 "MySQL is unavailable - sleeping"
  sleep 2
done
echo >&2 "MySQL is up - starting data import"
# Import local files
echo >&2 "importing countries.csv"
mysql --local-infile=1 -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "
    USE mydatabase;
    LOAD DATA LOCAL INFILE '/app/countries.csv'
        INTO TABLE countries
        FIELDS TERMINATED BY ','
        ENCLOSED BY '\"'
        LINES TERMINATED BY '\n'
        (Name, Code);
" && rm /app/countries.csv
mysql --local-infile=1 -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "
    USE mydatabase;
    LOAD DATA LOCAL INFILE '/app/sanctions.csv'
        INTO TABLE sanctions
        FIELDS TERMINATED BY ','
        LINES TERMINATED BY '\n'
        IGNORE 1 LINES;
" && rm /app/sanctions.csv
# Import external files
echo >&2 "Downloading ip-location-db files..."
curl -v -s -o iptoasn-asn-ipv4-num.csv  https://cdn.jsdelivr.net/npm/@ip-location-db/iptoasn-asn/iptoasn-asn-ipv4-num.csv >&2
curl -v -s -o geo-whois-asn-country-ipv4-num.csv  https://cdn.jsdelivr.net/npm/@ip-location-db/geo-whois-asn-country/geo-whois-asn-country-ipv4-num.csv >&2
curl -v -s -o asn-ipv4-num.csv https://cdn.jsdelivr.net/npm/@ip-location-db/asn/asn-ipv4-num.csv >&2
curl -v -s -L -o dbip-city-ipv4-num.csv.gz https://unpkg.com/@ip-location-db/dbip-city/dbip-city-ipv4-num.csv.gz >&2
echo >&2 "importing iptoasn-asn-ipv4-num.csv"
mysql --local-infile=1 -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "
    USE mydatabase;
    LOAD DATA LOCAL INFILE '/app/iptoasn-asn-ipv4-num.csv'
    INTO TABLE asn
    FIELDS TERMINATED BY ',' 
    LINES TERMINATED BY '\n'
    (start, end, asn, description); 
" && rm /app/iptoasn-asn-ipv4-num.csv
echo >&2 "importing geo-whois-asn-country-ipv4-num.csv"
mysql --local-infile=1 -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "
    USE mydatabase;
    LOAD DATA LOCAL INFILE '/app/geo-whois-asn-country-ipv4-num.csv'
    INTO TABLE geo
    FIELDS TERMINATED BY ',' 
    LINES TERMINATED BY '\n'
    (start, end, country); 
" && rm /app/geo-whois-asn-country-ipv4-num.csv

echo >&2 "importing asn-ipv4-num.csv"
mysql --local-infile=1 -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "
    USE mydatabase;
    LOAD DATA LOCAL INFILE '/app/asn-ipv4-num.csv'
    INTO TABLE isp
    FIELDS TERMINATED BY ','
    ENCLOSED BY '\"'
    LINES TERMINATED BY '\n'
    (start, end, asn, description); 
" && rm /app/asn-ipv4-num.csv

echo >&2 "unpacking and importing dbip-city-ipv4-num.csv.gz"
gunzip /app/dbip-city-ipv4-num.csv.gz && mysql --local-infile=1 -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "
    USE mydatabase;
    LOAD DATA LOCAL INFILE '/app/dbip-city-ipv4-num.csv'
    INTO TABLE city
    FIELDS TERMINATED BY ',' 
    LINES TERMINATED BY '\n'
    (start, end, country_code, state1, state2, city, postcode, latitude, longitude, timezone);
" && rm /app/dbip-city-ipv4-num.csv
# Start the app
echo >&2 "download complete - starting app"
python3 app.py
