# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install necessary tools
RUN apt-get update && apt-get install -y wget tar

# Download and set up the deposit tool
RUN wget https://github.com/ethereum/staking-deposit-cli/releases/download/v2.7.0/staking_deposit-cli-fdab65d-linux-amd64.tar.gz \
    && tar -xzf staking_deposit-cli-fdab65d-linux-amd64.tar.gz \
    && mv staking_deposit-cli-fdab65d-linux-amd64/deposit deposit \
    && rm staking_deposit-cli-fdab65d-linux-amd64.tar.gz

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Create a volume for the config file in the project root
VOLUME /app

# Set the path to the deposit tool in the environment
ENV DEPOSIT_CLI_PATH=/app/deposit

# Run swarm when the container launches, passing command-line arguments
ENTRYPOINT ["python", "-m", "swarm"]
CMD []
