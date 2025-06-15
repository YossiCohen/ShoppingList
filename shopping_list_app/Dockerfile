# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP wsgi.py

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed by some Python packages
# (e.g., for database drivers or other libraries).
# For a simple SQLite app, this might not be strictly necessary,
# but it's good practice for more complex applications.
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create the instance folder (Flask will create app.db here if it doesn't exist)
# The application code (wsgi.py) already creates the instance folder if it doesn't exist.
# So, this explicit RUN mkdir instance might not be strictly necessary if the app ensures it.
# However, it can be good for clarity or if initial db setup is done during build.
# For now, we'll keep it commented as the app handles it.
# RUN mkdir instance

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
# Use Gunicorn for a production-ready WSGI server
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
