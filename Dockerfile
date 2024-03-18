FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git mysql-server

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
