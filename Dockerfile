FROM mysql:latest # Or your preferred MySQL version

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy application files
COPY app.py schema.sql start.sh ./

# Set up MySQL (wait/configuration) - Assuming docker-entrypoint-initdb.d is supported
COPY schema.sql /docker-entrypoint-initdb.d/schema.sql 

# Start the container
CMD ["/bin/bash", "start.sh"]
