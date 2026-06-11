FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt . 

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application file
COPY index.py . 

# Expose the port (informative documentation)
EXPOSE 8000

# Command to run the application
CMD ["python", "index.py"]


