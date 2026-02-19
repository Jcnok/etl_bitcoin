# Stage 1: Build the virtual environment with Poetry
FROM python:3.12-slim AS builder

# Set environment variables to prevent interactive prompts and manage venv
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only dependency-related files to leverage Docker cache
COPY poetry.lock pyproject.toml ./

# Install dependencies, excluding development ones
RUN poetry install --only main --no-root

# Stage 2: Create the final, lean production image
FROM python:3.12-slim

# Set environment variables for the final image
ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# Create a non-root user and group for security
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Copy the application source code
COPY src/ ./src/

# Change ownership of the application files to the non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Set the entrypoint for the container
ENTRYPOINT ["python", "-m", "src.main"]

# Set a default command to show help
CMD ["--help"]
