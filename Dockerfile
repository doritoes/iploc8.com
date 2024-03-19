FROM mysql

RUN microdnf update && microdnf install -y python3-devel gcc make gnupg2 python3 python3-pip git

WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy application files
COPY app.py schema.sql start.sh ./

# Set up MySQL (wait/configuration) - Assuming docker-entrypoint-initdb.d is supported
COPY schema.sql /docker-entrypoint-initdb.d/schema.sql 

# Start the container
CMD ["/bin/bash", "start.sh"]
