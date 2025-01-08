#!/bin/bash

cd /app/downloads

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

if [ "$ARCH" = "x86_64" ]; then
    # Download x86_64 version
    wget https://github.com/ethereum/staking-deposit-cli/releases/download/v2.8.0/staking_deposit-cli-948d3fc-linux-amd64.tar.gz
    tar xvf staking_deposit-cli-948d3fc-linux-amd64.tar.gz
    cp staking_deposit-cli-948d3fc-linux-amd64/deposit /usr/local/bin/
elif [ "$ARCH" = "aarch64" ]; then
    # Download ARM version
    wget https://github.com/ethereum/staking-deposit-cli/releases/download/v2.8.0/staking_deposit-cli-948d3fc-linux-arm64.tar.gz
    tar xvf staking_deposit-cli-948d3fc-linux-arm64.tar.gz
    cp staking_deposit-cli-948d3fc-linux-arm64/deposit /usr/local/bin/
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

chmod +x /usr/local/bin/deposit 