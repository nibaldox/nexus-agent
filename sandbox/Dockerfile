FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    nodejs \
    npm \
    curl \
    git \
    vim \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash -u 1000 coderunner

# Setup workspace
WORKDIR /workspace
RUN chown coderunner:coderunner /workspace

# Switch to non-root user
USER coderunner

# Configure npm to use user directory for global installs
RUN mkdir -p /home/coderunner/.npm-global && \
    npm config set prefix '/home/coderunner/.npm-global'

# Add npm global bin to PATH (before Python user bin)
ENV PATH="/home/coderunner/.npm-global/bin:/home/coderunner/.local/bin:${PATH}"

# Pre-install common Python libraries
RUN pip3 install --user --no-cache-dir \
    numpy \
    pandas \
    requests \
    matplotlib \
    seaborn \
    scipy

# Default command
CMD ["/bin/bash"]
