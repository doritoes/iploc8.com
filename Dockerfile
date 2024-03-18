FROM mysql:debian 

RUN apt-get update && apt-get install -y gnupg2 && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B7B3B788A8D3785C
    
RUN apt-get update && apt-get install -y python3 python3-pip git

WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy application files
COPY app.py schema.sql start.sh ./

# Set up MySQL (wait/configuration) - Assuming docker-entrypoint-initdb.d is supported
COPY schema.sql /docker-entrypoint-initdb.d/schema.sql 

# Start the container
CMD ["/bin/bash", "start.sh"]
