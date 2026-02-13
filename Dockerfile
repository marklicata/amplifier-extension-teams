FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application
COPY src/ ./src/
COPY run.py .

# Expose port
EXPOSE 3978

# Run the bot
CMD ["python", "run.py"]
