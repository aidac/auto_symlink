# Use an official Python runtime as a parent image
FROM python:3.8

# Argument for user ID and group ID
ARG PUID=1000
ARG PGID=1000

# Install watchdog
RUN pip install watchdog

# Create a group and user with specified user ID and group ID
RUN groupadd -g $PGID appuser && \
    useradd -m -u $PUID -g appuser appuser

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the Flask app, script, and static files into the container
COPY app.py /usr/src/app/

# Change the ownership of the work directory to the new user
RUN chown -R appuser:appuser /usr/src/app

# Switch to the new user
USER appuser

# Run the app
CMD ["python", "app.py"]