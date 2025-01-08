FROM ubuntu:22.04

# Set working directory
WORKDIR /app

EXPOSE 8000

# Install required packages including libc6
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-pip \
    wget \
    sudo \
    ssh \
    libc6 \
    && rm -rf /var/lib/apt/lists/*

# Print architecture information for debugging
RUN uname -a && \
    dpkg --print-architecture

# Setup SSH directory
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

# Copy SSH config files from project directory
COPY /.ssh /root/.ssh
RUN chmod 644 /root/.ssh

# Create a directory for downloads
RUN mkdir -p /app/downloads

# Download and install staking deposit CLI
COPY download-deposit.sh /app/
RUN chmod +x /app/download-deposit.sh && \
    /app/download-deposit.sh && \
    # Verify deposit CLI installation
    ls -la /usr/local/bin/deposit && \
    # Create symlink to ensure it's found as deposit-cli
    ln -s /usr/local/bin/deposit /usr/local/bin/deposit-cli && \
    # Add to PATH just in case
    echo 'export PATH="/usr/local/bin:$PATH"' >> /etc/bash.bashrc && \
    # Verify both executables
    which deposit && \
    which deposit-cli

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

# Final verification of deposit CLI
RUN /usr/local/bin/deposit --help || true