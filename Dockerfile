# ------------------------------------------------------------------------------
# Base Image: Use a stable Python image compatible with Python 3.11
# ------------------------------------------------------------------------------
FROM python:3.11-slim

# ------------------------------------------------------------------------------
# Set Working Directory
# ------------------------------------------------------------------------------
WORKDIR /app

# ------------------------------------------------------------------------------
# Install OS-level dependencies
# (Requests, SSL, etc. Run minimal apt updates to keep image small)
# ------------------------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------
# Copy project files (source code + config)
# ------------------------------------------------------------------------------
COPY src/ ./src/
COPY environment.yml .
COPY README.md .
COPY ARCHITECTURE.md .
COPY EXPLANATION.md .
COPY DEMO.md .
COPY .env .

# ------------------------------------------------------------------------------
# Install pip and project dependencies
# ------------------------------------------------------------------------------
RUN pip install --upgrade pip && \
    pip install google-generativeai python-dotenv requests typing_extensions

# ------------------------------------------------------------------------------
# Default Command (for local testing)
# This runs your local CLI agent; ADK Playground provides its own entrypoint.
# ------------------------------------------------------------------------------
CMD ["python", "-m", "src.main"]
