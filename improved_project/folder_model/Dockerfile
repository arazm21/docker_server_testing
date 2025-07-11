
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# COPY .env .  


# Copy custom OpenSSL config (for unsafe legacy renegotiation)
COPY openssl.cnf /etc/ssl/openssl.cnf

# Use the custom OpenSSL config
ENV OPENSSL_CONF=/etc/ssl/openssl.cnf

# Install CA certificates
RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates

# Set Conda to skip SSL verification (for broken cert chains / firewalls)
RUN conda config --set ssl_verify False

# Copy model files (including conda.yaml)
COPY model ./model

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*
# Create the Conda environment
RUN conda env create -f model/conda.yaml

# Activate the environment
ENV PATH=/opt/conda/envs/mlflow-env/bin:$PATH
ENV CONDA_DEFAULT_ENV=mlflow-env

# Expose the default MLflow port
EXPOSE 5000

# Serve the model
# ENTRYPOINT ["mlflow", "models", "serve", "-m", "/app/model", "-h", "0.0.0.0", "-p", "5000"]
# ENTRYPOINT ["mlflow", "models", "serve", "-m", "/app/model", "-h", "0.0.0.0", "-p", "5000", "--env-manager=local"]
# ENTRYPOINT ["mlflow"]
# CMD ["models", "serve", "-m", "/app/model", "-h", "0.0.0.0", "-p", "5000", "--env-manager=local"]
CMD ["mlflow", "models", "serve", "-m", "/app/model", "-h", "0.0.0.0", "-p", "5000", "--env-manager=local"]

# works!!!


