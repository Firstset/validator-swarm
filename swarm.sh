#!/bin/bash

cp -r ~/.ssh .

# Handle docker-rebuild command
if [ "$1" = "docker-rebuild" ]; then
    echo "Rebuilding Docker image..."
    docker build -t swarm-python . --no-cache
    exit 0
fi

# Handle shell command
if [ "$1" = "shell" ]; then
    echo "Starting shell in container..."
    docker run -it \
        -v "$(pwd)/swarm:/app/swarm" \
        -v "$(pwd)/abis:/app/abis" \
        -v "$(pwd)/addresses:/app/addresses" \
        -v "$(pwd)/proofs:/app/proofs" \
        -v "$(pwd)/downloads:/app/downloads" \
        swarm-python /bin/bash
    exit 0
fi

# Ensure directories exist
mkdir -p swarm abis addresses proofs downloads

# Build the Docker image if it doesn't exist
docker build -t swarm-python . 2>/dev/null

# Run the container with all folders mounted
docker run -it \
    -p 8000:8000 \
    -v "$(pwd)/swarm:/app/swarm" \
    -v "$(pwd)/abis:/app/abis" \
    -v "$(pwd)/addresses:/app/addresses" \
    -v "$(pwd)/proofs:/app/proofs" \
    -v "$(pwd)/downloads:/app/downloads" \
    swarm-python python3 -m swarm "$@" 