# Use the specified image as the base
FROM python:3.10-slim-bullseye as release

# Set environment variables for Poetry
ENV POETRY_VERSION=1.6.1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry using pip and clear cache
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false

# Set the working directory
WORKDIR /app

# Copy the poetry lock file and pyproject.toml file to install dependencies
COPY pyproject.toml poetry.lock /app/

# Install the dependencies and clear cache
RUN poetry install --no-root --no-interaction --no-cache --without dev  && \
    pip install --no-cache-dir numpy==1.24.3 && \
    rm -rf ~/.cache/pypoetry/cache/ && \
    rm -rf ~/.cache/pypoetry/artifacts/

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt_tab'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
# Copy the rest of the code
COPY . /app

# Give execution permission to your shell script
RUN chmod +x /app/deploy/entrypoint.sh

# Run your shell script
CMD ["/app/deploy/entrypoint.sh"]
