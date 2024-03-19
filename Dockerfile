FROM mysql

RUN microdnf update && microdnf install -y python3-devel python3 python3-pip glibc-devel glibc-headers elfutils-libelf-devel gcc gcc-c++ make git

WORKDIR /app
COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy application files
COPY app.py schema.sql start.sh ./

# Set up MySQL (wait/configuration) - Assuming docker-entrypoint-initdb.d is supported
COPY schema.sql /docker-entrypoint-initdb.d/schema.sql 

# Expose Flask application port
EXPOSE 5000

# Start the container
CMD ["/bin/bash", "-c", "/app/start.sh"]
