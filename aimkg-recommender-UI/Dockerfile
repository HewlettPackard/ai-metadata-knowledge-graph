# Use an official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything except the utils folder (excluded via .dockerignore)
COPY . /app/

# Expose the port the app runs on
EXPOSE 9089

# Set environment variables for the app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Command to run the application
CMD ["python", "app.py"]