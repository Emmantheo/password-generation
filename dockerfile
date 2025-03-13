# Start from an official Python image
FROM python:3.9-slim

# Set a working directory inside the container
WORKDIR /app

# Copy requirements.txt if you have one
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 5000 to the host
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]





