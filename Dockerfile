FROM python:3.14-slim

WORKDIR /app

# Copy your files into the container
COPY . .

# Install dependencies if you have a requirements.txt file
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Run your Python script
CMD ["python", "main.py"]