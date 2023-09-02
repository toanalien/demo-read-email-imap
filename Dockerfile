# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install FastAPI, Uvicorn, and Gunicorn
RUN pip install fastapi uvicorn gunicorn

# Make port 80 available for the app to run on
EXPOSE 80

# Define the environment variable
ENV NAME World

# Run gunicorn server on startup
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:80"]
