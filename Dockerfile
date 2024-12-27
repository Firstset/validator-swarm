FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file and config
COPY requirements.txt .
COPY config.toml .

# Copy all required directories and their contents
COPY swarm/ /app/swarm/
COPY abis/ /app/abis/
COPY addresses/ /app/addresses/
COPY proofs/ /app/proofs/

RUN pip install -r requirements.txt

WORKDIR /app