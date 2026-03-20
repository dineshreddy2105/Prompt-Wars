# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Set the PYTHONPATH so the app can find modules in the backend directory
ENV PYTHONPATH="${PYTHONPATH}:${APP_HOME}:${APP_HOME}/backend"

# Install production dependencies.
RUN pip install --no-cache-dir -r backend/requirements.txt

# Run the web service on container startup.
# We use sh -c to allow environment variable expansion of $PORT.
CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
