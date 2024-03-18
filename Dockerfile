FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Add MariaDB repository (or official MySQL if preferred)
RUN apt-key adv --fetch-keys 'https://mariadb.org/mariadb_release_signing_key.asc' && \
    add-apt-repository 'deb [arch=amd64] http://nyc2.mirrors.digitalocean.com/mariadb/repo/10.6/debian bookworm main'

# Install MySQL server (MariaDB in this case)
RUN apt-get update && apt-get install -y mariadb-server 

# Create a working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy your Flask application 
COPY app.py ./

# Set up MySQL (wait/configuration)
RUN mkdir -p /docker-entrypoint-initdb.d
COPY schema.sql /docker-entrypoint-initdb.d/schema.sql 
COPY dockerful /dockerful

# Expose Flask port 
EXPOSE 5000

# Start the Flask app as the default command
CMD ["dockerful"]
